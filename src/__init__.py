"""
O-RAN × Nephio RAG 系統

一個基於檢索增強生成 (RAG) 技術的智能問答系統，
專門針對 O-RAN 和 Nephio 技術文檔設計。

主要功能：
- 自動抓取和處理官方文檔
- 智能語義搜索
- AI 驅動的問答系統
- 異步處理支持
- 完整的監控和可觀察性

版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Development Team"
__email__ = "dev-team@company.com"

# 主要類別導入
from .config import Config, DocumentSource, validate_config
from .document_loader import DocumentLoader, DocumentContentCleaner
from .oran_nephio_rag import ORANNephioRAG, VectorDatabaseManager, QueryProcessor, create_rag_system, quick_query

# 異步組件導入
try:
    from .async_rag_system import AsyncORANNephioRAG, AsyncDocumentLoader, AsyncQueryProcessor, async_rag_system
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

# 監控組件導入
try:
    from .monitoring import RAGSystemMetrics, HealthChecker, AlertManager, get_metrics, setup_monitoring
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

__all__ = [
    # 核心類別
    "Config",
    "DocumentSource", 
    "DocumentLoader",
    "DocumentContentCleaner",
    "ORANNephioRAG",
    "VectorDatabaseManager",
    "QueryProcessor",
    
    # 工廠函數
    "create_rag_system",
    "quick_query",
    "validate_config",
    
    # 元資訊
    "__version__",
    "__author__",
    "__email__",
    "ASYNC_AVAILABLE",
    "MONITORING_AVAILABLE",
]

# 異步組件（如果可用）
if ASYNC_AVAILABLE:
    __all__.extend([
        "AsyncORANNephioRAG",
        "AsyncDocumentLoader", 
        "AsyncQueryProcessor",
        "async_rag_system",
    ])

# 監控組件（如果可用）
if MONITORING_AVAILABLE:
    __all__.extend([
        "RAGSystemMetrics",
        "HealthChecker",
        "AlertManager", 
        "get_metrics",
        "setup_monitoring",
    ])

def get_system_info():
    """取得系統資訊"""
    return {
        "version": __version__,
        "author": __author__,
        "async_available": ASYNC_AVAILABLE,
        "monitoring_available": MONITORING_AVAILABLE,
    }