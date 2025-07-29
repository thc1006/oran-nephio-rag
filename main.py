"""
O-RAN × Nephio RAG 系統主程式
提供互動式命令列介面
"""
import sys
import os
import logging
from datetime import datetime
from typing import Optional

# 確保可以導入 src 模組
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.oran_nephio_rag import ORANNephioRAG
    from src.config import Config, validate_config
except ImportError as e:
    print(f"❌ 模組導入失敗: {e}")
    print("請確保已安裝所有依賴套件：pip install -r requirements.txt")
    sys.exit(1)

def setup_logging() -> None:
    """設定日誌系統"""
    try:
        config = Config()
        
        # 確保日誌目錄存在
        log_dir = os.path.dirname(config.LOG_FILE)
        os.makedirs(log_dir, exist_ok=True)
        
        # 設定日誌格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 配置日誌處理器
        handlers = [
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
        
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL, logging.INFO),
            format=log_format,
            handlers=handlers,
            force=True  # 覆蓋現有配置
        )
        
        # 設定第三方套件的日誌級別
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('chromadb').setLevel(logging.WARNING)
        
    except Exception as e:
        print(f"⚠️ 日誌設定失敗: {e}")
        # 使用基本日誌配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

def display_welcome() -> None:
    """顯示歡迎訊息"""
    print("=" * 60)
    print("🚀 O-RAN × Nephio 整合查詢系統")
    print("=" * 60)
    print("專注於 Network Function Scale-out & Scale-in 實作指導")
    print("所有回答基於官方文件，確保資訊的權威性和準確性")
    print()

def display_commands() -> None:
    """顯示可用指令"""
    print("📋 可用指令:")
    print("  quit/exit/退出    - 結束程式")
    print("  update           - 更新向量資料庫")
    print("  status           - 顯示系統狀態")
    print("  help             - 顯示此說明")
    print("  clear            - 清除螢幕")
    print("  examples         - 顯示範例問題")
    print("-" * 60)

