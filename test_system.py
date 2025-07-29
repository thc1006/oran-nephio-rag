#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系統測試腳本 - 驗證 O-RAN × Nephio RAG 系統功能
"""
import sys
import os
import logging
from datetime import datetime

# 設定路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """設定日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_basic_imports():
    """測試基本模組導入"""
    print("=== Basic Module Import Test ===")
    
    try:
        import requests
        print("[OK] requests import successful")
    except ImportError as e:
        print(f"[FAIL] requests import failed: {e}")
        return False
    
    try:
        import bs4
        print("[OK] beautifulsoup4 import successful")
    except ImportError as e:
        print(f"[FAIL] beautifulsoup4 import failed: {e}")
        return False
    
    try:
        import langchain
        print("[OK] langchain import successful")
    except ImportError as e:
        print(f"[FAIL] langchain import failed: {e}")
        return False
    
    return True

def test_config_module():
    """測試配置模組"""
    print("\n=== 測試配置模組 ===")
    
    try:
        from config import Config, DocumentSource, validate_config
        print("✅ config 模組導入成功")
        
        # 測試配置摘要
        summary = Config.get_config_summary()
        print(f"✅ 配置摘要取得成功: {len(summary)} 項設定")
        
        # 測試文件來源
        sources = Config.get_enabled_sources()
        print(f"✅ 啟用的文件來源: {len(sources)} 個")
        
        return True
    except Exception as e:
        print(f"❌ config 模組測試失敗: {e}")
        return False

def test_document_loader():
    """測試文件載入器"""
    print("\n=== 測試文件載入器 ===")
    
    try:
        from document_loader import DocumentLoader, create_document_loader
        from config import Config, DocumentSource
        
        print("✅ document_loader 模組導入成功")
        
        # 建立測試配置
        config = Config()
        loader = create_document_loader(config)
        print("✅ 文件載入器建立成功")
        
        # 測試統計功能
        stats = loader.get_load_statistics()
        print(f"✅ 載入統計功能正常: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ document_loader 模組測試失敗: {e}")
        return False

def test_simple_request():
    """測試簡單的網路請求"""
    print("\n=== 測試網路請求功能 ===")
    
    try:
        import requests
        
        # 測試基本請求功能
        response = requests.get('https://httpbin.org/get', timeout=10)
        response.raise_for_status()
        print("✅ 基本網路請求功能正常")
        
        return True
    except Exception as e:
        print(f"❌ 網路請求測試失敗: {e}")
        return False

def test_chromadb_fallback():
    """測試是否可以不依賴 ChromaDB 運行"""
    print("\n=== 測試 ChromaDB 相容性 ===")
    
    try:
        import chromadb
        print("✅ ChromaDB 可用")
        return True
    except Exception as e:
        print(f"⚠️ ChromaDB 不可用: {e}")
        print("💡 系統可以在沒有 ChromaDB 的情況下運行基本功能")
        return False

def main():
    """主測試函數"""
    setup_logging()
    
    print("O-RAN × Nephio RAG 系統測試")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python 版本: {sys.version}")
    print()
    
    test_results = []
    
    # 執行各項測試
    test_results.append(("基本模組導入", test_basic_imports()))
    test_results.append(("配置模組", test_config_module()))
    test_results.append(("文件載入器", test_document_loader()))
    test_results.append(("網路請求", test_simple_request()))
    test_results.append(("ChromaDB 相容性", test_chromadb_fallback()))
    
    # 統計結果
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n=== 測試結果摘要 ===")
    print(f"總測試項目: {total_tests}")
    print(f"通過測試: {passed_tests}")
    print(f"失敗測試: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests / total_tests * 100:.1f}%")
    
    print(f"\n=== 詳細結果 ===")
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    # 保存結果
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/system_test_report.txt", "w", encoding="utf-8") as f:
            f.write(f"O-RAN × Nephio RAG 系統測試報告\n")
            f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python 版本: {sys.version}\n\n")
            f.write(f"測試結果:\n")
            for test_name, result in test_results:
                status = "通過" if result else "失敗"  
                f.write(f"- {test_name}: {status}\n")
            f.write(f"\n成功率: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)\n")
        
        print(f"\n測試報告已保存至: logs/system_test_report.txt")
    except Exception as e:
        print(f"保存測試報告失敗: {e}")
    
    # 返回總體結果
    if passed_tests >= total_tests * 0.8:
        print("\n🎉 系統測試基本通過！")
        return 0
    else:
        print("\n⚠️ 系統測試發現問題，需要進一步檢查")
        return 1

if __name__ == "__main__":
    sys.exit(main())