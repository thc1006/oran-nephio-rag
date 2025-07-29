"""
Asynchronous O-RAN × Nephio RAG System Implementation
Based on 2024 asyncio and aiohttp best practices research
"""
import asyncio
import aiohttp
import time
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from contextlib import asynccontextmanager
import json

# AsyncIO imports
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from asyncio import Semaphore, gather, create_task
import uvloop  # High-performance event loop

# LangChain async components
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_anthropic import ChatAnthropic
from langchain.schema import Document

try:
    from .config import Config, DocumentSource
    from .document_loader import DocumentContentCleaner
except ImportError:
    from config import Config, DocumentSource
    from document_loader import DocumentContentCleaner

logger = logging.getLogger(__name__)


class AsyncDocumentLoader:
    """
    High-performance async document loader
    Based on 2024 aiohttp best practices
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.content_cleaner = DocumentContentCleaner(self.config)
        self.session: Optional[ClientSession] = None
        
        # Performance optimizations based on research
        self.connector = TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=10,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.timeout = ClientTimeout(
            total=self.config.REQUEST_TIMEOUT,
            connect=10,
            sock_read=30
        )
        
        # Concurrency control
        self.semaphore = Semaphore(self.config.MAX_CONCURRENT_REQUESTS or 5)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers={
                'User-Agent': 'O-RAN-Nephio-RAG/1.0 AsyncClient',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self.session:
            await self.session.close()
        await self.connector.close()

    async def load_document_async(self, source: DocumentSource) -> Optional[Document]:
        """
        Load single document asynchronously with retry logic
        """
        async with self.semaphore:  # Rate limiting
            for attempt in range(self.config.MAX_RETRIES):
                try:
                    logger.debug(f"Loading document from {source.url} (attempt {attempt + 1})")
                    
                    async with self.session.get(
                        source.url,
                        ssl=self.config.VERIFY_SSL,
                        allow_redirects=True,
                        max_redirects=3
                    ) as response:
                        
                        if response.status == 200:
                            content = await response.text()
                            
                            # Clean and process content
                            cleaned_content = self.content_cleaner.clean_html(content, source.url)
                            
                            if len(cleaned_content) >= self.config.MIN_CONTENT_LENGTH:
                                return Document(
                                    page_content=cleaned_content,
                                    metadata={
                                        "source": source.url,
                                        "type": source.source_type,
                                        "description": source.description,
                                        "priority": source.priority,
                                        "loaded_at": datetime.now().isoformat(),
                                        "content_length": len(cleaned_content),
                                        "status_code": response.status
                                    }
                                )
                            else:
                                logger.warning(f"Content too short from {source.url}: {len(cleaned_content)} chars")
                                
                        else:
                            logger.warning(f"HTTP {response.status} from {source.url}")
                            
                except Exception as e:
                    logger.error(f"Error loading {source.url} (attempt {attempt + 1}): {e}")
                    
                    if attempt < self.config.MAX_RETRIES - 1:
                        # Exponential backoff
                        delay = self.config.RETRY_DELAY_BASE ** attempt
                        await asyncio.sleep(min(delay, self.config.MAX_RETRY_DELAY))
                    
        return None

    async def load_all_documents_async(self) -> List[Document]:
        """
        Load all documents concurrently with progress tracking
        """
        sources = self.config.get_enabled_sources()
        logger.info(f"Starting async loading of {len(sources)} documents")
        
        start_time = time.time()
        
        # Create tasks for concurrent execution
        tasks = [
            create_task(self.load_document_async(source), name=f"load_{source.url}")
            for source in sources
        ]
        
        # Execute with progress tracking
        documents = []
        completed = 0
        
        for coro in asyncio.as_completed(tasks):
            try:
                doc = await coro
                if doc:
                    documents.append(doc)
                completed += 1
                
                if completed % 5 == 0 or completed == len(tasks):
                    logger.info(f"Progress: {completed}/{len(tasks)} documents processed")
                    
            except Exception as e:
                logger.error(f"Task failed: {e}")
                completed += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Async loading completed: {len(documents)}/{len(sources)} documents in {duration:.2f}s")
        
        return documents


class AsyncQueryProcessor:
    """
    Asynchronous query processing with concurrent capabilities
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.claude_client = None
        self.vectordb = None
        self.embeddings = None
        
        # Query processing semaphore for rate limiting
        self.query_semaphore = Semaphore(3)  # Max 3 concurrent queries

    async def setup_async_components(self):
        """Initialize async components"""
        # Setup embeddings (CPU-bound, use thread pool)
        loop = asyncio.get_event_loop()
        self.embeddings = await loop.run_in_executor(
            None, 
            self._setup_embeddings
        )
        
        # Setup Claude client
        self.claude_client = ChatAnthropic(
            model=self.config.CLAUDE_MODEL,
            max_tokens=self.config.CLAUDE_MAX_TOKENS,
            temperature=self.config.CLAUDE_TEMPERATURE,
            anthropic_api_key=self.config.ANTHROPIC_API_KEY
        )
        
        logger.info("Async components initialized")

    def _setup_embeddings(self):
        """Setup embeddings in thread pool (CPU-bound operation)"""
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            cache_folder=self.config.EMBEDDINGS_CACHE_PATH,
            model_kwargs={
                'device': 'cpu',
                'trust_remote_code': True,
                'normalize_embeddings': True
            },
            encode_kwargs={'normalize_embeddings': True}
        )

    async def process_query_async(self, query: str) -> Dict[str, Any]:
        """
        Process query asynchronously with performance monitoring
        """
        async with self.query_semaphore:
            start_time = time.time()
            
            try:
                # Vector search (CPU-bound, use thread pool)
                loop = asyncio.get_event_loop()
                similar_docs = await loop.run_in_executor(
                    None,
                    self._vector_search,
                    query
                )
                
                # Generate response with Claude
                response = await self._generate_response_async(query, similar_docs)
                
                end_time = time.time()
                query_time = end_time - start_time
                
                return {
                    "answer": response,
                    "sources": [
                        {
                            "content": doc.page_content[:200] + "...",
                            "source": doc.metadata.get("source", ""),
                            "type": doc.metadata.get("type", ""),
                            "score": score
                        }
                        for doc, score in similar_docs
                    ],
                    "query_time": f"{query_time:.2f}",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Query processing error: {e}")
                return {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

    def _vector_search(self, query: str):
        """Perform vector search in thread pool"""
        if not self.vectordb:
            raise ValueError("Vector database not initialized")
            
        return self.vectordb.similarity_search_with_score(
            query,
            k=self.config.RETRIEVER_K
        )

    async def _generate_response_async(self, query: str, similar_docs: List) -> str:
        """Generate response using Claude API asynchronously"""
        # Prepare context from similar documents
        context = "\n\n".join([
            f"來源: {doc.metadata.get('source', 'Unknown')}\n內容: {doc.page_content}"
            for doc, score in similar_docs[:3]  # Top 3 most relevant
        ])
        
        prompt = f"""
作為 O-RAN 和 Nephio 專家，請基於以下官方文件回答問題。

問題: {query}

參考文件:
{context}

請提供詳細且準確的回答，並引用相關的文件來源。回答應該：
1. 直接回答問題
2. 提供具體的實作指導
3. 引用相關的官方文件
4. 使用繁體中文回答
"""
        
        # Async invoke with error handling
        try:
            response = await asyncio.wait_for(
                self._invoke_claude_async(prompt),
                timeout=30.0  # 30 second timeout
            )
            return response.content
        except asyncio.TimeoutError:
            logger.error("Claude API timeout")
            return "抱歉，回應超時。請稍後再試。"

    async def _invoke_claude_async(self, prompt: str):
        """Invoke Claude API asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.claude_client.invoke,
            prompt
        )

    async def process_batch_queries_async(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries concurrently"""
        logger.info(f"Processing {len(queries)} queries concurrently")
        
        tasks = [
            create_task(self.process_query_async(query), name=f"query_{i}")
            for i, query in enumerate(queries)
        ]
        
        results = await gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "query_index": i,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        return processed_results


class AsyncORANNephioRAG:
    """
    Main async RAG system orchestrator
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.document_loader = None
        self.query_processor = None
        self.vectordb_manager = None
        
        # Performance monitoring
        self.metrics = {
            "queries_processed": 0,
            "documents_loaded": 0,
            "average_response_time": 0,
            "last_update": None
        }

    async def initialize_async(self):
        """Initialize all async components"""
        logger.info("Initializing async RAG system...")
        
        # Use uvloop for better performance if available
        try:
            uvloop.install()
            logger.info("Using uvloop for enhanced performance")
        except ImportError:
            logger.info("uvloop not available, using standard asyncio")
        
        # Initialize components
        self.query_processor = AsyncQueryProcessor(self.config)
        await self.query_processor.setup_async_components()
        
        logger.info("Async RAG system initialized successfully")

    async def load_documents_async(self) -> bool:
        """Load documents asynchronously"""
        try:
            async with AsyncDocumentLoader(self.config) as loader:
                documents = await loader.load_all_documents_async()
                
                if documents:
                    # Build vector database (CPU-bound, use thread pool)
                    loop = asyncio.get_event_loop()
                    success = await loop.run_in_executor(
                        None,
                        self._build_vectordb,
                        documents
                    )
                    
                    if success:
                        self.metrics["documents_loaded"] = len(documents)
                        self.metrics["last_update"] = datetime.now().isoformat()
                        logger.info(f"Successfully loaded {len(documents)} documents")
                        return True
                
                logger.error("No documents loaded")
                return False
                
        except Exception as e:
            logger.error(f"Document loading failed: {e}")
            return False

    def _build_vectordb(self, documents: List[Document]) -> bool:
        """Build vector database in thread pool"""
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            
            chunks = []
            for doc in documents:
                doc_chunks = text_splitter.split_documents([doc])
                chunks.extend(doc_chunks)
            
            # Create vector database
            vectordb = Chroma.from_documents(
                documents=chunks,
                embedding=self.query_processor.embeddings,
                persist_directory=self.config.VECTOR_DB_PATH,
                collection_name=self.config.COLLECTION_NAME
            )
            
            vectordb.persist()
            self.query_processor.vectordb = vectordb
            
            return True
            
        except Exception as e:
            logger.error(f"Vector database creation failed: {e}")
            return False

    async def query_async(self, query: str) -> Dict[str, Any]:
        """Process single query asynchronously"""
        if not self.query_processor:
            return {"error": "System not initialized"}
        
        result = await self.query_processor.process_query_async(query)
        self.metrics["queries_processed"] += 1
        
        return result

    async def batch_query_async(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries asynchronously"""
        if not self.query_processor:
            return [{"error": "System not initialized"} for _ in queries]
        
        results = await self.query_processor.process_batch_queries_async(queries)
        self.metrics["queries_processed"] += len(queries)
        
        return results

    async def get_system_status_async(self) -> Dict[str, Any]:
        """Get system status asynchronously"""
        return {
            "status": "running",
            "metrics": self.metrics,
            "config": {
                "max_concurrent_requests": getattr(self.config, 'MAX_CONCURRENT_REQUESTS', 5),
                "chunk_size": self.config.CHUNK_SIZE,
                "model": self.config.CLAUDE_MODEL
            },
            "timestamp": datetime.now().isoformat()
        }

    async def health_check_async(self) -> Dict[str, Any]:
        """Async health check endpoint"""
        try:
            # Test basic functionality
            test_query = "Test health check"
            result = await asyncio.wait_for(
                self.query_async(test_query),
                timeout=10.0
            )
            
            return {
                "status": "healthy",
                "response_time": result.get("query_time", "N/A"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Async context manager for system lifecycle
@asynccontextmanager
async def async_rag_system(config: Optional[Config] = None) -> AsyncGenerator[AsyncORANNephioRAG, None]:
    """
    Async context manager for RAG system lifecycle management
    """
    system = AsyncORANNephioRAG(config)
    
    try:
        await system.initialize_async()
        yield system
    finally:
        # Cleanup logic here
        logger.info("Cleaning up async RAG system")


# FastAPI integration example
async def create_fastapi_app():
    """
    Example FastAPI application with async RAG system
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    app = FastAPI(title="O-RAN × Nephio RAG API", version="1.0.0")
    
    class QueryRequest(BaseModel):
        query: str
        
    class BatchQueryRequest(BaseModel):
        queries: List[str]
    
    # Global RAG system instance
    rag_system = None
    
    @app.on_event("startup")
    async def startup_event():
        global rag_system
        rag_system = AsyncORANNephioRAG()
        await rag_system.initialize_async()
        await rag_system.load_documents_async()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        # Cleanup logic
        pass
    
    @app.post("/query")
    async def query_endpoint(request: QueryRequest):
        if not rag_system:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        result = await rag_system.query_async(request.query)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    
    @app.post("/batch-query")
    async def batch_query_endpoint(request: BatchQueryRequest):
        if not rag_system:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        results = await rag_system.batch_query_async(request.queries)
        return {"results": results}
    
    @app.get("/health")
    async def health_endpoint():
        if not rag_system:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        return await rag_system.health_check_async()
    
    @app.get("/status")
    async def status_endpoint():
        if not rag_system:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        return await rag_system.get_system_status_async()
    
    return app


# Example usage
async def main():
    """Example usage of async RAG system"""
    config = Config()
    
    async with async_rag_system(config) as rag:
        # Load documents
        await rag.load_documents_async()
        
        # Single query
        result = await rag.query_async("How to scale O-RAN network functions with Nephio?")
        print(f"Single query result: {result}")
        
        # Batch queries
        queries = [
            "What is Nephio?",
            "How to deploy O-RAN components?",
            "Network function scaling strategies"
        ]
        
        batch_results = await rag.batch_query_async(queries)
        print(f"Batch query results: {len(batch_results)} responses")


if __name__ == "__main__":
    asyncio.run(main())