"""
Advanced Retrieval Engine for O-RAN × Nephio RAG
Semantic search with ranking, filtering, and query optimization
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import time
import math

from langchain.docstore.document import Document

# Import dependencies
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Import configuration and components
try:
    from .config import Config
    from .vector_database_manager import AdvancedVectorDatabaseManager
    from .advanced_embeddings import AdvancedEmbeddingSystem
except ImportError:
    from config import Config
    from vector_database_manager import AdvancedVectorDatabaseManager
    from advanced_embeddings import AdvancedEmbeddingSystem

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries for specialized handling"""
    GENERAL = "general"
    TECHNICAL = "technical"
    CODE_RELATED = "code_related"
    ARCHITECTURE = "architecture"
    DEPLOYMENT = "deployment"
    TROUBLESHOOTING = "troubleshooting"
    COMPARISON = "comparison"
    HOW_TO = "how_to"


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval operations"""
    total_queries: int = 0
    total_retrieval_time: float = 0.0
    average_retrieval_time: float = 0.0
    documents_retrieved: int = 0
    rerank_operations: int = 0
    filter_operations: int = 0
    query_expansions: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


@dataclass
class RetrievalResult:
    """Structured retrieval result"""
    documents: List[Document]
    scores: List[float]
    query_type: QueryType
    total_candidates: int
    filtered_count: int
    reranked: bool
    retrieval_time: float
    metadata: Dict[str, Any]


class QueryAnalyzer:
    """Analyzes queries to determine type and extract key information"""
    
    def __init__(self):
        # Query type patterns
        self.query_patterns = {
            QueryType.CODE_RELATED: [
                r'\b(code|implementation|script|command|kubectl|yaml|json|api)\b',
                r'\b(function|class|method|variable|configuration)\b',
                r'\b(example|snippet|syntax)\b'
            ],
            QueryType.ARCHITECTURE: [
                r'\b(architecture|design|structure|component|module)\b',
                r'\b(diagram|topology|pattern|framework)\b',
                r'\b(overview|high-level|system)\b'
            ],
            QueryType.DEPLOYMENT: [
                r'\b(deploy|deployment|install|setup|configure)\b',
                r'\b(cluster|kubernetes|helm|manifest)\b',
                r'\b(provision|scale|orchestrat)\b'
            ],
            QueryType.TROUBLESHOOTING: [
                r'\b(error|issue|problem|debug|troubleshoot|fix)\b',
                r'\b(fail|crash|not working|broken)\b',
                r'\b(logs|monitoring|alert)\b'
            ],
            QueryType.COMPARISON: [
                r'\b(vs|versus|compare|comparison|difference|better)\b',
                r'\b(alternative|option|choice)\b',
                r'\b(pros|cons|advantage|disadvantage)\b'
            ],
            QueryType.HOW_TO: [
                r'\b(how to|how do|step|guide|tutorial|process)\b',
                r'\b(procedure|instruction|workflow)\b'
            ],
            QueryType.TECHNICAL: [
                r'\b(o-ran|oran|nephio|kubernetes|gitops)\b',
                r'\b(cnf|vnf|nf|network function|workload)\b',
                r'\b(porch|kpt|controller|operator)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for query_type, patterns in self.query_patterns.items():
            self.compiled_patterns[query_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        
        # O-RAN/Nephio specific terms for boosting
        self.domain_terms = {
            'oran': ['o-ran', 'oran', 'o-cu', 'o-du', 'o-ru', 'ric', 'smo', 'xapp', 'rapp'],
            'nephio': ['nephio', 'porch', 'gitops', 'kpt', 'package', 'workload'],
            'kubernetes': ['kubernetes', 'k8s', 'pod', 'deployment', 'service', 'configmap'],
            'networking': ['network', 'function', 'cnf', 'vnf', 'nf', 'slice', 'edge']
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to extract type and key information"""
        query_lower = query.lower()
        
        # Determine query type
        query_type = self._classify_query_type(query)
        
        # Extract domain terms
        found_terms = self._extract_domain_terms(query_lower)
        
        # Extract intent signals
        intent_signals = self._extract_intent_signals(query_lower)
        
        # Generate expansion terms
        expansion_terms = self._generate_expansion_terms(query, found_terms)
        
        return {
            'original_query': query,
            'query_type': query_type,
            'domain_terms': found_terms,
            'intent_signals': intent_signals,
            'expansion_terms': expansion_terms,
            'boost_factors': self._calculate_boost_factors(found_terms, query_type),
            'query_complexity': self._assess_complexity(query)
        }
    
    def _classify_query_type(self, query: str) -> QueryType:
        """Classify the query type based on patterns"""
        scores = {}
        
        for query_type, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(query))
                score += matches
            scores[query_type] = score
        
        # Return the type with the highest score, default to GENERAL
        if scores:
            max_type = max(scores, key=scores.get)
            if scores[max_type] > 0:
                return max_type
        
        return QueryType.GENERAL
    
    def _extract_domain_terms(self, query: str) -> Dict[str, List[str]]:
        """Extract domain-specific terms from query"""
        found_terms = {domain: [] for domain in self.domain_terms}
        
        for domain, terms in self.domain_terms.items():
            for term in terms:
                if term in query:
                    found_terms[domain].append(term)
        
        return {k: v for k, v in found_terms.items() if v}  # Remove empty lists
    
    def _extract_intent_signals(self, query: str) -> List[str]:
        """Extract intent signals from query"""
        intent_signals = []
        
        # Question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        for word in question_words:
            if word in query:
                intent_signals.append(f'question_{word}')
        
        # Action words
        action_words = ['deploy', 'configure', 'install', 'setup', 'scale', 'monitor']
        for word in action_words:
            if word in query:
                intent_signals.append(f'action_{word}')
        
        return intent_signals
    
    def _generate_expansion_terms(self, query: str, found_terms: Dict[str, List[str]]) -> List[str]:
        """Generate query expansion terms"""
        expansion_terms = []
        
        # Add synonyms for found domain terms
        synonyms = {
            'oran': ['open-ran', 'disaggregated-ran'],
            'nephio': ['network-automation', 'cloud-native-automation'],
            'kubernetes': ['k8s', 'container-orchestration'],
            'deployment': ['provisioning', 'installation'],
            'scaling': ['autoscaling', 'horizontal-scaling', 'vertical-scaling']
        }
        
        query_lower = query.lower()
        for term, synonyms_list in synonyms.items():
            if term in query_lower:
                expansion_terms.extend(synonyms_list)
        
        return expansion_terms
    
    def _calculate_boost_factors(self, found_terms: Dict[str, List[str]], 
                                query_type: QueryType) -> Dict[str, float]:
        """Calculate boost factors for different document types"""
        boost_factors = {}
        
        # Base boost for query type
        type_boosts = {
            QueryType.CODE_RELATED: {'code_blocks_count': 2.0, 'kubernetes_yaml': 2.5},
            QueryType.ARCHITECTURE: {'diagrams_count': 2.0, 'relevance_score': 1.5},
            QueryType.DEPLOYMENT: {'kubectl_commands': 2.0, 'helm_command': 1.8},
            QueryType.TECHNICAL: {'total_technical_terms': 1.5}
        }
        
        if query_type in type_boosts:
            boost_factors.update(type_boosts[query_type])
        
        # Domain-specific boosts
        if found_terms.get('oran'):
            boost_factors['oran_terms_count'] = 2.0
        if found_terms.get('nephio'):
            boost_factors['nephio_terms_count'] = 2.0
        if found_terms.get('kubernetes'):
            boost_factors['k8s_terms_count'] = 1.5
        
        return boost_factors
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity"""
        words = query.split()
        
        if len(words) <= 3:
            return 'simple'
        elif len(words) <= 8:
            return 'medium'
        else:
            return 'complex'


class DocumentRanker:
    """Advanced document ranking with multiple signals"""
    
    def __init__(self):
        pass
    
    def rerank_documents(self, documents: List[Tuple[Document, float]], 
                        query_analysis: Dict[str, Any]) -> List[Tuple[Document, float]]:
        """Rerank documents based on multiple signals"""
        if not documents:
            return documents
        
        # Calculate additional ranking signals
        enhanced_scores = []
        
        for doc, similarity_score in documents:
            # Start with similarity score
            final_score = similarity_score
            
            # Apply boost factors from query analysis
            boost_factors = query_analysis.get('boost_factors', {})
            metadata = doc.metadata
            
            for boost_key, boost_value in boost_factors.items():
                if boost_key in metadata:
                    metadata_value = metadata[boost_key]
                    if isinstance(metadata_value, (int, float)) and metadata_value > 0:
                        # Apply logarithmic boost to prevent extreme values
                        boost = math.log(1 + metadata_value) * boost_value * 0.1
                        final_score += boost
            
            # Content quality signals
            content_score = self._calculate_content_score(doc, query_analysis)
            final_score += content_score * 0.2
            
            # Recency boost (if available)
            if 'last_updated' in metadata:
                try:
                    # Simple recency boost (this could be more sophisticated)
                    recency_boost = 0.05  # Small boost for recently updated content
                    final_score += recency_boost
                except:
                    pass
            
            enhanced_scores.append((doc, final_score))
        
        # Sort by enhanced score
        enhanced_scores.sort(key=lambda x: x[1], reverse=True)
        
        return enhanced_scores
    
    def _calculate_content_score(self, document: Document, 
                                query_analysis: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        content = document.page_content
        metadata = document.metadata
        score = 0.0
        
        # Content length score (prefer substantial content)
        content_length = len(content)
        if 500 <= content_length <= 3000:  # Sweet spot
            score += 0.3
        elif content_length > 3000:
            score += 0.1
        
        # Technical density score
        technical_terms = sum(metadata.get(f'{domain}_terms_count', 0) 
                            for domain in ['oran', 'nephio', 'k8s', 'telecom'])
        if technical_terms > 0:
            score += min(technical_terms * 0.05, 0.5)  # Cap at 0.5
        
        # Code presence score for code-related queries
        if query_analysis.get('query_type') == QueryType.CODE_RELATED:
            code_blocks = metadata.get('code_blocks_count', 0)
            if code_blocks > 0:
                score += min(code_blocks * 0.1, 0.4)
        
        # Structural score (prefer well-structured content)
        if metadata.get('chunk_type') in ['heading_section', 'semantic']:
            score += 0.2
        
        return score


class AdvancedRetrievalEngine:
    """Advanced retrieval engine with semantic search and ranking"""
    
    def __init__(self, config: Optional[Config] = None,
                 vector_db_manager: Optional[AdvancedVectorDatabaseManager] = None,
                 embedding_system: Optional[AdvancedEmbeddingSystem] = None):
        self.config = config or Config()
        self.vector_db_manager = vector_db_manager or AdvancedVectorDatabaseManager(self.config)
        self.embedding_system = embedding_system or AdvancedEmbeddingSystem(self.config)
        
        # Initialize components
        self.query_analyzer = QueryAnalyzer()
        self.document_ranker = DocumentRanker()
        
        # Retrieval metrics
        self.metrics = RetrievalMetrics()
        
        # Query cache
        self.query_cache = {}
        self.max_cache_size = 200
        
        logger.info("Advanced retrieval engine initialized")
    
    def retrieve(self, query: str, k: int = None, 
                filters: Optional[Dict[str, Any]] = None,
                rerank: bool = True,
                use_cache: bool = True) -> RetrievalResult:
        """Advanced document retrieval with analysis and ranking"""
        start_time = time.time()
        
        # Use config default if k not specified
        k = k or self.config.RETRIEVER_K
        
        # Create cache key
        cache_key = f"{query}:{k}:{filters}:{rerank}"
        
        # Check cache
        if use_cache and cache_key in self.query_cache:
            self.metrics.cache_hits += 1
            cached_result = self.query_cache[cache_key]
            cached_result.retrieval_time = time.time() - start_time  # Update time
            return cached_result
        
        self.metrics.cache_misses += 1
        
        # Analyze query
        query_analysis = self.query_analyzer.analyze_query(query)
        logger.debug(f"Query analysis: {query_analysis['query_type']}, "
                    f"Domain terms: {query_analysis['domain_terms']}")
        
        # Expand query if beneficial
        expanded_query = self._expand_query(query, query_analysis)
        
        # Retrieve candidates
        candidates = self._retrieve_candidates(expanded_query, k * 2)  # Get more candidates for reranking
        
        # Apply filters
        filtered_candidates = self._apply_filters(candidates, filters, query_analysis)
        
        # Rerank if requested
        if rerank and len(filtered_candidates) > 1:
            reranked_docs = self.document_ranker.rerank_documents(filtered_candidates, query_analysis)
            self.metrics.rerank_operations += 1
        else:
            reranked_docs = filtered_candidates
        
        # Select top k results
        final_docs = reranked_docs[:k]
        
        # Create result
        result = RetrievalResult(
            documents=[doc for doc, _ in final_docs],
            scores=[score for _, score in final_docs],
            query_type=query_analysis['query_type'],
            total_candidates=len(candidates),
            filtered_count=len(filtered_candidates),
            reranked=rerank,
            retrieval_time=time.time() - start_time,
            metadata={
                'query_analysis': query_analysis,
                'expanded_query': expanded_query,
                'filters_applied': filters is not None
            }
        )
        
        # Cache result
        if use_cache:
            if len(self.query_cache) >= self.max_cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.query_cache))
                del self.query_cache[oldest_key]
            self.query_cache[cache_key] = result
        
        # Update metrics
        self.metrics.total_queries += 1
        self.metrics.total_retrieval_time += result.retrieval_time
        self.metrics.average_retrieval_time = self.metrics.total_retrieval_time / self.metrics.total_queries
        self.metrics.documents_retrieved += len(final_docs)
        
        if filters:
            self.metrics.filter_operations += 1
        
        if expanded_query != query:
            self.metrics.query_expansions += 1
        
        logger.debug(f"Retrieved {len(final_docs)} documents in {result.retrieval_time:.3f}s")
        
        return result
    
    def _expand_query(self, query: str, query_analysis: Dict[str, Any]) -> str:
        """Expand query with additional terms if beneficial"""
        expansion_terms = query_analysis.get('expansion_terms', [])
        
        if not expansion_terms:
            return query
        
        # Only expand for complex queries or when domain terms are present
        if (query_analysis.get('query_complexity') in ['medium', 'complex'] or 
            query_analysis.get('domain_terms')):
            
            # Add top expansion terms
            top_expansions = expansion_terms[:3]  # Limit to avoid over-expansion
            expanded = f"{query} {' '.join(top_expansions)}"
            logger.debug(f"Expanded query: {query} -> {expanded}")
            return expanded
        
        return query
    
    def _retrieve_candidates(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Retrieve candidate documents from vector database"""
        try:
            return self.vector_db_manager.search_similar(query, k=k)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _apply_filters(self, documents: List[Tuple[Document, float]], 
                      filters: Optional[Dict[str, Any]], 
                      query_analysis: Dict[str, Any]) -> List[Tuple[Document, float]]:
        """Apply filters to candidate documents"""
        if not filters and not query_analysis.get('domain_terms'):
            return documents
        
        filtered_docs = []
        
        for doc, score in documents:
            metadata = doc.metadata
            
            # Apply explicit filters
            if filters:
                if not self._document_matches_filters(metadata, filters):
                    continue
            
            # Apply query-type specific filters
            query_type = query_analysis.get('query_type')
            if query_type == QueryType.CODE_RELATED:
                # Prefer documents with code blocks
                if metadata.get('code_blocks_count', 0) == 0:
                    score *= 0.7  # Reduce score but don't eliminate
            
            elif query_type == QueryType.ARCHITECTURE:
                # Prefer documents with diagrams or high-level content
                if metadata.get('diagrams_count', 0) > 0:
                    score *= 1.2
            
            # Domain term filtering
            domain_terms = query_analysis.get('domain_terms', {})
            if domain_terms:
                domain_match = False
                for domain in domain_terms.keys():
                    if metadata.get(f'{domain}_terms_count', 0) > 0:
                        domain_match = True
                        break
                
                if not domain_match:
                    score *= 0.5  # Reduce score for documents without domain terms
            
            filtered_docs.append((doc, score))
        
        return filtered_docs
    
    def _document_matches_filters(self, metadata: Dict[str, Any], 
                                 filters: Dict[str, Any]) -> bool:
        """Check if document metadata matches filters"""
        for filter_key, filter_value in filters.items():
            if filter_key not in metadata:
                return False
            
            metadata_value = metadata[filter_key]
            
            if isinstance(filter_value, list):
                if metadata_value not in filter_value:
                    return False
            elif isinstance(filter_value, dict):
                # Range filters like {'min': 5, 'max': 20}
                if 'min' in filter_value and metadata_value < filter_value['min']:
                    return False
                if 'max' in filter_value and metadata_value > filter_value['max']:
                    return False
            else:
                if metadata_value != filter_value:
                    return False
        
        return True
    
    def get_retrieval_metrics(self) -> Dict[str, Any]:
        """Get retrieval engine metrics"""
        cache_total = self.metrics.cache_hits + self.metrics.cache_misses
        cache_hit_rate = (self.metrics.cache_hits / max(cache_total, 1)) * 100
        
        return {
            'total_queries': self.metrics.total_queries,
            'total_retrieval_time': round(self.metrics.total_retrieval_time, 3),
            'average_retrieval_time': round(self.metrics.average_retrieval_time, 3),
            'documents_retrieved': self.metrics.documents_retrieved,
            'average_docs_per_query': round(self.metrics.documents_retrieved / max(self.metrics.total_queries, 1), 2),
            'rerank_operations': self.metrics.rerank_operations,
            'filter_operations': self.metrics.filter_operations,
            'query_expansions': self.metrics.query_expansions,
            'cache_hits': self.metrics.cache_hits,
            'cache_misses': self.metrics.cache_misses,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_size': len(self.query_cache)
        }
    
    def clear_cache(self) -> None:
        """Clear the retrieval cache"""
        self.query_cache.clear()
        logger.info("Retrieval cache cleared")
    
    def benchmark_retrieval(self, test_queries: List[str], k: int = 5) -> Dict[str, Any]:
        """Benchmark retrieval performance"""
        start_time = time.time()
        total_docs = 0
        query_times = []
        
        for query in test_queries:
            query_start = time.time()
            result = self.retrieve(query, k=k, use_cache=False)
            query_time = time.time() - query_start
            
            query_times.append(query_time)
            total_docs += len(result.documents)
        
        total_time = time.time() - start_time
        
        return {
            'total_queries': len(test_queries),
            'total_time': round(total_time, 3),
            'average_query_time': round(sum(query_times) / len(query_times), 3),
            'queries_per_second': round(len(test_queries) / total_time, 2),
            'total_documents_retrieved': total_docs,
            'average_docs_per_query': round(total_docs / len(test_queries), 2),
            'fastest_query': round(min(query_times), 3),
            'slowest_query': round(max(query_times), 3)
        }


# Factory function
def create_retrieval_engine(config: Optional[Config] = None,
                           vector_db_manager: Optional[AdvancedVectorDatabaseManager] = None,
                           embedding_system: Optional[AdvancedEmbeddingSystem] = None) -> AdvancedRetrievalEngine:
    """Create advanced retrieval engine"""
    return AdvancedRetrievalEngine(config, vector_db_manager, embedding_system)
