"""
Advanced Vector Database Manager for O-RAN × Nephio RAG
Supports multiple vector database backends with fallback and optimization
"""

import logging
import os
import shutil
import time
import json
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Core dependencies
import numpy as np
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStore

# Vector database backends
try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import pinecone
    from langchain_community.vectorstores import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import weaviate
    from langchain_community.vectorstores import Weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

# Import configuration and other components
try:
    from .config import Config
    from .advanced_embeddings import AdvancedEmbeddingSystem
except ImportError:
    from config import Config
    from advanced_embeddings import AdvancedEmbeddingSystem

logger = logging.getLogger(__name__)


@dataclass
class VectorDBMetrics:
    """Metrics for vector database operations"""
    total_documents: int = 0
    total_vectors: int = 0
    index_build_time: float = 0.0
    query_count: int = 0
    total_query_time: float = 0.0
    average_query_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    database_size_mb: float = 0.0
    last_update: Optional[str] = None


class VectorDatabaseBackend(ABC):
    """Abstract base class for vector database backends"""
    
    def __init__(self, config: Config, embedding_system: AdvancedEmbeddingSystem):
        self.config = config
        self.embedding_system = embedding_system
        self.is_ready = False
        self.vectorstore: Optional[VectorStore] = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the vector database backend"""
        pass
    
    @abstractmethod
    def build_index(self, documents: List[Document]) -> bool:
        """Build vector index from documents"""
        pass
    
    @abstractmethod
    def search_similar(self, query: str, k: int = 5, **kwargs) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> bool:
        """Add new documents to the index"""
        pass
    
    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the index"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        pass


class ChromaBackend(VectorDatabaseBackend):
    """ChromaDB backend implementation"""
    
    def __init__(self, config: Config, embedding_system: AdvancedEmbeddingSystem):
        super().__init__(config, embedding_system)
        self.persist_directory = config.VECTOR_DB_PATH
        self.collection_name = config.COLLECTION_NAME
    
    def initialize(self) -> bool:
        """Initialize ChromaDB"""
        if not CHROMA_AVAILABLE:
            logger.error("ChromaDB not available")
            return False
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.persist_directory), exist_ok=True)
            
            # Try to load existing database
            if os.path.exists(self.persist_directory):
                self.vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embedding_system.get_best_provider(),
                    persist_directory=self.persist_directory
                )
                
                # Verify the database has content
                try:
                    count = self.vectorstore._collection.count()
                    if count > 0:
                        logger.info(f"Loaded existing ChromaDB with {count} vectors")
                        self.is_ready = True
                        return True
                except Exception as e:
                    logger.warning(f"Existing ChromaDB verification failed: {e}")
            
            logger.info("ChromaDB backend initialized (empty)")
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            return False
    
    def build_index(self, documents: List[Document]) -> bool:
        """Build ChromaDB index from documents"""
        if not documents:
            logger.warning("No documents to index")
            return False
        
        try:
            start_time = time.time()
            logger.info(f"Building ChromaDB index with {len(documents)} documents")
            
            # Clear existing database
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
            
            # Create new database
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_system.get_best_provider(),
                collection_name=self.collection_name,
                persist_directory=self.persist_directory
            )
            
            # Persist the database
            self.vectorstore.persist()
            
            build_time = time.time() - start_time
            logger.info(f"ChromaDB index built in {build_time:.2f}s")
            
            self.is_ready = True
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB index building failed: {e}")
            return False
    
    def search_similar(self, query: str, k: int = 5, **kwargs) -> List[Tuple[Document, float]]:
        """Search for similar documents in ChromaDB"""
        if not self.is_ready or not self.vectorstore:
            logger.error("ChromaDB not ready for search")
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add new documents to ChromaDB"""
        if not self.is_ready or not self.vectorstore:
            logger.error("ChromaDB not ready for adding documents")
            return False
        
        try:
            self.vectorstore.add_documents(documents)
            self.vectorstore.persist()
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            return False
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from ChromaDB"""
        if not self.is_ready or not self.vectorstore:
            logger.error("ChromaDB not ready for deletion")
            return False
        
        try:
            # ChromaDB delete implementation
            self.vectorstore.delete(document_ids)
            self.vectorstore.persist()
            logger.info(f"Deleted {len(document_ids)} documents from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from ChromaDB: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics"""
        stats = {
            'backend_type': 'ChromaDB',
            'ready': self.is_ready,
            'persist_directory': self.persist_directory,
            'collection_name': self.collection_name
        }
        
        if self.is_ready and self.vectorstore:
            try:
                count = self.vectorstore._collection.count()
                stats.update({
                    'document_count': count,
                    'database_size_mb': self._get_database_size(),
                    'error': None
                })
            except Exception as e:
                stats.update({
                    'document_count': 0,
                    'database_size_mb': 0,
                    'error': str(e)
                })
        else:
            stats.update({
                'document_count': 0,
                'database_size_mb': 0,
                'error': 'Database not ready'
            })
        
        return stats
    
    def _get_database_size(self) -> float:
        """Get database size in MB"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.persist_directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0


class PineconeBackend(VectorDatabaseBackend):
    """Pinecone backend implementation"""
    
    def __init__(self, config: Config, embedding_system: AdvancedEmbeddingSystem):
        super().__init__(config, embedding_system)
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.environment = os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        self.index_name = config.COLLECTION_NAME.replace('_', '-')  # Pinecone naming requirements
    
    def initialize(self) -> bool:
        """Initialize Pinecone"""
        if not PINECONE_AVAILABLE:
            logger.error("Pinecone not available")
            return False
        
        if not self.api_key:
            logger.error("Pinecone API key not provided")
            return False
        
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
            
            # Check if index exists
            if self.index_name in pinecone.list_indexes():
                logger.info(f"Using existing Pinecone index: {self.index_name}")
                self.is_ready = True
            else:
                logger.info(f"Pinecone index '{self.index_name}' does not exist, will be created on first build")
            
            return True
            
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
            return False
    
    def build_index(self, documents: List[Document]) -> bool:
        """Build Pinecone index from documents"""
        if not documents:
            logger.warning("No documents to index")
            return False
        
        try:
            start_time = time.time()
            logger.info(f"Building Pinecone index with {len(documents)} documents")
            
            # Get embedding dimension
            dimension = self.embedding_system.get_best_provider().get_dimension()
            
            # Create index if it doesn't exist
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric='cosine'
                )
                logger.info(f"Created Pinecone index '{self.index_name}' with dimension {dimension}")
            
            # Create vectorstore
            self.vectorstore = Pinecone.from_documents(
                documents=documents,
                embedding=self.embedding_system.get_best_provider(),
                index_name=self.index_name
            )
            
            build_time = time.time() - start_time
            logger.info(f"Pinecone index built in {build_time:.2f}s")
            
            self.is_ready = True
            return True
            
        except Exception as e:
            logger.error(f"Pinecone index building failed: {e}")
            return False
    
    def search_similar(self, query: str, k: int = 5, **kwargs) -> List[Tuple[Document, float]]:
        """Search for similar documents in Pinecone"""
        if not self.is_ready or not self.vectorstore:
            logger.error("Pinecone not ready for search")
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add new documents to Pinecone"""
        if not self.is_ready or not self.vectorstore:
            logger.error("Pinecone not ready for adding documents")
            return False
        
        try:
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to Pinecone")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents to Pinecone: {e}")
            return False
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from Pinecone"""
        if not self.is_ready:
            logger.error("Pinecone not ready for deletion")
            return False
        
        try:
            # Pinecone delete implementation
            index = pinecone.Index(self.index_name)
            index.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from Pinecone")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from Pinecone: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Pinecone statistics"""
        stats = {
            'backend_type': 'Pinecone',
            'ready': self.is_ready,
            'index_name': self.index_name,
            'environment': self.environment
        }
        
        if self.is_ready:
            try:
                index = pinecone.Index(self.index_name)
                index_stats = index.describe_index_stats()
                stats.update({
                    'document_count': index_stats.total_vector_count,
                    'dimension': index_stats.dimension,
                    'error': None
                })
            except Exception as e:
                stats.update({
                    'document_count': 0,
                    'dimension': 0,
                    'error': str(e)
                })
        else:
            stats.update({
                'document_count': 0,
                'dimension': 0,
                'error': 'Database not ready'
            })
        
        return stats


