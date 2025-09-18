"""
Enhanced RAG System for O-RAN × Nephio
Integrates all components into a comprehensive RAG system with developer-focused features
"""

import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

from langchain.docstore.document import Document

# Import all components
try:
    from .config import Config
    from .document_preprocessor import EnhancedDocumentPreprocessor
    from .smart_chunking import SmartChunkingSystem
    from .advanced_embeddings import AdvancedEmbeddingSystem
    from .vector_database_manager import AdvancedVectorDatabaseManager
    from .retrieval_engine import AdvancedRetrievalEngine, QueryType
    from .enhanced_llm_integration import EnhancedLLMManager, ResponseType
    from .document_loader import DocumentLoader
except ImportError:
    from config import Config
    from document_preprocessor import EnhancedDocumentPreprocessor
    from smart_chunking import SmartChunkingSystem
    from advanced_embeddings import AdvancedEmbeddingSystem
    from vector_database_manager import AdvancedVectorDatabaseManager
    from retrieval_engine import AdvancedRetrievalEngine, QueryType
    from enhanced_llm_integration import EnhancedLLMManager, ResponseType
    from document_loader import DocumentLoader

logger = logging.getLogger(__name__)


@dataclass
class RAGSystemMetrics:
    """Comprehensive metrics for the RAG system"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time: float = 0.0
    total_documents_processed: int = 0
    total_chunks_created: int = 0
    vector_database_size: int = 0
    last_index_update: Optional[str] = None
    system_health_score: float = 100.0


class EnhancedRAGSystem:
    """Enhanced RAG System with comprehensive O-RAN/Nephio optimization"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        # Validate configuration
        try:
            self.config.validate()
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
        
        # Initialize all components
        logger.info("Initializing Enhanced RAG System components...")
        
        # Core processing components
        self.document_loader = DocumentLoader(self.config)
        self.preprocessor = EnhancedDocumentPreprocessor(self.config)
        self.chunking_system = SmartChunkingSystem(self.config)
        self.embedding_system = AdvancedEmbeddingSystem(self.config)
        
        # Storage and retrieval components
        self.vector_db_manager = AdvancedVectorDatabaseManager(
            self.config, self.embedding_system
        )
        self.retrieval_engine = AdvancedRetrievalEngine(
            self.config, self.vector_db_manager, self.embedding_system
        )
        
        # Generation component
        self.llm_manager = EnhancedLLMManager(self.config)
        
        # System metrics
        self.metrics = RAGSystemMetrics()
        
        # System state
        self.is_ready = False
        self.initialization_time: Optional[datetime] = None
        
        logger.info("Enhanced RAG System initialized successfully")
    
    async def initialize_system(self, force_rebuild: bool = False, 
                              custom_documents: Optional[List[Document]] = None) -> bool:
        """Initialize the complete RAG system"""
        start_time = time.time()
        logger.info("Starting Enhanced RAG System initialization...")
        
        try:
            # Step 1: Load and preprocess documents
            if custom_documents:
                logger.info(f"Using {len(custom_documents)} custom documents")
                raw_documents = custom_documents
            else:
                logger.info("Loading documents from configured sources...")
                raw_documents = self.document_loader.load_all_documents()
            
            if not raw_documents:
                logger.error("No documents loaded - cannot initialize system")
                return False
            
            logger.info(f"Loaded {len(raw_documents)} raw documents")
            
            # Step 2: Enhanced preprocessing
            logger.info("Starting enhanced document preprocessing...")
            processed_documents = await self.preprocessor.process_documents(raw_documents)
            
            if not processed_documents:
                logger.error("Document preprocessing failed")
                return False
            
            logger.info(f"Preprocessed {len(processed_documents)} documents")
            
            # Step 3: Smart chunking
            logger.info("Starting smart chunking...")
            chunks = self.chunking_system.chunk_documents(processed_documents)
            
            if not chunks:
                logger.error("Document chunking failed")
                return False
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 4: Build vector index
            logger.info("Building vector database index...")
            index_success = self.vector_db_manager.build_index(chunks)
            
            if not index_success:
                logger.error("Vector database index building failed")
                return False
            
            # Update metrics
            self.metrics.total_documents_processed = len(processed_documents)
            self.metrics.total_chunks_created = len(chunks)
            self.metrics.vector_database_size = len(chunks)
            self.metrics.last_index_update = datetime.now().isoformat()
            
            # Mark system as ready
            self.is_ready = True
            self.initialization_time = datetime.now()
            
            initialization_time = time.time() - start_time
            logger.info(f"Enhanced RAG System initialization completed in {initialization_time:.2f}s")
            
            # Log system summary
            self._log_system_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"RAG System initialization failed: {e}")
            self.is_ready = False
            return False
    
    def query(self, question: str, 
             k: Optional[int] = None,
             filters: Optional[Dict[str, Any]] = None,
             response_type: Optional[ResponseType] = None,
             **kwargs) -> Dict[str, Any]:
        """Process a query through the complete RAG pipeline"""
        start_time = time.time()
        
        # Check system readiness
        if not self.is_ready:
            logger.warning("System not ready, attempting lazy initialization...")
            # Try to initialize synchronously (not ideal but necessary for compatibility)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(self.initialize_system())
                if not success:
                    return self._create_error_response(
                        "System initialization failed", start_time
                    )
            finally:
                loop.close()
        
        try:
            # Step 1: Advanced retrieval
            logger.debug(f"Processing query: {question[:100]}...")
            
            retrieval_result = self.retrieval_engine.retrieve(
                query=question,
                k=k,
                filters=filters,
                **kwargs
            )
            
            if not retrieval_result.documents:
                logger.warning("No relevant documents found")
                return self._create_error_response(
                    "No relevant documents found for your query", start_time
                )
            
            logger.debug(f"Retrieved {len(retrieval_result.documents)} documents")
            
            # Step 2: Enhanced answer generation
            generation_result = self.llm_manager.generate_answer(
                query=question,
                retrieval_result=retrieval_result,
                response_type=response_type
            )
            
            # Update metrics
            self._update_query_metrics(start_time, generation_result.get('success', False))
            
            # Combine results
            final_response = {
                'success': generation_result.get('success', False),
                'answer': generation_result.get('answer', 'No answer generated'),
                'query': question,
                'response_type': generation_result.get('response_type', 'unknown'),
                'sources': self._format_sources(retrieval_result.documents, retrieval_result.scores),
                'retrieval_info': {
                    'documents_found': len(retrieval_result.documents),
                    'query_type': retrieval_result.query_type.value,
                    'retrieval_time': retrieval_result.retrieval_time,
                    'total_candidates': retrieval_result.total_candidates,
                    'reranked': retrieval_result.reranked
                },
                'generation_info': {
                    'generation_time': generation_result.get('generation_time', 0),
                    'context_length': generation_result.get('context_length', 0),
                    'model_info': generation_result.get('model_info', {})
                },
                'system_info': {
                    'total_response_time': round(time.time() - start_time, 3),
                    'system_ready': self.is_ready,
                    'constraint_compliant': True,
                    'integration_method': 'enhanced_rag_pipeline'
                }
            }
            
            if not generation_result.get('success'):
                final_response['error'] = generation_result.get('error', 'Unknown error')
            
            return final_response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            self._update_query_metrics(start_time, False)
            return self._create_error_response(str(e), start_time)
    
    def add_documents(self, documents: List[Document], 
                     reprocess: bool = True) -> bool:
        """Add new documents to the system"""
        if not documents:
            logger.warning("No documents provided to add")
            return False
        
        try:
            logger.info(f"Adding {len(documents)} new documents to system")
            
            if reprocess:
                # Full preprocessing pipeline
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    processed_docs = loop.run_until_complete(
                        self.preprocessor.process_documents(documents)
                    )
                finally:
                    loop.close()
                
                chunks = self.chunking_system.chunk_documents(processed_docs)
            else:
                # Use documents as-is (assume already processed)
                chunks = documents
            
            # Add to vector database
            success = self.vector_db_manager.add_documents(chunks)
            
            if success:
                self.metrics.total_documents_processed += len(documents)
                self.metrics.total_chunks_created += len(chunks)
                self.metrics.vector_database_size += len(chunks)
                self.metrics.last_index_update = datetime.now().isoformat()
                logger.info(f"Successfully added {len(chunks)} chunks to system")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Collect status from all components
        status = {
            'system_ready': self.is_ready,
            'initialization_time': self.initialization_time.isoformat() if self.initialization_time else None,
            'health_score': self._calculate_health_score(),
            'metrics': {
                'total_queries': self.metrics.total_queries,
                'successful_queries': self.metrics.successful_queries,
                'failed_queries': self.metrics.failed_queries,
                'success_rate': round(
                    (self.metrics.successful_queries / max(self.metrics.total_queries, 1)) * 100, 2
                ),
                'average_response_time': round(self.metrics.average_response_time, 3),
                'total_documents_processed': self.metrics.total_documents_processed,
                'total_chunks_created': self.metrics.total_chunks_created,
                'vector_database_size': self.metrics.vector_database_size,
                'last_index_update': self.metrics.last_index_update
            },
            'component_status': {
                'document_loader': self.document_loader.get_load_statistics(),
                'preprocessor': self.preprocessor.get_processing_metrics(),
                'chunking_system': self.chunking_system.get_chunking_stats(),
                'embedding_system': self.embedding_system.get_embedding_metrics(),
                'vector_database': self.vector_db_manager.get_database_stats(),
                'retrieval_engine': self.retrieval_engine.get_retrieval_metrics(),
                'llm_manager': self.llm_manager.get_llm_metrics()
            },
            'configuration': self.config.get_config_summary()
        }
        
        return status
    
    def benchmark_system(self, test_queries: List[str] = None) -> Dict[str, Any]:
        """Benchmark the complete RAG system"""
        if not test_queries:
            test_queries = [
                "What is O-RAN architecture?",
                "How to deploy Nephio workloads?",
                "Kubernetes integration with O-RAN",
                "Network function scaling strategies",
                "Troubleshooting deployment issues"
            ]
        
        logger.info(f"Starting system benchmark with {len(test_queries)} queries")
        
        start_time = time.time()
        benchmark_results = {
            'test_queries': len(test_queries),
            'individual_results': [],
            'summary': {}
        }
        
        successful_queries = 0
        total_response_time = 0
        retrieval_times = []
        generation_times = []
        
        for i, query in enumerate(test_queries):
            query_start = time.time()
            
            try:
                result = self.query(query, use_cache=False)  # Disable cache for benchmarking
                query_time = time.time() - query_start
                
                individual_result = {
                    'query': query,
                    'success': result.get('success', False),
                    'response_time': round(query_time, 3),
                    'retrieval_time': result.get('retrieval_info', {}).get('retrieval_time', 0),
                    'generation_time': result.get('generation_info', {}).get('generation_time', 0),
                    'documents_found': result.get('retrieval_info', {}).get('documents_found', 0)
                }
                
                if result.get('success'):
                    successful_queries += 1
                    retrieval_times.append(individual_result['retrieval_time'])
                    generation_times.append(individual_result['generation_time'])
                else:
                    individual_result['error'] = result.get('error', 'Unknown error')
                
                total_response_time += query_time
                benchmark_results['individual_results'].append(individual_result)
                
                logger.debug(f"Benchmark query {i+1}/{len(test_queries)} completed in {query_time:.3f}s")
                
            except Exception as e:
                logger.error(f"Benchmark query {i+1} failed: {e}")
                benchmark_results['individual_results'].append({
                    'query': query,
                    'success': False,
                    'error': str(e),
                    'response_time': time.time() - query_start
                })
        
        total_benchmark_time = time.time() - start_time
        
        # Calculate summary statistics
        benchmark_results['summary'] = {
            'total_time': round(total_benchmark_time, 3),
            'successful_queries': successful_queries,
            'failed_queries': len(test_queries) - successful_queries,
            'success_rate': round((successful_queries / len(test_queries)) * 100, 2),
            'average_response_time': round(total_response_time / len(test_queries), 3),
            'queries_per_second': round(len(test_queries) / total_benchmark_time, 2),
            'average_retrieval_time': round(sum(retrieval_times) / max(len(retrieval_times), 1), 3),
            'average_generation_time': round(sum(generation_times) / max(len(generation_times), 1), 3)
        }
        
        logger.info(f"Benchmark completed: {successful_queries}/{len(test_queries)} successful queries")
        
        return benchmark_results
    
    def _create_error_response(self, error_message: str, start_time: float) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'success': False,
            'answer': f'Sorry, I encountered an error: {error_message}',
            'error': error_message,
            'sources': [],
            'system_info': {
                'total_response_time': round(time.time() - start_time, 3),
                'system_ready': self.is_ready,
                'constraint_compliant': True,
                'integration_method': 'enhanced_rag_pipeline'
            }
        }
    
    def _format_sources(self, documents: List[Document], 
                       scores: List[float]) -> List[Dict[str, Any]]:
        """Format source documents for response"""
        sources = []
        
        for doc, score in zip(documents, scores):
            source = {
                'content_preview': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,
                'metadata': {
                    'source_url': doc.metadata.get('source_url', 'unknown'),
                    'title': doc.metadata.get('title', 'Untitled'),
                    'source_type': doc.metadata.get('source_type', 'unknown'),
                    'relevance_score': round(float(score), 3)
                }
            }
            
            # Add technical context if available
            technical_info = {}
            for key in ['total_technical_terms', 'code_blocks_count', 'diagrams_count']:
                if key in doc.metadata:
                    technical_info[key] = doc.metadata[key]
            
            if technical_info:
                source['technical_context'] = technical_info
            
            sources.append(source)
        
        return sources
    
    def _update_query_metrics(self, start_time: float, success: bool) -> None:
        """Update query metrics"""
        response_time = time.time() - start_time
        
        self.metrics.total_queries += 1
        if success:
            self.metrics.successful_queries += 1
        else:
            self.metrics.failed_queries += 1
        
        # Update running average
        total_response_time = self.metrics.average_response_time * (self.metrics.total_queries - 1) + response_time
        self.metrics.average_response_time = total_response_time / self.metrics.total_queries
    
    def _calculate_health_score(self) -> float:
        """Calculate system health score"""
        score = 100.0
        
        # Deduct for system not ready
        if not self.is_ready:
            score -= 50.0
        
        # Deduct for high failure rate
        if self.metrics.total_queries > 0:
            failure_rate = self.metrics.failed_queries / self.metrics.total_queries
            score -= failure_rate * 30.0
        
        # Deduct for slow response times
        if self.metrics.average_response_time > 10.0:
            score -= 10.0
        elif self.metrics.average_response_time > 5.0:
            score -= 5.0
        
        return max(score, 0.0)
    
    def _log_system_summary(self) -> None:
        """Log system initialization summary"""
        logger.info("=== Enhanced RAG System Summary ===")
        logger.info(f"Documents processed: {self.metrics.total_documents_processed}")
        logger.info(f"Chunks created: {self.metrics.total_chunks_created}")
        logger.info(f"Vector database size: {self.metrics.vector_database_size}")
        logger.info(f"Available backends: {self.vector_db_manager.get_available_backends()}")
        logger.info(f"Embedding providers: {self.embedding_system.get_available_providers()}")
        logger.info(f"System health score: {self._calculate_health_score():.1f}/100")
        logger.info("=================================")


# Factory function
def create_enhanced_rag_system(config: Optional[Config] = None) -> EnhancedRAGSystem:
    """Create enhanced RAG system"""
    return EnhancedRAGSystem(config)


# Convenience function for quick queries
def quick_rag_query(question: str, config: Optional[Config] = None) -> Dict[str, Any]:
    """Quick RAG query with automatic system initialization"""
    rag_system = create_enhanced_rag_system(config)
    
    # Initialize system synchronously
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(rag_system.initialize_system())
        if not success:
            return {
                'success': False,
                'answer': 'System initialization failed',
                'error': 'Could not initialize RAG system'
            }
    finally:
        loop.close()
    
    return rag_system.query(question)
