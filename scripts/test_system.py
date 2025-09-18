"""
O-RAN × Nephio RAG 系統測試腳本

測試系統的各個組件是否正常運行
"""

import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def setup_test_logging():
    """設定測試專用日誌"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    # 抑制第三方套件的詳細日誌
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def test_python_environment() -> List[Tuple[str, bool, str]]:
    """測試 Python 環境"""
    tests = []

    # 測試 Python 版本
    python_version = sys.version_info
    if python_version >= (3, 10):
        tests.append(("Python 版本", True, f"{python_version.major}.{python_version.minor}.{python_version.micro}"))
    else:
        tests.append(("Python 版本", False, f"{python_version.major}.{python_version.minor} (需要 3.10+)"))

    # 測試環境變數 (Browser Mode)
    api_mode = os.getenv("API_MODE", "browser")
    if api_mode == "browser":
        tests.append(("API_MODE", True, "已設定為瀏覽器自動化模式"))
    else:
        tests.append(("API_MODE", False, f"設定為 {api_mode}，建議使用 browser 模式"))

    # 測試瀏覽器設定
    puter_model = os.getenv("PUTER_MODEL", "claude-sonnet-4")
    tests.append(("PUTER_MODEL", True, f"已設定為 {puter_model}"))

    return tests


def test_package_imports() -> List[Tuple[str, bool, str]]:
    """測試套件導入"""
    tests = []

    # 測試核心套件 (Browser Mode)
    packages = [
        ("langchain", "LangChain 框架"),
        ("langchain_community", "LangChain 社群套件"),
        ("chromadb", "向量資料庫"),
        ("selenium", "瀏覽器自動化"),
        ("webdriver_manager", "WebDriver 管理"),
        ("requests", "HTTP 客戶端"),
        ("beautifulsoup4", "HTML 解析器"),
        ("dotenv", "環境變數"),
        ("schedule", "任務排程"),
        ("rich", "終端介面"),
        ("tqdm", "進度條"),
    ]

    for package_name, description in packages:
        try:
            if package_name == "beautifulsoup4":
                import bs4

                version = getattr(bs4, "__version__", "未知")
            elif package_name == "dotenv":
                from dotenv import load_dotenv

                version = "可用"
            else:
                module = __import__(package_name)
                version = getattr(module, "__version__", "未知")

            tests.append((description, True, f"版本 {version}"))
        except ImportError as e:
            tests.append((description, False, f"導入失敗: {str(e)}"))
        except Exception as e:
            tests.append((description, False, f"錯誤: {str(e)}"))

    return tests


def test_system_modules() -> List[Tuple[str, bool, str]]:
    """測試系統模組"""
    tests = []

    try:
        # 測試配置模組
        from src.config import Config, DocumentSource, validate_config

        tests.append(("配置模組導入", True, "成功"))

        # 測試配置驗證
        try:
            validate_config()
            tests.append(("配置驗證", True, "通過"))
        except Exception as e:
            tests.append(("配置驗證", False, f"失敗: {e}"))

        # 測試文件載入器
        from src.document_loader import DocumentLoader, create_document_loader

        tests.append(("文件載入器導入", True, "成功"))

        # 測試 RAG 系統
        from src.oran_nephio_rag import ORANNephioRAG, create_rag_system

        tests.append(("RAG 系統導入", True, "成功"))

    except ImportError as e:
        tests.append(("系統模組導入", False, f"導入失敗: {e}"))
    except Exception as e:
        tests.append(("系統模組導入", False, f"錯誤: {e}"))

    return tests


def test_rag_system_basic() -> List[Tuple[str, bool, str]]:
    """測試 RAG 系統基本功能"""
    tests = []

    try:
        from src.oran_nephio_rag import ORANNephioRAG

        # 測試系統初始化
        try:
            rag = ORANNephioRAG()
            tests.append(("RAG 系統初始化", True, "成功"))
        except Exception as e:
            tests.append(("RAG 系統初始化", False, f"失敗: {e}"))
            return tests

        # 測試系統狀態
        try:
            status = rag.get_system_status()
            if isinstance(status, dict) and not status.get("error"):
                tests.append(("系統狀態檢查", True, "成功"))
            else:
                tests.append(("系統狀態檢查", False, f"狀態異常: {status.get('error', '未知錯誤')}"))
        except Exception as e:
            tests.append(("系統狀態檢查", False, f"失敗: {e}"))

        # 測試向量資料庫載入（如果存在）
        try:
            if rag.load_existing_database():
                tests.append(("向量資料庫載入", True, "成功"))

                # 測試問答鏈設定
                if rag.setup_qa_chain():
                    tests.append(("問答鏈設定", True, "成功"))

                    # 測試簡單查詢
                    try:
                        test_question = "什麼是 Nephio？"
                        result = rag.query(test_question)

                        if result and result.get("answer") and not result.get("error") and len(result["answer"]) > 10:
                            tests.append(("測試查詢", True, "成功"))
                        else:
                            error_msg = result.get("error", "回答內容異常")
                            tests.append(("測試查詢", False, f"失敗: {error_msg}"))
                    except Exception as e:
                        tests.append(("測試查詢", False, f"異常: {e}"))
                else:
                    tests.append(("問答鏈設定", False, "失敗"))
            else:
                tests.append(("向量資料庫載入", False, "資料庫不存在或載入失敗"))

        except Exception as e:
            tests.append(("向量資料庫載入", False, f"異常: {e}"))

    except Exception as e:
        tests.append(("RAG 系統測試", False, f"初始化異常: {e}"))

    return tests


def test_document_loader() -> List[Tuple[str, bool, str]]:
    """測試文件載入器功能"""
    tests = []

    try:
        from src.config import DocumentSource
        from src.document_loader import DocumentLoader

        # 建立文件載入器
        loader = DocumentLoader()
        tests.append(("文件載入器建立", True, "成功"))

        # 測試載入統計功能
        stats = loader.get_load_statistics()
        if isinstance(stats, dict):
            tests.append(("載入統計功能", True, "可用"))
        else:
            tests.append(("載入統計功能", False, "異常"))

        # 測試單一文件載入（使用一個簡單的測試來源）
        test_source = DocumentSource(
            url="https://docs.nephio.org/",  # 簡單頁面測試
            source_type="nephio",
            description="Nephio 首頁測試",
            priority=5,
            enabled=True,
        )

        try:
            # 設定較短的超時時間用於測試
            loader.timeout = 10
            doc = loader.load_document(test_source)

            if doc and hasattr(doc, "page_content") and len(doc.page_content) > 50:
                tests.append(("文件載入測試", True, f"成功載入 {len(doc.page_content)} 字元"))
            else:
                tests.append(("文件載入測試", False, "載入內容為空或過短"))
        except Exception as e:
            tests.append(("文件載入測試", False, f"網路載入失敗: {e}"))

    except Exception as e:
        tests.append(("文件載入器測試", False, f"異常: {e}"))

    return tests


def test_file_permissions() -> List[Tuple[str, bool, str]]:
    """測試檔案權限"""
    tests = []

    # 測試目錄建立和寫入權限
    test_dirs = ["logs", "oran_nephio_vectordb", "embeddings_cache"]

    for dir_name in test_dirs:
        try:
            # 嘗試建立目錄
            os.makedirs(dir_name, exist_ok=True)

            # 測試寫入權限
            test_file = os.path.join(dir_name, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")

            # 清理測試檔案
            if os.path.exists(test_file):
                os.remove(test_file)

            tests.append((f"目錄權限 {dir_name}", True, "可讀寫"))

        except Exception as e:
            tests.append((f"目錄權限 {dir_name}", False, f"權限錯誤: {e}"))

    return tests


def print_test_results(test_name: str, tests: List[Tuple[str, bool, str]]):
    """打印測試結果"""
    print(f"\n🔍 {test_name}")
    print("-" * 50)

    passed = 0
    total = len(tests)

    for name, result, message in tests:
        status = "✅" if result else "❌"
        print(f"{status} {name:<25} {message}")
        if result:
            passed += 1

    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n通過率: {passed}/{total} ({success_rate:.1f}%)")

    return passed, total


def generate_test_report(all_results: Dict[str, List[Tuple[str, bool, str]]]) -> str:
    """生成測試報告"""
    report = []
    report.append("=" * 70)
    report.append("O-RAN × Nephio RAG 系統測試報告")
    report.append("=" * 70)
    report.append(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Python 版本: {sys.version}")
    report.append("")

    total_passed = 0
    total_tests = 0

    for category, results in all_results.items():
        passed = sum(1 for _, result, _ in results if result)
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0

        total_passed += passed
        total_tests += total

        report.append(f"{category}: {passed}/{total} ({success_rate:.1f}%)")

        # 列出失敗的測試
        failed_tests = [name for name, result, message in results if not result]
        if failed_tests:
            report.append(f"  失敗項目: {', '.join(failed_tests)}")

    report.append("")
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    report.append(f"總體結果: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")

    if overall_success_rate >= 80:
        report.append("🎉 系統測試基本通過！")
    elif overall_success_rate >= 60:
        report.append("⚠️  系統部分功能可能有問題，建議檢查失敗項目")
    else:
        report.append("❌ 系統存在較多問題，需要解決後再使用")

    report.append("=" * 70)

    return "\n".join(report)


def main():
    """主測試函數"""
    print("🧪 O-RAN × Nephio RAG 系統全面測試")
    print("本測試將檢查系統的各個組件是否正常運行")

    # 設定日誌
    setup_test_logging()

    # 存儲所有測試結果
    all_results = {}

    try:
        # 1. 測試 Python 環境
        env_tests = test_python_environment()
        passed, total = print_test_results("Python 環境測試", env_tests)
        all_results["Python 環境"] = env_tests

        # 2. 測試套件導入
        import_tests = test_package_imports()
        passed, total = print_test_results("套件導入測試", import_tests)
        all_results["套件導入"] = import_tests

        # 3. 測試檔案權限
        permission_tests = test_file_permissions()
        passed, total = print_test_results("檔案權限測試", permission_tests)
        all_results["檔案權限"] = permission_tests

        # 4. 測試系統模組
        module_tests = test_system_modules()
        passed, total = print_test_results("系統模組測試", module_tests)
        all_results["系統模組"] = module_tests

        # 5. 測試文件載入器
        loader_tests = test_document_loader()
        passed, total = print_test_results("文件載入器測試", loader_tests)
        all_results["文件載入器"] = loader_tests

        # 6. 測試 RAG 系統（如果前面的測試基本通過）
        if sum(result for _, result, _ in module_tests) >= len(module_tests) * 0.8:
            rag_tests = test_rag_system_basic()
            passed, total = print_test_results("RAG 系統測試", rag_tests)
            all_results["RAG 系統"] = rag_tests
        else:
            print("\n⚠️  由於系統模組測試失敗較多，跳過 RAG 系統測試")
            all_results["RAG 系統"] = [("RAG 系統測試", False, "跳過測試")]

        # 生成並顯示最終報告
        report = generate_test_report(all_results)
        print(f"\n{report}")

        # 將報告寫入檔案
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/test_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            print("\n📄 詳細測試報告已儲存至: logs/test_report.txt")
        except Exception as e:
            print(f"\n⚠️  無法儲存測試報告: {e}")

        # 決定退出碼
        total_passed = sum(sum(1 for _, result, _ in results if result) for results in all_results.values())
        total_tests = sum(len(results) for results in all_results.values())
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        if success_rate >= 80:
            return 0  # 成功
        else:
            return 1  # 失敗

    except KeyboardInterrupt:
        print("\n\n👋 測試被使用者中斷")
        return 1
    except Exception as e:
        print(f"\n❌ 測試過程中發生未預期的錯誤: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
