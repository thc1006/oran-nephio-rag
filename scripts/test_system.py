"""
系統測試腳本
"""
import sys
import os
import logging
from typing import List, Tuple

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.oran_nephio_rag import ORANNephioRAG
from src.config import Config

def test_environment() -> List[Tuple[str, bool, str]]:
    """測試環境設定"""
    tests = []
    
    # 測試 Python 版本
    python_version = sys.version_info
    if python_version >= (3, 10):
        tests.append(("Python 版本", True, f"{python_version.major}.{python_version.minor}"))
    else:
        tests.append(("Python 版本", False, f"{python_version.major}.{python_version.minor} (需要 3.10+)"))
    
    # 測試環境變數
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        tests.append(("ANTHROPIC_API_KEY", True, "已設定"))
    else:
        tests.append(("ANTHROPIC_API_KEY", False, "未設定"))
    
    # 測試套件導入
    try:
        import langchain
        tests.append(("LangChain", True, f"版本 {langchain.__version__}"))
    except ImportError as e:
        tests.append(("LangChain", False, f"導入失敗: {e}"))
    
    try:
        import chromadb
        tests.append(("ChromaDB", True, f"版本 {chromadb.__version__}"))
    except ImportError as e:
        tests.append(("ChromaDB", False, f"導入失敗: {e}"))
    
    try:
        from langchain_anthropic import ChatAnthropic
        tests.append(("Anthropic", True, "可用"))
    except ImportError as e:
        tests.append(("Anthropic", False, f"導入失敗: {e}"))
    
    try:
        from sentence_transformers import SentenceTransformer
        tests.append(("SentenceTransformers", True, "可用"))
    except ImportError as e:
        tests.append(("SentenceTransformers", False, f"導入失敗: {e}"))
    
    return tests

def test_rag_system() -> List[Tuple[str, bool, str]]:
    """測試 RAG 系統"""
    tests = []
    
    try:
        # 測試系統初始化
        rag = ORANNephioRAG()
        tests.append(("RAG 系統初始化", True, "成功"))
        
        # 測試向量資料庫載入
        if rag.load_existing_database():
            tests.append(("向量資料庫載入", True, "成功"))
        else:
            tests.append(("向量資料庫載入", False, "失敗"))
            return tests
        
        # 測試問答鏈設定
        if rag.setup_qa_chain():
            tests.append(("問答鏈設定", True, "成功"))
        else:
            tests.append(("問答鏈設定", False, "失敗"))
            return tests
        
        # 測試簡單查詢
        test_question = "什麼是 Nephio？"
        result = rag.query(test_question)
        
        if result and result.get("answer") and not result.get("error"):
            tests.append(("測試查詢", True, "成功"))
        else:
            tests.append(("測試查詢", False, f"失敗: {result.get('error', '未知錯誤')}"))
        
    except Exception as e:
        tests.append(("RAG 系統初始化", False, f"異常: {e}"))
    
    return tests

def run_all_tests():
    """執行所有測試"""
    print("=" * 60)
    print("O-RAN × Nephio RAG 系統測試")
    print("=" * 60)
    
    # 環境測試
    print("\n🔍 環境測試:")
    print("-" * 30)
    
    env_tests = test_environment()
    env_passed = 0
    
    for name, passed, message in env_tests:
        status = "✅" if passed else "❌"
        print(f"{status} {name:<20} {message}")
        if passed:
            env_passed += 1
    
    print(f"\n環境測試結果: {env_passed}/{len(env_tests)} 通過")
    
    # 如果環境測試失敗太多，跳過系統測試
    if env_passed < len(env_tests) * 0.8:
        print("\n⚠️  環境測試失敗過多，跳過系統測試")
        return
    
    # 系統測試
    print("\n🚀 系統測試:")
    print("-" * 30)
    
    system_tests = test_rag_system()
    system_passed = 0
    
    for name, passed, message in system_tests:
        status = "✅" if passed else "❌"
        print(f"{status} {name:<20} {message}")
        if passed:
            system_passed += 1
    
    print(f"\n系統測試結果: {system_passed}/{len(system_tests)} 通過")
    
    # 總結
    total_tests = len(env_tests) + len(system_tests)
    total_passed = env_passed + system_passed
    
    print("\n" + "=" * 60)
    print(f"總體測試結果: {total_passed}/{total_tests} 通過")
    
    if total_passed == total_tests:
        print("🎉 所有測試通過！系統已準備就緒。")
    else:
        print("⚠️  部分測試失敗，請檢查上述錯誤訊息。")
    
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
