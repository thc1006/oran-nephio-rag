"""
配置管理模組
"""
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DocumentSource:
    """文件來源配置"""
    url: str
    source_type: str  # 'oran_sc' or 'nephio'
    description: str
    priority: int  # 1-5, 1 為最高優先級
    enabled: bool = True

class Config:
    """系統配置類"""
    
    # API 設定
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # 向量資料庫設定
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./oran_nephio_vectordb")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "oran_nephio_official")
    
    # Claude 模型設定
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
    CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "2048"))
    CLAUDE_TEMPERATURE = float(os.getenv("CLAUDE_TEMPERATURE", "0.1"))
    
    # 日誌設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/oran_nephio_rag.log")
    
    # 同步設定
    AUTO_SYNC_ENABLED = os.getenv("AUTO_SYNC_ENABLED", "true").lower() == "true"
    SYNC_INTERVAL_HOURS = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))
    
    # 官方文件來源
    OFFICIAL_SOURCES: List[DocumentSource] = [
        DocumentSource(
            url="https://docs.nephio.org/docs/network-architecture/o-ran-integration/",
            source_type="nephio",
            description="Nephio O-RAN Integration Architecture",
            priority=1
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-4-o2ims/",
            source_type="nephio",
            description="O2IMS Integration Exercise",
            priority=2
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/architecture/",
            source_type="nephio",
            description="Nephio Core Architecture",
            priority=1
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-2-free5gc-operator/",
            source_type="nephio",
            description="Free5GC NF Deployment Guide",
            priority=2
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/installation/",
            source_type="nephio",
            description="Nephio Installation Guide",
            priority=3
        ),
        DocumentSource(
            url="https://docs.nephio.org/docs/guides/user-guides/automation-user-guide/",
            source_type="nephio",
            description="Nephio Automation User Guide",
            priority=2
        )
    ]
    
    @classmethod
    def validate(cls):
        """驗證配置"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        # 確保日誌目錄存在
        log_dir = os.path.dirname(cls.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        return True
