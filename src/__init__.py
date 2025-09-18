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
__author__ = "Tsai, Hsiu-Chi (thc1006)"
__email__ = "hctsai@linux.com"

# 主要類別導入
from .config import Config, DocumentSource, validate_config
from .document_loader import DocumentContentCleaner, DocumentLoader

# RAG 系統導入 (條件性導入以支援測試)
try:
    from .oran_nephio_rag import ORANNephioRAG, QueryProcessor, VectorDatabaseManager, create_rag_system, quick_query

    RAG_AVAILABLE = True
except ImportError as e:
    # 在測試環境中，如果依賴項目不可用，使用模擬版本
    RAG_AVAILABLE = False
    import logging

    logging.getLogger(__name__).warning(f"RAG system not available: {e}")

# 異步組件導入
try:
    from .async_rag_system import AsyncDocumentLoader, AsyncORANNephioRAG, AsyncQueryProcessor, async_rag_system

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

# 監控組件導入
try:
    from .monitoring import AlertManager, HealthChecker, RAGSystemMetrics, get_metrics, setup_monitoring

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

__all__ = [
    # 核心類別
    "Config",
    "DocumentSource",
    "DocumentLoader",
    "DocumentContentCleaner",
    # 工廠函數
    "validate_config",
    # 元資訊
    "__version__",
    "__author__",
    "__email__",
    "RAG_AVAILABLE",
    "ASYNC_AVAILABLE",
    "MONITORING_AVAILABLE",
]

# RAG 系統組件（如果可用）
if RAG_AVAILABLE:
    __all__.extend(
        [
            "ORANNephioRAG",
            "VectorDatabaseManager",
            "QueryProcessor",
            "create_rag_system",
            "quick_query",
        ]
    )

# 異步組件（如果可用）
if ASYNC_AVAILABLE:
    __all__.extend(
        [
            "AsyncORANNephioRAG",
            "AsyncDocumentLoader",
            "AsyncQueryProcessor",
            "async_rag_system",
        ]
    )

# 監控組件（如果可用）
if MONITORING_AVAILABLE:
    __all__.extend(
        [
            "RAGSystemMetrics",
            "HealthChecker",
            "AlertManager",
            "get_metrics",
            "setup_monitoring",
        ]
    )


def get_system_info():
    """取得系統資訊"""
    return {
        "version": __version__,
        "author": __author__,
        "rag_available": RAG_AVAILABLE,
        "async_available": ASYNC_AVAILABLE,
        "monitoring_available": MONITORING_AVAILABLE,
    }
