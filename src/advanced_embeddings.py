"""
Advanced Embedding Generation System for O-RAN × Nephio RAG
Multiple embedding models with fallback and ensemble capabilities
"""

import logging
import os
import pickle
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# Core dependencies
import numpy as np
from langchain.docstore.document import Document

# Multiple embedding backends
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import configuration
try:
    from .config import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingMetrics:
    """Metrics for embedding generation"""
    total_documents: int = 0
    total_chunks: int = 0
    embedding_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    failed_embeddings: int = 0
    average_vector_dimension: int = 0
    models_used: List[str] = None
    
    def __post_init__(self):
        if self.models_used is None:
            self.models_used = []


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    def __init__(self, model_name: str, config: Config):
        self.model_name = model_name
        self.config = config
        self.is_available = False
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        pass
    
    def initialize(self) -> bool:
        """Initialize the embedding provider"""
        try:
            # Test with a simple text
            test_embedding = self.embed_query("test")
            self.is_available = len(test_embedding) > 0
            return self.is_available
        except Exception as e:
            logger.error(f"Failed to initialize {self.model_name}: {e}")
            self.is_available = False
            return False


class SentenceTransformerProvider(EmbeddingProvider):
    """Sentence Transformers embedding provider"""
    
    def __init__(self, model_name: str, config: Config):
        super().__init__(model_name, config)
        self.model = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(
                    model_name, 
                    cache_folder=config.EMBEDDINGS_CACHE_PATH
                )
                logger.info(f"Initialized SentenceTransformer: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer {model_name}: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        if not self.model:
            raise RuntimeError("SentenceTransformer model not available")
        
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"SentenceTransformer embedding failed: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        if not self.model:
            raise RuntimeError("SentenceTransformer model not available")
        
        try:
            embedding = self.model.encode([text])[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"SentenceTransformer query embedding failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 384  # Default for most sentence transformer models


class TFIDFProvider(EmbeddingProvider):
    """TF-IDF based embedding provider (fallback)"""
    
    def __init__(self, model_name: str, config: Config, max_features: int = 5000):
        super().__init__(model_name, config)
        self.max_features = max_features
        self.vectorizer = None
        self.is_fitted = False
        
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate TF-IDF embeddings for documents"""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("sklearn not available for TF-IDF embeddings")
        
        try:
            if not self.is_fitted:
                # Fit the vectorizer on the provided texts
                self.vectorizer.fit(texts)
                self.is_fitted = True
                logger.info(f"TF-IDF vectorizer fitted on {len(texts)} documents")
            
            # Transform texts to TF-IDF vectors
            tfidf_matrix = self.vectorizer.transform(texts)
            dense_matrix = tfidf_matrix.toarray()
            
            return dense_matrix.tolist()
            
        except Exception as e:
            logger.error(f"TF-IDF embedding failed: {e}")
            # Fallback to simple feature vectors
            return [[float(len(text)), float(text.count(' ')), float(text.count('.'))] for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Generate TF-IDF embedding for a single query"""
        if not self.is_fitted:
            logger.warning("TF-IDF vectorizer not fitted, using simple features")
            return [float(len(text)), float(text.count(' ')), float(text.count('.'))]
        
        try:
            tfidf_vector = self.vectorizer.transform([text])
            return tfidf_vector.toarray()[0].tolist()
        except Exception as e:
            logger.error(f"TF-IDF query embedding failed: {e}")
            return [float(len(text)), float(text.count(' ')), float(text.count('.'))]
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self.is_fitted and self.vectorizer:
            return len(self.vectorizer.get_feature_names_out())
        return self.max_features


class EmbeddingCache:
    """Cache for embeddings to avoid recomputation"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.memory_cache = {}  # In-memory cache for session
        self.max_memory_items = 1000
    
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key for text and model"""
        combined = f"{model_name}:{text}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, text: str, model_name: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        cache_key = self._get_cache_key(text, model_name)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    embedding = pickle.load(f)
                
                # Add to memory cache if there's space
                if len(self.memory_cache) < self.max_memory_items:
                    self.memory_cache[cache_key] = embedding
                
                return embedding
            except Exception as e:
                logger.error(f"Failed to load embedding from cache: {e}")
        
        return None
    
    def put(self, text: str, model_name: str, embedding: List[float]) -> None:
        """Store embedding in cache"""
        cache_key = self._get_cache_key(text, model_name)
        
        # Store in memory cache
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest item
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[cache_key] = embedding
        
        # Store in disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.error(f"Failed to save embedding to cache: {e}")
    
    def clear(self) -> None:
        """Clear all caches"""
        self.memory_cache.clear()
        
        # Clear disk cache
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            logger.error(f"Failed to clear disk cache: {e}")


class AdvancedEmbeddingSystem:
    """Advanced embedding system with multiple providers and fallback"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.cache = EmbeddingCache(self.config.EMBEDDINGS_CACHE_PATH)
        
        # Initialize available providers
        self.providers = {}
        self._initialize_providers()
        
        # Embedding metrics
        self.metrics = EmbeddingMetrics()
        
        # Default provider order (best to worst)
        self.provider_priority = [
            'all-mpnet-base-v2',
            'all-MiniLM-L6-v2', 
            'multi-qa-MiniLM-L6-cos-v1',
            'tfidf'
        ]
        
        logger.info(f"Advanced embedding system initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self) -> None:
        """Initialize all available embedding providers"""
        # Sentence Transformer models
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            st_models = [
                'all-mpnet-base-v2',  # Best quality
                'all-MiniLM-L6-v2',   # Good balance
                'multi-qa-MiniLM-L6-cos-v1',  # Good for Q&A
            ]
            
            for model_name in st_models:
                try:
                    provider = SentenceTransformerProvider(model_name, self.config)
                    if provider.initialize():
                        self.providers[model_name] = provider
                        logger.info(f"SentenceTransformer provider '{model_name}' ready")
                except Exception as e:
                    logger.warning(f"Failed to initialize SentenceTransformer '{model_name}': {e}")
        
        # TF-IDF fallback
        if SKLEARN_AVAILABLE:
            try:
                tfidf_provider = TFIDFProvider('tfidf', self.config)
                if tfidf_provider.initialize():
                    self.providers['tfidf'] = tfidf_provider
                    logger.info("TF-IDF provider ready")
            except Exception as e:
                logger.warning(f"Failed to initialize TF-IDF provider: {e}")
        
        if not self.providers:
            logger.error("No embedding providers available!")
            raise RuntimeError("No embedding providers could be initialized")
    
    def get_best_provider(self) -> EmbeddingProvider:
        """Get the best available embedding provider"""
        for provider_name in self.provider_priority:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.is_available:
                    return provider
        
        # Return any available provider
        for provider in self.providers.values():
            if provider.is_available:
                return provider
        
        raise RuntimeError("No embedding providers available")
    
    async def embed_documents_async(self, documents: List[Document], 
                                  provider_name: Optional[str] = None) -> List[List[float]]:
        """Asynchronously generate embeddings for documents"""
        start_time = time.time()
        
        # Select provider
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        else:
            provider = self.get_best_provider()
        
        logger.info(f"Generating embeddings for {len(documents)} documents using {provider.model_name}")
        
        # Extract texts from documents
        texts = [doc.page_content for doc in documents]
        
        # Process in batches to avoid memory issues
        batch_size = 50  # Adjust based on memory constraints
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Check cache for each text
            batch_embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for j, text in enumerate(batch_texts):
                cached_embedding = self.cache.get(text, provider.model_name)
                if cached_embedding:
                    batch_embeddings.append(cached_embedding)
                    self.metrics.cache_hits += 1
                else:
                    batch_embeddings.append(None)  # Placeholder
                    uncached_texts.append(text)
                    uncached_indices.append(j)
                    self.metrics.cache_misses += 1
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                try:
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        loop = asyncio.get_event_loop()
                        new_embeddings = await loop.run_in_executor(
                            executor, provider.embed_documents, uncached_texts
                        )
                    
                    # Fill in the placeholders and cache new embeddings
                    for idx, embedding in zip(uncached_indices, new_embeddings):
                        batch_embeddings[idx] = embedding
                        self.cache.put(batch_texts[idx], provider.model_name, embedding)
                
                except Exception as e:
                    logger.error(f"Batch embedding failed: {e}")
                    self.metrics.failed_embeddings += len(uncached_texts)
                    
                    # Fill with fallback embeddings
                    for idx in uncached_indices:
                        fallback_embedding = self._generate_fallback_embedding(batch_texts[idx])
                        batch_embeddings[idx] = fallback_embedding
            
            all_embeddings.extend(batch_embeddings)
        
        # Update metrics
        self.metrics.total_documents += len(documents)
        self.metrics.total_chunks += len(documents)
        self.metrics.embedding_time += time.time() - start_time
        self.metrics.average_vector_dimension = provider.get_dimension()
        if provider.model_name not in self.metrics.models_used:
            self.metrics.models_used.append(provider.model_name)
        
        logger.info(f"Generated {len(all_embeddings)} embeddings in {time.time() - start_time:.2f}s")
        
        return all_embeddings
    
    def embed_documents(self, documents: List[Document], 
                       provider_name: Optional[str] = None) -> List[List[float]]:
        """Synchronous wrapper for embedding documents"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.embed_documents_async(documents, provider_name)
            )
        finally:
            loop.close()
    
    def embed_query(self, query: str, provider_name: Optional[str] = None) -> List[float]:
        """Generate embedding for a single query"""
        # Select provider
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        else:
            provider = self.get_best_provider()
        
        # Check cache
        cached_embedding = self.cache.get(query, provider.model_name)
        if cached_embedding:
            self.metrics.cache_hits += 1
            return cached_embedding
        
        # Generate new embedding
        try:
            embedding = provider.embed_query(query)
            self.cache.put(query, provider.model_name, embedding)
            self.metrics.cache_misses += 1
            return embedding
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            self.metrics.failed_embeddings += 1
            return self._generate_fallback_embedding(query)
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generate simple fallback embedding"""
        # Very basic features as fallback
        features = [
            float(len(text)),
            float(text.count(' ')),
            float(text.count('.')),
            float(text.count('?')),
            float(text.count('!')),
            float(text.lower().count('nephio')),
            float(text.lower().count('oran')),
            float(text.lower().count('kubernetes'))
        ]
        
        # Pad to match expected dimension
        expected_dim = 384  # Common dimension
        while len(features) < expected_dim:
            features.append(0.0)
        
        return features[:expected_dim]
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [name for name, provider in self.providers.items() if provider.is_available]
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific provider"""
        if provider_name not in self.providers:
            return None
        
        provider = self.providers[provider_name]
        return {
            'name': provider.model_name,
            'dimension': provider.get_dimension(),
            'available': provider.is_available,
            'type': type(provider).__name__
        }
    
    def get_embedding_metrics(self) -> Dict[str, Any]:
        """Get embedding generation metrics"""
        total_requests = self.metrics.cache_hits + self.metrics.cache_misses
        cache_hit_rate = (self.metrics.cache_hits / max(total_requests, 1)) * 100
        
        return {
            'total_documents': self.metrics.total_documents,
            'total_chunks': self.metrics.total_chunks,
            'embedding_time': round(self.metrics.embedding_time, 2),
            'cache_hits': self.metrics.cache_hits,
            'cache_misses': self.metrics.cache_misses,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'failed_embeddings': self.metrics.failed_embeddings,
            'average_vector_dimension': self.metrics.average_vector_dimension,
            'models_used': self.metrics.models_used.copy(),
            'available_providers': self.get_available_providers()
        }
    
    def benchmark_providers(self, test_texts: List[str]) -> Dict[str, Dict[str, Any]]:
        """Benchmark different embedding providers"""
        results = {}
        
        for provider_name, provider in self.providers.items():
            if not provider.is_available:
                continue
            
            logger.info(f"Benchmarking provider: {provider_name}")
            
            start_time = time.time()
            try:
                embeddings = provider.embed_documents(test_texts)
                end_time = time.time()
                
                results[provider_name] = {
                    'success': True,
                    'time_taken': end_time - start_time,
                    'texts_per_second': len(test_texts) / (end_time - start_time),
                    'dimension': len(embeddings[0]) if embeddings else 0,
                    'error': None
                }
            except Exception as e:
                results[provider_name] = {
                    'success': False,
                    'time_taken': 0,
                    'texts_per_second': 0,
                    'dimension': 0,
                    'error': str(e)
                }
        
        return results


# Factory function
def create_advanced_embedding_system(config: Optional[Config] = None) -> AdvancedEmbeddingSystem:
    """Create advanced embedding system"""
    return AdvancedEmbeddingSystem(config)
