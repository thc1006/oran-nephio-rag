"""
Asynchronous O-RAN × Nephio RAG System Implementation - Browser Mode
Constraint-compliant version using browser automation for AI integration
"""

import asyncio
import logging
import os
import time
from asyncio import Semaphore, gather
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

# AsyncIO imports
from aiohttp import ClientSession, ClientTimeout, TCPConnector

# Optional high-performance event loop
try:
    import uvloop

    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

from langchain.text_splitter import RecursiveCharacterTextSplitter

# LangChain core components (lightweight)
from langchain_core.documents import Document

try:
    from .config import Config, DocumentSource
    from .document_loader import DocumentContentCleaner
    from .oran_nephio_rag_fixed import SimplifiedVectorDatabase
    from .puter_integration import PuterRAGManager, create_puter_rag_manager
except ImportError:
    from config import Config, DocumentSource
    from document_loader import DocumentContentCleaner
    from oran_nephio_rag_fixed import SimplifiedVectorDatabase
    from puter_integration import create_puter_rag_manager

logger = logging.getLogger(__name__)


class AsyncDocumentLoader:
    """
    High-performance async document loader
    Browser-compatible version without heavy ML dependencies
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.content_cleaner = DocumentContentCleaner(self.config)
        self.session: Optional[ClientSession] = None

        # Performance optimizations
        self.connector = TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=10,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        self.timeout = ClientTimeout(total=self.config.REQUEST_TIMEOUT, connect=10, sock_read=30)

        # Concurrency control
        self.semaphore = Semaphore(self.config.MAX_CONCURRENT_REQUESTS or 5)

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers={
                "User-Agent": "O-RAN-Nephio-RAG/1.0 AsyncClient",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self.session:
            await self.session.close()
        await self.connector.close()

    async def load_document_async(self, source: DocumentSource) -> Optional[Document]:
        """Load single document asynchronously with retry logic"""
        async with self.semaphore:
            return await self._fetch_with_retry(source)

    async def _fetch_with_retry(self, source: DocumentSource, max_retries: int = 3) -> Optional[Document]:
        """Fetch document with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                async with self.session.get(source.url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Clean and process content
                        cleaned_content = self.content_cleaner.clean_content(content, source.source_type)

                        return Document(
                            page_content=cleaned_content,
                            metadata={
                                "source_url": source.url,
                                "source_type": source.source_type,
                                "title": source.title,
                                "description": source.description,
                                "fetch_time": datetime.now().isoformat(),
                                "content_length": len(cleaned_content),
                            },
                        )
                    else:
                        logger.warning(f"HTTP {response.status} for {source.url}")

            except Exception as e:
                wait_time = 2**attempt
                logger.warning(f"Attempt {attempt + 1} failed for {source.url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to load {source.url} after {max_retries} attempts")

        return None

    async def batch_load_documents(self, sources: List[DocumentSource]) -> List[Document]:
        """Load multiple documents concurrently"""
        logger.info(f"Loading {len(sources)} documents asynchronously...")

        # Create tasks for concurrent loading
        tasks = [self.load_document_async(source) for source in sources]
        results = await gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        documents = []
        for i, result in enumerate(results):
            if isinstance(result, Document):
                documents.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Document {i} failed: {result}")

        logger.info(f"Successfully loaded {len(documents)} out of {len(sources)} documents")
        return documents


class AsyncBrowserRAGSystem:
    """
    Async RAG system using browser automation for AI integration
    Fully constraint-compliant implementation
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.vectordb = None
        self.text_splitter = None
        self.puter_manager = None
        self._setup_components()

    def _setup_components(self):
        """Setup system components for browser mode"""
        # Text splitter for document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\\n\\n", "\\n", " ", ""],
        )

        # Simplified vector database (no heavy ML)
        db_file = os.path.join(self.config.VECTOR_DB_PATH, "async_vectordb.json")
        self.vectordb = SimplifiedVectorDatabase(db_file)

        # Browser-based AI manager
        model = getattr(self.config, "PUTER_MODEL", "claude-sonnet-4")
        self.puter_manager = create_puter_rag_manager(model=model, headless=True)

        logger.info("✅ Async browser RAG system components initialized")

    async def build_vector_database_async(self, sources: Optional[List[DocumentSource]] = None) -> bool:
        """Build vector database asynchronously"""
        try:
            if not sources:
                sources = [s for s in self.config.OFFICIAL_SOURCES if s.enabled]

            logger.info(f"Building vector database with {len(sources)} sources...")

            # Load documents asynchronously
            async with AsyncDocumentLoader(self.config) as loader:
                documents = await loader.batch_load_documents(sources)

            if not documents:
                logger.error("No documents loaded for vector database")
                return False

            # Split documents
            all_chunks = []
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                all_chunks.extend(chunks)

            logger.info(f"Created {len(all_chunks)} document chunks")

            # Add to vector database
            self.vectordb.add_documents(all_chunks)
            self.vectordb.save()

            logger.info("✅ Async vector database built successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Async vector database build failed: {e}")
            return False

    async def query_async(self, question: str, k: int = 6) -> Dict[str, Any]:
        """Execute async RAG query using browser integration"""
        try:
            start_time = time.time()

            if not self.vectordb:
                return {"error": "vector_db_not_ready", "answer": "Vector database not initialized"}

            # Retrieve relevant documents
            relevant_docs = self.vectordb.similarity_search(question, k=k)

            if not relevant_docs:
                # Direct query without context
                result = self.puter_manager.query(question)
            else:
                # Query with context
                context = "\\n\\n".join([doc.page_content for doc in relevant_docs])
                result = self.puter_manager.query(question, context=context)

            end_time = time.time()

            # Process sources
            sources = []
            for doc in relevant_docs:
                metadata = doc.metadata
                sources.append(
                    {
                        "url": metadata.get("source_url", ""),
                        "type": metadata.get("source_type", ""),
                        "description": metadata.get("description", ""),
                        "title": metadata.get("title", ""),
                        "content_preview": (
                            doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                        ),
                    }
                )

            return {
                "answer": result.get("answer", "No answer received"),
                "sources": sources,
                "query_time": round(end_time - start_time, 2),
                "mode": "async_browser_rag",
                "model": result.get("model"),
                "integration_type": "async_browser_automation",
                "constraint_compliant": True,
            }

        except Exception as e:
            logger.error(f"Async RAG query failed: {e}")
            return {"error": str(e), "answer": f"Query processing error: {str(e)}"}

    async def batch_query_async(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries concurrently"""
        logger.info(f"Processing {len(questions)} queries asynchronously...")

        tasks = [self.query_async(q) for q in questions]
        results = await gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({"error": str(result), "answer": f"Query {i} failed: {str(result)}"})
            else:
                processed_results.append(result)

        return processed_results

    def get_system_status(self) -> Dict[str, Any]:
        """Get async system status"""
        try:
            vectordb_ready = len(self.vectordb.documents) > 0 if self.vectordb else False
            puter_status = self.puter_manager.get_status() if self.puter_manager else {}

            return {
                "vectordb_ready": vectordb_ready,
                "puter_integration": puter_status,
                "total_documents": len(self.vectordb.documents) if self.vectordb else 0,
                "last_update": datetime.now().isoformat(),
                "integration_type": "async_browser_automation",
                "constraint_compliant": True,
                "performance_mode": "async",
            }

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {"error": str(e)}


# Async context manager for system lifecycle
@asynccontextmanager
async def async_rag_system(config: Optional[Config] = None) -> AsyncGenerator[AsyncBrowserRAGSystem, None]:
    """
    Async context manager for RAG system
    Ensures proper setup and cleanup of resources
    """
    # Set up high-performance event loop if available
    if UVLOOP_AVAILABLE and asyncio.get_event_loop_policy().__class__.__name__ != "WindowsProactorEventLoopPolicy":
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("Using uvloop for enhanced performance")

    rag_system = AsyncBrowserRAGSystem(config)

    try:
        # Load existing database
        if rag_system.vectordb:
            rag_system.vectordb.load()

        logger.info("✅ Async RAG system ready")
        yield rag_system

    finally:
        # Cleanup resources
        logger.info("🧹 Cleaning up async RAG system resources")


# Factory functions
def create_async_rag_system(config: Optional[Config] = None) -> AsyncBrowserRAGSystem:
    """Create async RAG system instance"""
    return AsyncBrowserRAGSystem(config)


async def quick_async_query(question: str, config: Optional[Config] = None) -> str:
    """Quick async query function"""
    try:
        async with async_rag_system(config) as rag:
            result = await rag.query_async(question)

            if result.get("error"):
                return f"Query failed: {result['error']}"

            return result.get("answer", "No answer received")

    except Exception as e:
        logger.error(f"Quick async query failed: {e}")
        return f"Query failed: {str(e)}"


# Performance utilities
def setup_async_performance():
    """Setup optimal async performance settings"""
    if UVLOOP_AVAILABLE:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("Async performance optimized with uvloop")
    else:
        logger.info("Using standard asyncio (consider installing uvloop for better performance)")


# Backward compatibility aliases
AsyncORANNephioRAG = AsyncBrowserRAGSystem
AsyncRAGSystem = AsyncBrowserRAGSystem
