"""
O-RAN × Nephio RAG 系統自動同步腳本
定期更新官方文件，確保 Release 更新自動納入
"""
import sys
import os
import logging
import schedule
import time
import signal
from datetime import datetime, timedelta
from typing import Optional
import threading

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.oran_nephio_rag import ORANNephioRAG
from src.config import Config

class AutoSyncService:
    """自動同步服務"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.rag_system = None
        self.is_running = False
        self.sync_thread = None
        self.stop_event = threading.Event()
        
        # 同步統計
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync_time': None,
            'last_sync_status': None,
            'last_error': None
        }
        
        # 設定日誌
        self._setup_logging()
        
        # 註冊信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("自動同步服務初始化完成")
    
    def _setup_logging(self):
        """設定日誌系統"""
        # 建立同步專用的日誌記錄器
        self.logger = logging.getLogger('auto_sync')
        
        # 避免重複添加處理器
        if not self.logger.handlers:
            # 檔案處理器
            log_file = os.path.join(os.path.dirname(self.config.LOG_FILE), 'auto_sync.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台處理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 設定格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加處理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def _signal_handler(self, signum, frame):
        """信號處理器"""
        self.logger.info(f"收到信號 {signum}，正在停止服務...")
        self.stop()
    
    def initialize_rag_system(self) -> bool:
        """初始化 RAG 系統"""
        try:
            self.logger.info("初始化 RAG 系統...")
            self.rag_system = ORANNephioRAG(self.config)
            self.logger.info("✅ RAG 系統初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"❌ RAG 系統初始化失敗: {e}")
            self.sync_stats['last_error'] = str(e)
            return False
    
    def sync_database(self) -> bool:
        """同步資料庫"""
        sync_start_time = datetime.now()
        self.sync_stats['total_syncs'] += 1
        
        try:
            self.logger.info(f"開始定期同步 - {sync_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 確保 RAG 系統已初始化
            if not self.rag_system:
                if not self.initialize_rag_system():
                    return False
            
            # 執行同步
            success = self.rag_system.update_database()
            
            sync_end_time = datetime.now()
            sync_duration = (sync_end_time - sync_start_time).total_seconds()
            
            if success:
                self.sync_stats['successful_syncs'] += 1
                self.sync_stats['last_sync_status'] = 'success'
                self.sync_stats['last_error'] = None
                self.logger.info(f"✅ 定期同步完成，耗時 {sync_duration:.2f} 秒")
            else:
                self.sync_stats['failed_syncs'] += 1
                self.sync_stats['last_sync_status'] = 'failed'
                self.logger.error("❌ 定期同步失敗")
            
            self.sync_stats['last_sync_time'] = sync_end_time.isoformat()
            
            # 記錄統計資訊
            self._log_sync_statistics()
            
            return success
            
        except Exception as e:
            sync_end_time = datetime.now()
            sync_duration = (sync_end_time - sync_start_time).total_seconds()
            
            self.sync_stats['failed_syncs'] += 1
            self.sync_stats['last_sync_status'] = 'error'
            self.sync_stats['last_sync_time'] = sync_end_time.isoformat()
            self.sync_stats['last_error'] = str(e)
            
            self.logger.error(f"❌ 同步過程中發生錯誤 (耗時 {sync_duration:.2f} 秒): {e}")
            return False
    
    def _log_sync_statistics(self):
        """記錄同步統計資訊"""
        stats = self.sync_stats
        success_rate = (stats['successful_syncs'] / stats['total_syncs'] * 100) if stats['total_syncs'] > 0 else 0
        
        self.logger.info("同步統計資訊:")
        self.logger.info(f"  總同步次數: {stats['total_syncs']}")
        self.logger.info(f"  成功次數: {stats['successful_syncs']}")
        self.logger.info(f"  失敗次數: {stats['failed_syncs']}")
        self.logger.info(f"  成功率: {success_rate:.1f}%")
        self.logger.info(f"  最後同步: {stats['last_sync_time']}")
        self.logger.info(f"  最後狀態: {stats['last_sync_status']}")
    
    def schedule_sync(self):
        """設定同步排程"""
        if not self.config.AUTO_SYNC_ENABLED:
            self.logger.info("自動同步功能已停用")
            return
        
        self.logger.info(f"設定自動同步，間隔: {self.config.SYNC_INTERVAL_HOURS} 小時")
        
        # 清除現有排程
        schedule.clear()
        
        # 設定排程
        schedule.every(self.config.SYNC_INTERVAL_HOURS).hours.do(self._scheduled_sync)
        
        # 也可以設定每週固定時間同步（可選）
        # schedule.every().sunday.at("02:00").do(self._scheduled_sync)
        
        self.logger.info("同步排程設定完成")
    
    def _scheduled_sync(self):
        """排程的同步任務"""
        if self.stop_event.is_set():
            return
        
        # 在單獨的執行緒中執行同步，避免阻塞排程器
        if self.sync_thread is None or not self.sync_thread.is_alive():
            self.sync_thread = threading.Thread(target=self.sync_database)
            self.sync_thread.daemon = True
            self.sync_thread.start()
    
    def run_once(self) -> bool:
        """執行單次同步"""
        self.logger.info("執行單次同步...")
        return self.sync_database()
    
    def run(self):
        """執行自動同步服務"""
        try:
            self.logger.info("🚀 自動同步服務啟動...")
            self.is_running = True
            
            # 設定排程
            self.schedule_sync()
            
            # 立即執行一次同步
            if self.config.AUTO_SYNC_ENABLED:
                self.logger.info("執行初始同步...")
                self.sync_database()
            
            # 主循環
            self.logger.info("進入服務主循環...")
            while self.is_running and not self.stop_event.is_set():
                try:
                    # 執行排程任務
                    schedule.run_pending()
                    
                    # 等待一分鐘
                    self.stop_event.wait(60)
                    
                except Exception as e:
                    self.logger.error(f"服務循環錯誤: {e}")
                    time.sleep(60)
            
            self.logger.info("自動同步服務已停止")
            
        except KeyboardInterrupt:
            self.logger.info("收到中斷信號，停止服務...")
        except Exception as e:
            self.logger.error(f"服務運行錯誤: {e}")
        finally:
            self.cleanup()
    
    def stop(self):
        """停止服務"""
        self.logger.info("正在停止自動同步服務...")
        self.is_running = False
        self.stop_event.set()
        
        # 等待同步執行緒完成
        if self.sync_thread and self.sync_thread.is_alive():
            self.logger.info("等待同步任務完成...")
            self.sync_thread.join(timeout=30)
    
    def cleanup(self):
        """清理資源"""
        self.logger.info("清理服務資源...")
        
        # 清除排程
        schedule.clear()
        
        # 關閉 RAG 系統（如果有清理方法的話）
        if self.rag_system:
            del self.rag_system
            self.rag_system = None
        
        self.logger.info("資源清理完成")
    
    def get_status(self) -> dict:
        """取得服務狀態"""
        return {
            "is_running": self.is_running,
            "auto_sync_enabled": self.config.AUTO_SYNC_ENABLED,
            "sync_interval_hours": self.config.SYNC_INTERVAL_HOURS,
            "sync_statistics": self.sync_stats.copy(),
            "next_sync": self._get_next_sync_time(),
            "rag_system_ready": self.rag_system is not None
        }
    
    def _get_next_sync_time(self) -> Optional[str]:
        """取得下次同步時間"""
        if not schedule.jobs:
            return None
        
        try:
            next_run = min(job.next_run for job in schedule.jobs if job.next_run)
            return next_run.isoformat()
        except (ValueError, AttributeError):
            return None

def main():
    """主函數"""
    try:
        # 建立並執行同步服務
        service = AutoSyncService()
        
        # 檢查命令列參數
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'once':
                # 執行單次同步
                print("執行單次同步...")
                success = service.run_once()
                sys.exit(0 if success else 1)
            
            elif command == 'status':
                # 顯示狀態
                status = service.get_status()
                print("自動同步服務狀態:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                sys.exit(0)
            
            elif command == 'help':
                print("使用方法:")
                print("  python auto_sync.py          # 啟動自動同步服務")
                print("  python auto_sync.py once     # 執行單次同步")
                print("  python auto_sync.py status   # 顯示狀態")
                print("  python auto_sync.py help     # 顯示說明")
                sys.exit(0)
            
            else:
                print(f"未知命令: {command}")
                print("使用 'python auto_sync.py help' 查看可用命令")
                sys.exit(1)
        
        # 預設執行自動同步服務
        service.run()
        
    except Exception as e:
        print(f"程式執行失敗: {e}")
        logging.error(f"程式執行失敗: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