def display_examples() -> None:
    """顯示範例問題"""
    print("\n💡 範例問題:")
    examples = [
        "如何在 Nephio 上實現 O-RAN DU 的 scale-out？",
        "O2IMS 介面在 NF 擴縮中扮演什麼角色？",
        "什麼是 ProvisioningRequest CRD？如何使用？",
        "FOCOM 和 SMO 如何協作進行 NF 的自動擴縮？",
        "Nephio 的 GitOps 流程如何支援大規模擴縮？",
        "Free5GC 網路功能如何在 Nephio 上部署和擴縮？"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    print()

def clear_screen() -> None:
    """清除螢幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_system_status(status: dict) -> str:
    """格式化系統狀態顯示"""
    output = []
    output.append("📊 系統狀態:")
    output.append("-" * 30)
    
    # 基本狀態
    vectordb_status = "✅ 就緒" if status.get("vectordb_ready") else "❌ 未就緒"
    qa_chain_status = "✅ 就緒" if status.get("qa_chain_ready") else "❌ 未就緒"
    
    output.append(f"向量資料庫: {vectordb_status}")
    output.append(f"問答鏈: {qa_chain_status}")
    
    # 來源統計
    output.append(f"文件來源總數: {status.get('total_sources', 0)}")
    output.append(f"啟用來源數: {status.get('enabled_sources', 0)}")
    
    # 更新時間
    last_update = status.get('last_update')
    if last_update:
        output.append(f"最後更新: {last_update}")
    else:
        output.append("最後更新: 未知")
    
    # 向量資料庫資訊
    vectordb_info = status.get('vectordb_info', {})
    if vectordb_info and not vectordb_info.get('error'):
        doc_count = vectordb_info.get('document_count', 0)
        output.append(f"文件塊數量: {doc_count}")
    
    # 載入統計
    load_stats = status.get('load_statistics', {})
    if load_stats:
        success_rate = load_stats.get('success_rate', 0)
        output.append(f"文件載入成功率: {success_rate}%")
    
    return "\n".join(output)

def main() -> int:
    """主函數"""
    logger: Optional[logging.Logger] = None
    rag_system: Optional[ORANNephioRAG] = None
    
    try:
        # 設定日誌
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("程式啟動")
        
        # 顯示歡迎訊息
        display_welcome()
        
        # 驗證配置
        logger.info("驗證系統配置...")
        print("🔍 驗證系統配置...")
        validate_config()
        print("✅ 配置驗證通過")
        
        # 初始化 RAG 系統
        logger.info("初始化 RAG 系統...")
        print("🚀 初始化 RAG 系統...")
        rag_system = ORANNephioRAG()
        
        # 載入向量資料庫
        logger.info("載入向量資料庫...")
        print("📚 載入向量資料庫...")
        if not rag_system.load_existing_database():
            print("❌ 向量資料庫載入失敗")
            logger.error("向量資料庫載入失敗")
            return 1
        print("✅ 向量資料庫載入成功")
        
        # 設定問答鏈
        logger.info("設定問答鏈...")
        print("🔗 設定問答鏈...")
        if not rag_system.setup_qa_chain():
            print("❌ 問答鏈設定失敗")
            logger.error("問答鏈設定失敗")
            return 1
        print("✅ 問答鏈設定成功")
        
        print("\n🎉 系統初始化完成！")
        display_commands()
        
        # 主要互動循環
        while True:
            try:
                # 獲取用戶輸入
                question = input("\n請輸入您的問題：").strip()
                
                if not question:
                    continue
                
                # 處理特殊指令
                if question.lower() in ['quit', 'exit', '退出']:
                    print("👋 感謝使用！再見！")
                    logger.info("用戶正常退出程式")
                    break
                
                elif question.lower() == 'help':
                    display_commands()
                    continue
                
                elif question.lower() == 'clear':
                    clear_screen()
                    display_welcome()
                    continue
                
                elif question.lower() == 'examples':
                    display_examples()
                    continue
                
                elif question.lower() == 'update':
                    print("🔄 正在更新向量資料庫...")
                    logger.info("用戶觸發資料庫更新")
                    
                    if rag_system.update_database():
                        print("✅ 向量資料庫更新成功！")
                        logger.info("向量資料庫更新成功")
                    else:
                        print("❌ 向量資料庫更新失敗")
                        logger.error("向量資料庫更新失敗")
                    continue
                
                elif question.lower() == 'status':
                    try:
                        status = rag_system.get_system_status()
                        print(f"\n{format_system_status(status)}")
                    except Exception as e:
                        print(f"❌ 無法取得系統狀態: {e}")
                        logger.error(f"取得系統狀態失敗: {e}")
                    continue
                
                # 處理一般問題查詢
                print("🤔 正在思考中...")
                logger.info(f"處理用戶查詢: {question[:50]}...")
                
                start_time = datetime.now()
                result = rag_system.query(question)
                end_time = datetime.now()
                
                query_time = (end_time - start_time).total_seconds()
                logger.info(f"查詢完成，耗時: {query_time:.2f} 秒")
                
                # 顯示結果
                if result.get('error'):
                    print(f"\n❌ 查詢錯誤: {result['error']}")
                    logger.error(f"查詢錯誤: {result['error']}")
                else:
                    print(f"\n💡 回答：\n{result['answer']}")
                    
                    # 顯示參考來源
                    sources = result.get('sources', [])
                    if sources:
                        print(f"\n📚 參考來源 ({len(sources)} 個):")
                        for i, source in enumerate(sources[:3], 1):  # 只顯示前 3 個
                            source_type = source.get('type', 'UNKNOWN').upper()
                            description = source.get('description', '未知')
                            print(f"  {i}. [{source_type}] {description}")
                    
                    # 顯示查詢統計
                    if result.get('query_time'):
                        print(f"\n⚡ 查詢耗時: {result['query_time']} 秒")
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 程式被使用者中斷，再見！")
                logger.info("程式被用戶中斷")
                break
                
            except Exception as e:
                print(f"\n❌ 發生錯誤: {str(e)}")
                logger.error(f"處理用戶輸入時發生錯誤: {str(e)}", exc_info=True)
                print("請檢查日誌檔案以獲取詳細資訊")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n👋 程式被使用者中斷，再見！")
        if logger:
            logger.info("程式被用戶中斷")
        return 0
        
    except Exception as e:
        error_msg = f"程式啟動失敗: {str(e)}"
        print(f"❌ {error_msg}")
        
        if logger:
            logger.error(error_msg, exc_info=True)
        else:
            # 如果 logger 未初始化，直接打印詳細錯誤
            import traceback
            print("詳細錯誤資訊:")
            traceback.print_exc()
        
        return 1
        
    finally:
        # 清理資源
        if rag_system:
            try:
                del rag_system
                if logger:
                    logger.info("RAG 系統資源已清理")
            except Exception as e:
                if logger:
                    logger.debug(f"清理 RAG 系統失敗: {e}")

if __name__ == "__main__":
    sys.exit(main())
