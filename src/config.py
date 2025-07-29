"""
O-RAN × Nephio RAG 系統配置管理模組
"""
import os
import logging
import pathlib
from dataclasses import dataclass
from typing import List, Dict, Any
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定模組日誌記錄器
logger = logging.getLogger(__name__)

@dataclass
class DocumentSource:
    """文件來源配置類別"""
    url: str
    source_type: str  # 'nephio' 或 'oran_sc'
    description: str
    priority: int     # 1-5, 1 為最高優先級
    enabled: bool = True
    
    def __post_init__(self):
        """初始化後驗證"""
        if self.priority not in range(1, 6):
            raise ValueError("優先級必須在 1-5 之間")
        if self.source_type not in ['nephio', 'oran_sc']:
            raise ValueError("來源類型必須是 'nephio' 或 'oran_sc'")

class Config:
    """系統配置類別"""
    
    # ============ API 設定 ============
    # API 模式選擇: anthropic | mock | local | puter
    API_MODE = os.getenv("API_MODE", "anthropic")
    
    # Anthropic API 配置
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # 本地模型配置 (API_MODE=local 時使用)
    LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434")
    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "llama2")
    
    # Puter.js 實驗性配置 (API_MODE=puter 時使用)
    PUTER_RISK_ACKNOWLEDGED = os.getenv("PUTER_RISK_ACKNOWLEDGED", "false").lower() == "true"
    PUTER_MODEL = os.getenv("PUTER_MODEL", "claude-sonnet-4")
    
    # ============ 向量資料庫設定 ============
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./oran_nephio_vectordb")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "oran_nephio_official")
    EMBEDDINGS_CACHE_PATH = os.getenv("EMBEDDINGS_CACHE_PATH", "./embeddings_cache")
    
    # ============ Claude 模型設定 ============
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
    CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "2048"))
    CLAUDE_TEMPERATURE = float(os.getenv("CLAUDE_TEMPERATURE", "0.1"))
    
    # ============ 文件載入設定 ============
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # ============ 日誌設定 ============
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/oran_nephio_rag.log")
    
    # ============ 同步設定 ============
    AUTO_SYNC_ENABLED = os.getenv("AUTO_SYNC_ENABLED", "true").lower() == "true"
    SYNC_INTERVAL_HOURS = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))
    
    # ============ 檢索設定 ============
    RETRIEVER_K = int(os.getenv("RETRIEVER_K", "6"))
    RETRIEVER_FETCH_K = int(os.getenv("RETRIEVER_FETCH_K", "15"))
    RETRIEVER_LAMBDA_MULT = float(os.getenv("RETRIEVER_LAMBDA_MULT", "0.7"))
    
    # ============ 文件載入器驗證設定 ============
    MIN_CONTENT_LENGTH = int(os.getenv("MIN_CONTENT_LENGTH", "500"))  # 最小內容長度 (bytes)
    MIN_EXTRACTED_CONTENT_LENGTH = int(os.getenv("MIN_EXTRACTED_CONTENT_LENGTH", "100"))  # 最小提取內容長度
    MIN_LINE_LENGTH = int(os.getenv("MIN_LINE_LENGTH", "3"))  # 最小行長度
    MAX_LINE_MERGE_LENGTH = int(os.getenv("MAX_LINE_MERGE_LENGTH", "80"))  # 行合併長度閾值
    CONTENT_PREVIEW_LENGTH = int(os.getenv("CONTENT_PREVIEW_LENGTH", "200"))  # 內容預覽長度
    MIN_KEYWORD_COUNT = int(os.getenv("MIN_KEYWORD_COUNT", "2"))  # 最小關鍵字數量
    
    # ============ 重試和延遲設定 ============
    RETRY_DELAY_BASE = float(os.getenv("RETRY_DELAY_BASE", "2.0"))  # 重試延遲基數
    MAX_RETRY_DELAY = int(os.getenv("MAX_RETRY_DELAY", "10"))  # 最大重試延遲 (秒)
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))  # 請求間延遲 (秒)
    
    # ============ 安全性設定 ============
    VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"  # 驗證 SSL 憑證
    SSL_TIMEOUT = int(os.getenv("SSL_TIMEOUT", "30"))  # SSL 連線超時時間
    
    # ============ 官方文件來源白名單 ============
    OFFICIAL_SOURCES: List[DocumentSource] = [
        DocumentSource(
            url="https://docs.nephio.org/docs/network-architecture/o-ran-integration/",
            source_type="nephio",
            description="Nephio O-RAN Integration Architecture",
            priority=1,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-4-o2ims/",
            source_type="nephio",
            description="O2IMS Integration Exercise",
            priority=2,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/architecture/",
            source_type="nephio",
            description="Nephio Core Architecture",
            priority=1,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-2-free5gc-operator/",
            source_type="nephio",
            description="Free5GC NF Deployment Guide",
            priority=2,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/installation/",
            source_type="nephio",
            description="Nephio Installation Guide",
            priority=3,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/automation-user-guide/",
            source_type="nephio",
            description="Nephio Automation User Guide",
            priority=2,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/configmap-user-guide/",
            source_type="nephio",
            description="Nephio ConfigMap User Guide",
            priority=3,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/package-specialization-user-guide/",
            source_type="nephio",
            description="Nephio Package Specialization Guide",
            priority=2,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-1-clusters/",
            source_type="nephio",
            description="Nephio Clusters Management Exercise",
            priority=2,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-3-edge-workloads/",
            source_type="nephio",
            description="Nephio Edge Workloads Exercise",
            priority=2,
            enabled=True
        )
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """驗證配置有效性"""
        errors = []
        
        try:
            # 檢查 API 模式
            valid_api_modes = ['anthropic', 'mock', 'local', 'puter']
            if cls.API_MODE not in valid_api_modes:
                errors.append(f"API_MODE 必須是以下其中之一: {', '.join(valid_api_modes)}")
            
            # 根據 API 模式檢查必要設定
            if cls.API_MODE == 'anthropic':
                if not cls.ANTHROPIC_API_KEY:
                    errors.append("API_MODE=anthropic 時需要設定 ANTHROPIC_API_KEY")
                elif cls.ANTHROPIC_API_KEY.startswith('test-'):
                    logger.warning("⚠️ 使用測試用 API 金鑰，可能無法正常運作")
            elif cls.API_MODE == 'local':
                if not cls.LOCAL_MODEL_URL:
                    errors.append("API_MODE=local 時需要設定 LOCAL_MODEL_URL")
                if not cls.LOCAL_MODEL_NAME:
                    errors.append("API_MODE=local 時需要設定 LOCAL_MODEL_NAME")
            elif cls.API_MODE == 'puter':
                if not cls.PUTER_RISK_ACKNOWLEDGED:
                    logger.warning("🚨 Puter.js 實驗性功能需要風險確認")
                    logger.warning("⚠️ 請設定 PUTER_RISK_ACKNOWLEDGED=true 以啟用此功能")
                    errors.append("API_MODE=puter 需要設定 PUTER_RISK_ACKNOWLEDGED=true")
                else:
                    logger.warning("🧪 已啟用實驗性 Puter.js 整合")
                    logger.warning("⚠️ 此功能僅建議用於學習和研究")
                if not cls.PUTER_MODEL:
                    errors.append("API_MODE=puter 時需要設定 PUTER_MODEL")
            
            # 檢查數值範圍
            if not (0 <= cls.CLAUDE_TEMPERATURE <= 1):
                errors.append("CLAUDE_TEMPERATURE 必須在 0-1 之間")
            
            if cls.CLAUDE_MAX_TOKENS < 100:
                errors.append("CLAUDE_MAX_TOKENS 不能少於 100")
            
            if cls.CHUNK_SIZE < 100:
                errors.append("CHUNK_SIZE 不能少於 100")
            
            if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
                errors.append("CHUNK_OVERLAP 不能大於等於 CHUNK_SIZE")
            
            # 檢查並建立目錄
            cls._ensure_directories()
            
            # 檢查官方來源配置
            if not cls.OFFICIAL_SOURCES:
                errors.append("OFFICIAL_SOURCES 不能為空")
            
            enabled_sources = [s for s in cls.OFFICIAL_SOURCES if s.enabled]
            if not enabled_sources:
                errors.append("至少需要啟用一個官方文件來源")
            
            if errors:
                error_message = "配置驗證失敗:\n" + "\n".join(f"- {error}" for error in errors)
                logger.error(f"❌ {error_message}")
                raise ValueError(error_message)
            
            logger.info("✅ 配置驗證通過")
            return True
            
        except ValueError:
            # 重新拋出 ValueError，保持原始錯誤訊息
            raise
        except Exception as e:
            error_message = f"配置驗證過程中發生未預期的錯誤: {str(e)}"
            logger.error(f"❌ {error_message}")
            raise RuntimeError(error_message) from e
    
    @classmethod
    def _ensure_directories(cls):
        """確保必要目錄存在"""
        directories = [
            ("日誌目錄", pathlib.Path(cls.LOG_FILE).parent),
            ("向量資料庫目錄", pathlib.Path(cls.VECTOR_DB_PATH)),
            ("嵌入模型快取目錄", pathlib.Path(cls.EMBEDDINGS_CACHE_PATH))
        ]
        
        for name, directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"✅ {name} 已確保存在: {directory}")
            except PermissionError as e:
                error_message = f"權限不足，無法建立{name}: {directory}"
                logger.error(f"❌ {error_message}")
                raise PermissionError(error_message) from e
            except OSError as e:
                error_message = f"無法建立{name}: {directory} - {str(e)}"
                logger.error(f"❌ {error_message}")
                raise OSError(error_message) from e
            except Exception as e:
                error_message = f"建立{name}時發生未預期的錯誤: {directory} - {str(e)}"
                logger.error(f"❌ {error_message}")
                raise RuntimeError(error_message) from e
    
    @classmethod
    def get_enabled_sources(cls) -> List[DocumentSource]:
        """取得啟用的文件來源"""
        return [source for source in cls.OFFICIAL_SOURCES if source.enabled]
    
    @classmethod
    def get_sources_by_priority(cls, max_priority: int = 2) -> List[DocumentSource]:
        """根據優先級取得文件來源"""
        enabled_sources = cls.get_enabled_sources()
        return [source for source in enabled_sources if source.priority <= max_priority]
    
    @classmethod
    def get_sources_by_type(cls, source_type: str) -> List[DocumentSource]:
        """根據類型取得文件來源"""
        enabled_sources = cls.get_enabled_sources()
        return [source for source in enabled_sources if source.source_type == source_type]
    
    @classmethod
    def add_custom_source(cls, source: DocumentSource):
        """新增自訂文件來源"""
        if source not in cls.OFFICIAL_SOURCES:
            cls.OFFICIAL_SOURCES.append(source)
            logger.info(f"新增文件來源: {source.description}")
    
    @classmethod
    def disable_source_by_url(cls, url: str) -> bool:
        """根據 URL 停用文件來源"""
        for source in cls.OFFICIAL_SOURCES:
            if source.url == url:
                source.enabled = False
                logger.info(f"停用文件來源: {source.description}")
                return True
        return False
    
    @classmethod
    def enable_source_by_url(cls, url: str) -> bool:
        """根據 URL 啟用文件來源"""
        for source in cls.OFFICIAL_SOURCES:
            if source.url == url:
                source.enabled = True
                logger.info(f"啟用文件來源: {source.description}")
                return True
        return False
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """取得配置摘要"""
        summary = {
            "api_mode": cls.API_MODE,
            "claude_model": cls.CLAUDE_MODEL,
            "vector_db_path": cls.VECTOR_DB_PATH,
            "total_sources": len(cls.OFFICIAL_SOURCES),
            "enabled_sources": len(cls.get_enabled_sources()),
            "nephio_sources": len(cls.get_sources_by_type("nephio")),
            "oran_sc_sources": len(cls.get_sources_by_type("oran_sc")),
            "auto_sync_enabled": cls.AUTO_SYNC_ENABLED,
            "sync_interval_hours": cls.SYNC_INTERVAL_HOURS,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP
        }
        
        # 根據 API 模式加入相關配置
        if cls.API_MODE == 'anthropic':
            summary["anthropic_api_available"] = bool(cls.ANTHROPIC_API_KEY and not cls.ANTHROPIC_API_KEY.startswith('test-'))
        elif cls.API_MODE == 'local':
            summary["local_model_url"] = cls.LOCAL_MODEL_URL
            summary["local_model_name"] = cls.LOCAL_MODEL_NAME
        elif cls.API_MODE == 'puter':
            summary["puter_risk_acknowledged"] = cls.PUTER_RISK_ACKNOWLEDGED
            summary["puter_model"] = cls.PUTER_MODEL
            summary["experimental_feature"] = True
        
        return summary

# 模組層級的便利函數
def validate_config() -> bool:
    """驗證配置的便利函數"""
    return Config.validate()

def get_config_summary() -> Dict[str, Any]:
    """取得配置摘要的便利函數"""
    return Config.get_config_summary()
