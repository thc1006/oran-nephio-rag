"""
main.py - 主程式整合
"""
import sys
import os
import logging
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.oran_nephio_rag import ORANNephioRAG
from src.config import Config, validate_config

def setup_logging():
    """設定日誌系統"""
    try:
        config = Config()
        
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # 設定第三方套件的日誌級別
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        
    except Exception as e:
        print(f"日誌設定失敗: {e}")
        # 使用基本配置
        logging.basicConfig(level=logging.INFO)

def main():
    """主函數"""
    logger = None
    rag_system = None
    
    try:
        # 設定日誌
        setup_logging()
        logger = logging.getLogger(__name__)
        
        print("=" * 60)
        print("O-RAN × Nephio 整合查詢系統")
        print("=" * 60)
        
        # 驗證配置
        logger.info("驗證系統配置...")
        validate_config()
        
        # 初始化 RAG 系統
        logger.info("初始化 RAG 系統...")
        rag_system = ORANNephioRAG()
        
        # 載入向量資料庫
        logger.info("載入向量資料庫...")
        if not rag_system.load_existing_database():
            print("❌ 向量資料庫載入失敗")
            return 1
        
        # 設定問答鏈
        logger.info("設定問答鏈...")
        if not rag_system.setup_qa_chain():
            print("❌ 問答鏈設定失敗")
            return 1
        
        print("✅ 系統初始化完成！")
        print("\n可用指令:")
        print("  quit/exit/退出 - 結束程式")
        print("  update - 更新向量資料庫")
        print("  status - 顯示系統狀態")
        print("  help - 顯示說明")
        print("-" * 60)
        
        # 主循環
        while True:
            try:
                question = input("\n請輸入您的問題：").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', '退出']:
                    print("👋 再見！")
                    break
                
                elif question.lower() == 'update':
                    print("🔄 正在更新資料庫...")
                    if rag_system.update_database():
                        print("✅ 資料庫更新成功！")
                    else:
                        print("❌ 資料庫更新失敗")
                    continue
                
                elif question.lower() == 'status':
                    try:
                        status = rag_system.get_system_status()
                        print("\n📊 系統狀態:")
                        for key, value in status.items():
                            if isinstance(value, dict):
                                print(f"  {key}:")
                                for sub_key, sub_value in value.items():
                                    print(f"    {sub_key}: {sub_value}")
                            else:
                                print(f"  {key}: {value}")
                    except Exception as e:
                        print(f"❌ 無法取得系統狀態: {e}")
                    continue
                
                elif question.lower() == 'help':
                    print("\n📖 系統說明:")
                    print("  本系統專注於 O-RAN 和 Nephio 整合相關問題")
                    print("  所有回答都基於官方文件，確保準確性")
                    print("  適合詢問 NF scale-out/scale-in 實作細節")
                    print("  範例問題:")
                    print("    - 如何在 Nephio 上實現 O-RAN DU 的 scale-out？")
                    print("    - O2IMS 介面在 NF 擴縮中扮演什麼角色？")
                    print("    - 什麼是 ProvisioningRequest CRD？")
                    continue
                
                # 處理問題查詢
                print("🤔 正在思考中...")
                result = rag_system.query(question)
                
                if result.get('error'):
                    print(f"\n❌ 查詢錯誤: {result['error']}")
                else:
                    print(f"\n💡 回答：\n{result['answer']}")
                    
                    if result.get('sources'):
                        print(f"\n📚 參考來源 ({len(result['sources'])} 個):")
                        for i, source in enumerate(result['sources'][:3], 1):  # 只顯示前 3 個
                            print(f"  {i}. [{source['type'].upper()}] {source['description']}")
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 程式被使用者中斷，再見！")
                break
            except Exception as e:
                print(f"\n❌ 發生錯誤: {str(e)}")
                if logger:
                    logger.error(f"主程式錯誤: {str(e)}", exc_info=True)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n👋 程式被使用者中斷，再見！")
        return 0
    except Exception as e:
        print(f"程式啟動失敗: {str(e)}")
        if logger:
            logger.error(f"程式啟動失敗: {str(e)}", exc_info=True)
        return 1
    finally:
        # 清理資源
        if rag_system:
            try:
                del rag_system
            except Exception as e:
                if logger:
                    logger.debug(f"清理 RAG 系統失敗: {e}")

if __name__ == "__main__":
    sys.exit(main())
