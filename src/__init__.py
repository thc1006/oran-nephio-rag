"""
O-RAN × Nephio RAG System - Enhanced Core Components
Comprehensive RAG system with advanced O-RAN/Nephio optimization
"""

# Import enhanced core components
try:
    from .enhanced_rag_system import (
        EnhancedRAGSystem,
        create_enhanced_rag_system,
        quick_rag_query
    )
    ENHANCED_RAG_AVAILABLE = True
except ImportError:
    ENHANCED_RAG_AVAILABLE = False

# Import individual components for advanced usage
try:
    from .document_preprocessor import (
        EnhancedDocumentPreprocessor,
        TelecomTermExtractor,
        CodeBlockExtractor,
        DiagramDetector
    )
    PREPROCESSOR_AVAILABLE = True
except ImportError:
    PREPROCESSOR_AVAILABLE = False

try:
    from .smart_chunking import (
        SmartChunkingSystem,
        SemanticChunker,
        StructuralChunker,
        HybridChunker
    )
    SMART_CHUNKING_AVAILABLE = True
except ImportError:
    SMART_CHUNKING_AVAILABLE = False

try:
    from .advanced_embeddings import (
        AdvancedEmbeddingSystem,
        SentenceTransformerProvider,
        TFIDFProvider
    )
    ADVANCED_EMBEDDINGS_AVAILABLE = True
except ImportError:
    ADVANCED_EMBEDDINGS_AVAILABLE = False

try:
    from .vector_database_manager import (
        AdvancedVectorDatabaseManager,
        ChromaBackend,
        PineconeBackend
    )
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False

try:
    from .retrieval_engine import (
        AdvancedRetrievalEngine,
        QueryType,
        QueryAnalyzer,
        DocumentRanker
    )
    RETRIEVAL_ENGINE_AVAILABLE = True
except ImportError:
    RETRIEVAL_ENGINE_AVAILABLE = False

try:
    from .enhanced_llm_integration import (
        EnhancedLLMManager,
        ResponseType,
        PromptTemplateManager,
        ContextOptimizer
    )
    LLM_INTEGRATION_AVAILABLE = True
except ImportError:
    LLM_INTEGRATION_AVAILABLE = False

try:
    from .performance_monitor import (
        PerformanceMonitoringSystem,
        performance_monitor,
        get_global_monitor,
        start_global_monitoring,
        stop_global_monitoring
    )
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

# Import existing components for backward compatibility
from .config import Config, DocumentSource, validate_config
from .document_loader import DocumentContentCleaner, DocumentLoader

# RAG 系統導入 (條件性導入以支援測試)
try:
    from .oran_nephio_rag import ORANNephioRAG, QueryProcessor, VectorDatabaseManager, create_rag_system, quick_query
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False

try:
    from .puter_integration import PuterRAGManager, create_puter_rag_manager
    PUTER_AVAILABLE = True
except ImportError:
    PUTER_AVAILABLE = False

# Version information
__version__ = "2.0.0-enhanced"
__author__ = "O-RAN × Nephio RAG Team"
__description__ = "Enhanced RAG system optimized for O-RAN and Nephio documentation"

# Public API
__all__ = [
    # Configuration and utilities
    'Config',
    'DocumentSource',
    'validate_config',
    'DocumentLoader',
    'DocumentContentCleaner',

    # Version info
    '__version__',
    '__author__',
    '__description__',

    # Availability flags
    'ENHANCED_RAG_AVAILABLE',
    'PREPROCESSOR_AVAILABLE',
    'SMART_CHUNKING_AVAILABLE',
    'ADVANCED_EMBEDDINGS_AVAILABLE',
    'VECTOR_DB_AVAILABLE',
    'RETRIEVAL_ENGINE_AVAILABLE',
    'LLM_INTEGRATION_AVAILABLE',
    'MONITORING_AVAILABLE',
    'RAG_AVAILABLE',
    'PUTER_AVAILABLE'
]

# Add enhanced components if available
if ENHANCED_RAG_AVAILABLE:
    __all__.extend([
        'EnhancedRAGSystem',
        'create_enhanced_rag_system',
        'quick_rag_query'
    ])

