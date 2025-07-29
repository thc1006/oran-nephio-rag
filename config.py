import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    應用程式的設定類別，會自動從 .env 檔案讀取變數。
    """
    # .env 檔案路徑設定
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM 和 API 金鑰
    ANTHROPIC_API_KEY: str = "YOUR_ANTHROPIC_API_KEY_HERE"

    # ChromaDB 設定
    VECTOR_DB_PATH: str = "./oran_nephio_vectordb"
    COLLECTION_NAME: str = "oran_documents"

    # 嵌入模型設定
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # 日誌級別
    LOG_LEVEL: str = "INFO"


# 建立一個全域可用的設定實例
settings = Settings()

# 根據設定配置日誌
logging.basicConfig(level=settings.LOG_LEVEL.upper(), format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Configuration loaded successfully.")