class AdvancedVectorDatabaseManager:
    """Advanced vector database manager with multiple backend support"""
    
    def __init__(self, config: Optional[Config] = None, 
                 embedding_system: Optional[AdvancedEmbeddingSystem] = None):
        self.config = config or Config()
        self.embedding_system = embedding_system or AdvancedEmbeddingSystem(self.config)
        
        # Initialize available backends
        self.backends = {}
        self.active_backend: Optional[VectorDatabaseBackend] = None
        self._initialize_backends()
        
        # Metrics
        self.metrics = VectorDBMetrics()
        
        # Query cache for performance
        self.query_cache = {}
        self.max_cache_size = 100
        
        logger.info(f"Vector database manager initialized with {len(self.backends)} backends")
    
    def _initialize_backends(self) -> None:
        """Initialize all available vector database backends"""
        # ChromaDB backend (highest priority for local development)
        if CHROMA_AVAILABLE:
            try:
                chroma_backend = ChromaBackend(self.config, self.embedding_system)
                if chroma_backend.initialize():
                    self.backends['chroma'] = chroma_backend
                    logger.info("ChromaDB backend available")
            except Exception as e:
                logger.warning(f"ChromaDB backend initialization failed: {e}")
        
        # Pinecone backend (for production)
        if PINECONE_AVAILABLE and os.getenv('PINECONE_API_KEY'):
            try:
                pinecone_backend = PineconeBackend(self.config, self.embedding_system)
                if pinecone_backend.initialize():
                    self.backends['pinecone'] = pinecone_backend
                    logger.info("Pinecone backend available")
            except Exception as e:
                logger.warning(f"Pinecone backend initialization failed: {e}")
        
        # Select active backend (prefer Pinecone for production, ChromaDB for development)
        backend_priority = ['pinecone', 'chroma']
        
        for backend_name in backend_priority:
            if backend_name in self.backends:
                self.active_backend = self.backends[backend_name]
                logger.info(f"Selected active backend: {backend_name}")
                break
        
        if not self.active_backend:
            raise RuntimeError("No vector database backends available")
    
    def build_index(self, documents: List[Document], backend_name: Optional[str] = None) -> bool:
        """Build vector index from documents"""
        if not documents:
            logger.warning("No documents provided for index building")
            return False
        
        # Select backend
        backend = self._get_backend(backend_name)
        if not backend:
            return False
        
        start_time = time.time()
        
        # Clear query cache
        self.query_cache.clear()
        
        # Build index
        success = backend.build_index(documents)
        
        if success:
            self.metrics.total_documents = len(documents)
            self.metrics.index_build_time = time.time() - start_time
            self.metrics.last_update = datetime.now().isoformat()
            logger.info(f"Index built successfully with {len(documents)} documents")
        
        return success
    
    def search_similar(self, query: str, k: int = 5, 
                      backend_name: Optional[str] = None, 
                      use_cache: bool = True) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        # Check cache first
        cache_key = f"{query}:{k}:{backend_name or 'default'}"
        if use_cache and cache_key in self.query_cache:
            self.metrics.cache_hits += 1
            return self.query_cache[cache_key]
        
        # Select backend
        backend = self._get_backend(backend_name)
        if not backend:
            return []
        
        start_time = time.time()
        
        # Perform search
        results = backend.search_similar(query, k)
        
        # Update metrics
        query_time = time.time() - start_time
        self.metrics.query_count += 1
        self.metrics.total_query_time += query_time
        self.metrics.average_query_time = self.metrics.total_query_time / self.metrics.query_count
        
        if use_cache:
            # Cache results
            if len(self.query_cache) >= self.max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.query_cache))
                del self.query_cache[oldest_key]
            
            self.query_cache[cache_key] = results
            self.metrics.cache_misses += 1
        
        logger.debug(f"Search completed in {query_time:.3f}s, found {len(results)} results")
        
        return results
    
    def add_documents(self, documents: List[Document], 
                     backend_name: Optional[str] = None) -> bool:
        """Add new documents to the index"""
        backend = self._get_backend(backend_name)
        if not backend:
            return False
        
        # Clear query cache when adding documents
        self.query_cache.clear()
        
        success = backend.add_documents(documents)
        
        if success:
            self.metrics.total_documents += len(documents)
            self.metrics.last_update = datetime.now().isoformat()
        
        return success
    
    def delete_documents(self, document_ids: List[str], 
                        backend_name: Optional[str] = None) -> bool:
        """Delete documents from the index"""
        backend = self._get_backend(backend_name)
        if not backend:
            return False
        
        # Clear query cache when deleting documents
        self.query_cache.clear()
        
        return backend.delete_documents(document_ids)
    
    def _get_backend(self, backend_name: Optional[str] = None) -> Optional[VectorDatabaseBackend]:
        """Get specified backend or active backend"""
        if backend_name:
            if backend_name not in self.backends:
                logger.error(f"Backend '{backend_name}' not available")
                return None
            return self.backends[backend_name]
        
        if not self.active_backend:
            logger.error("No active backend available")
            return None
        
        return self.active_backend
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backend names"""
        return list(self.backends.keys())
    
    def switch_backend(self, backend_name: str) -> bool:
        """Switch to a different backend"""
        if backend_name not in self.backends:
            logger.error(f"Backend '{backend_name}' not available")
            return False
        
        self.active_backend = self.backends[backend_name]
        self.query_cache.clear()  # Clear cache when switching backends
        logger.info(f"Switched to backend: {backend_name}")
        return True
    
    def get_database_stats(self, backend_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        backend = self._get_backend(backend_name)
        if not backend:
            return {'error': 'Backend not available'}
        
        backend_stats = backend.get_stats()
        
        # Add manager-level metrics
        manager_stats = {
            'manager_metrics': {
                'query_count': self.metrics.query_count,
                'total_query_time': round(self.metrics.total_query_time, 3),
                'average_query_time': round(self.metrics.average_query_time, 3),
                'cache_hits': self.metrics.cache_hits,
                'cache_misses': self.metrics.cache_misses,
                'cache_hit_rate': round(
                    (self.metrics.cache_hits / max(self.metrics.cache_hits + self.metrics.cache_misses, 1)) * 100, 2
                ),
                'active_backend': type(self.active_backend).__name__ if self.active_backend else None,
                'available_backends': self.get_available_backends()
            }
        }
        
        return {**backend_stats, **manager_stats}
    
    def benchmark_backends(self, test_query: str = "test query", k: int = 5) -> Dict[str, Dict[str, Any]]:
        """Benchmark all available backends"""
        results = {}
        
        for backend_name, backend in self.backends.items():
            if not backend.is_ready:
                results[backend_name] = {
                    'success': False,
                    'error': 'Backend not ready',
                    'query_time': 0
                }
                continue
            
            try:
                start_time = time.time()
                search_results = backend.search_similar(test_query, k)
                query_time = time.time() - start_time
                
                results[backend_name] = {
                    'success': True,
                    'query_time': round(query_time, 3),
                    'results_count': len(search_results),
                    'error': None
                }
                
            except Exception as e:
                results[backend_name] = {
                    'success': False,
                    'query_time': 0,
                    'results_count': 0,
                    'error': str(e)
                }
        
        return results
    
    def clear_cache(self) -> None:
        """Clear the query cache"""
        self.query_cache.clear()
        logger.info("Query cache cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all backends"""
        health_status = {
            'overall_status': 'healthy',
            'active_backend': type(self.active_backend).__name__ if self.active_backend else None,
            'backends': {}
        }
        
        for backend_name, backend in self.backends.items():
            try:
                stats = backend.get_stats()
                health_status['backends'][backend_name] = {
                    'status': 'healthy' if backend.is_ready else 'unhealthy',
                    'ready': backend.is_ready,
                    'document_count': stats.get('document_count', 0),
                    'error': stats.get('error')
                }
            except Exception as e:
                health_status['backends'][backend_name] = {
                    'status': 'error',
                    'ready': False,
                    'error': str(e)
                }
        
        # Check if any backend is healthy
        if not any(status['ready'] for status in health_status['backends'].values()):
            health_status['overall_status'] = 'unhealthy'
        
        return health_status


# Factory function
def create_vector_database_manager(config: Optional[Config] = None, 
                                  embedding_system: Optional[AdvancedEmbeddingSystem] = None) -> AdvancedVectorDatabaseManager:
    """Create advanced vector database manager"""
    return AdvancedVectorDatabaseManager(config, embedding_system)
