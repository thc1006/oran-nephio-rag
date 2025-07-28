"""
自動同步腳本
"""
import sys
import os
import logging
import schedule
import time
from datetime import datetime

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.oran_nephio_rag import ORANNephioRAG
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoSyncService:
    """自動同步服務"""
    
    def __init__(self):
        self.config = Config()
        self.rag_system = None
        
    def initialize_system(self):
        """初始化 RAG 系統"""
        try:
            self.rag_system = ORANNephioRAG(self.config)
            logger.info("RAG 系統初始化成功")
            return True
        except Exception as e:
            logger.error(f"RAG 系統初始化失敗: {e}")
            return False
    
    def sync_database(self):
        """同步資料庫"""
        try:
            logger.info(f"開始定期同步 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if not self.rag_system:
                if not self.initialize_system():
                    return False
            
            success = self.rag_system.update_database()
            
            if success:
                logger.info("✅ 定期同步完成")
            else:
                logger.error("❌ 定期同步失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"同步過程中發生錯誤: {e}")
            return False
    
    def run(self):
        """執行自動同步服務"""
        if not self.config.AUTO_SYNC_ENABLED:
            logger.info("自動同步功能已停用")
            return
        
        logger.info("🚀 自動同步服務啟動...")
        logger.info(f"同步間隔: {self.config.SYNC_INTERVAL_HOURS} 小時")
        
        # 設定排程 - 每 N 小時執行一次
        schedule.every(self.config.SYNC_INTERVAL_HOURS).hours.do(self.sync_database)
        
        # 立即執行一次同步
        self.sync_database()
        
        # 持續運行
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
            except KeyboardInterrupt:
                logger.info("自動同步服務停止")
                break
            except Exception as e:
                logger.error(f"服務運行錯誤: {e}")
                time.sleep(300)  # 錯誤後等待 5 分鐘

def main():
    """主函數"""
    service = AutoSyncService()
    service.run()

if __name__ == "__main__":
    main()