if PREPROCESSOR_AVAILABLE:
    __all__.extend([
        'EnhancedDocumentPreprocessor',
        'TelecomTermExtractor',
        'CodeBlockExtractor',
        'DiagramDetector'
    ])

if SMART_CHUNKING_AVAILABLE:
    __all__.extend([
        'SmartChunkingSystem',
        'SemanticChunker',
        'StructuralChunker',
        'HybridChunker'
    ])

if ADVANCED_EMBEDDINGS_AVAILABLE:
    __all__.extend([
        'AdvancedEmbeddingSystem',
        'SentenceTransformerProvider',
        'TFIDFProvider'
    ])

if VECTOR_DB_AVAILABLE:
    __all__.extend([
        'AdvancedVectorDatabaseManager',
        'ChromaBackend',
        'PineconeBackend'
    ])

if RETRIEVAL_ENGINE_AVAILABLE:
    __all__.extend([
        'AdvancedRetrievalEngine',
        'QueryType',
        'QueryAnalyzer',
        'DocumentRanker'
    ])

if LLM_INTEGRATION_AVAILABLE:
    __all__.extend([
        'EnhancedLLMManager',
        'ResponseType',
        'PromptTemplateManager',
        'ContextOptimizer'
    ])

if MONITORING_AVAILABLE:
    __all__.extend([
        'PerformanceMonitoringSystem',
        'performance_monitor',
        'get_global_monitor',
        'start_global_monitoring',
        'stop_global_monitoring'
    ])

if RAG_AVAILABLE:
    __all__.extend([
        'ORANNephioRAG',
        'QueryProcessor',
        'VectorDatabaseManager',
        'create_rag_system',
        'quick_query'
    ])

if PUTER_AVAILABLE:
    __all__.extend([
        'PuterRAGManager',
        'create_puter_rag_manager'
    ])


def get_system_info() -> dict:
    """Get system information and capabilities"""
    info = {
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'enhanced_capabilities': {
            'enhanced_rag_system': ENHANCED_RAG_AVAILABLE,
            'document_preprocessing': PREPROCESSOR_AVAILABLE,
            'smart_chunking': SMART_CHUNKING_AVAILABLE,
            'advanced_embeddings': ADVANCED_EMBEDDINGS_AVAILABLE,
            'vector_database_manager': VECTOR_DB_AVAILABLE,
            'retrieval_engine': RETRIEVAL_ENGINE_AVAILABLE,
            'llm_integration': LLM_INTEGRATION_AVAILABLE,
            'performance_monitoring': MONITORING_AVAILABLE
        },
        'legacy_compatibility': {
            'basic_rag_system': RAG_AVAILABLE,
            'puter_integration': PUTER_AVAILABLE
        }
    }

    if RETRIEVAL_ENGINE_AVAILABLE and LLM_INTEGRATION_AVAILABLE:
        try:
            info['supported_query_types'] = [qt.value for qt in QueryType]
            info['supported_response_types'] = [rt.value for rt in ResponseType]
        except:
            pass

    return info


def create_optimized_system(config_overrides: dict = None):
    """Create an optimized RAG system with recommended settings"""
    if not ENHANCED_RAG_AVAILABLE:
        raise ImportError("Enhanced RAG system not available. Install required dependencies.")

    # Load default config
    config = Config()

    # Apply overrides if provided
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)

    # Create enhanced system
    rag_system = create_enhanced_rag_system(config)

    # Start performance monitoring if available
    if MONITORING_AVAILABLE:
        monitor = get_global_monitor()
        if not monitor.is_monitoring:
            monitor.start_monitoring()

    return rag_system


# Convenience imports for quick access (if available)
if ENHANCED_RAG_AVAILABLE:
    try:
        from .enhanced_rag_system import EnhancedRAGSystem as RAGSystem
    except ImportError:
        pass

if RETRIEVAL_ENGINE_AVAILABLE:
    try:
        from .retrieval_engine import QueryType
    except ImportError:
        pass

if LLM_INTEGRATION_AVAILABLE:
    try:
        from .enhanced_llm_integration import ResponseType
    except ImportError:
        pass
