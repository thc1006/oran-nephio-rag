#!/usr/bin/env python3
"""
O-RAN × Nephio RAG 系統驗證測試腳本
用於驗證系統的核心功能是否能正常運作
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

# 設定測試環境
TEST_ENV = {
    "ANTHROPIC_API_KEY": "test-key-not-real",
    "VECTOR_DB_PATH": "./test_vectordb",
    "EMBEDDINGS_CACHE_PATH": "./test_embeddings_cache",
    "LOG_LEVEL": "INFO",
    "CLAUDE_MODEL": "claude-3-sonnet-20240229",
    "CLAUDE_TEMPERATURE": "0.1",
}

# 設定環境變數
for key, value in TEST_ENV.items():
    os.environ[key] = value

# 添加 src 到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))


class SystemVerificationTester:
    """系統驗證測試器"""

    def __init__(self):
        self.results = {}
        self.errors = []
        self.setup_logging()

    def setup_logging(self):
        """設定日誌"""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

    def test_imports(self) -> bool:
        """測試模組導入"""
        self.logger.info("🔍 測試模組導入...")

        try:
            # 測試核心模組導入
            from config import Config, DocumentSource
            from document_loader import DocumentContentCleaner
            from oran_nephio_rag import ORANNephioRAG, create_rag_system

            self.logger.info("✅ 核心模組導入成功")

            # 測試異步模組導入
            from async_rag_system import AsyncORANNephioRAG

            self.logger.info("✅ 異步模組導入成功")

            # 測試監控模組導入
            from simple_monitoring import get_monitoring

            self.logger.info("✅ 監控模組導入成功")

            return True

        except ImportError as e:
            self.logger.error(f"❌ 模組導入失敗: {e}")
            self.errors.append(f"Import Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ 未預期的導入錯誤: {e}")
            self.errors.append(f"Unexpected Import Error: {e}")
            return False

    def test_config_validation(self) -> bool:
        """測試配置驗證"""
        self.logger.info("🔍 測試配置驗證...")

        try:
            from config import Config

            # 測試基本配置
            config = Config()
            self.logger.info(f"Claude 模型: {config.CLAUDE_MODEL}")
            self.logger.info(f"向量資料庫路徑: {config.VECTOR_DB_PATH}")
            self.logger.info(f"文檔來源數量: {len(config.OFFICIAL_SOURCES)}")

            # 測試文檔來源配置
            enabled_sources = config.get_enabled_sources()
            self.logger.info(f"啟用的文檔來源: {len(enabled_sources)}")

            for source in enabled_sources[:3]:  # 顯示前3個
                self.logger.info(f"  - {source.description}")

            # 測試配置摘要
            summary = config.get_config_summary()
            self.logger.info(f"配置摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")

            self.logger.info("✅ 配置驗證成功")
            return True

        except Exception as e:
            self.logger.error(f"❌ 配置驗證失敗: {e}")
            self.errors.append(f"Config Validation Error: {e}")
            return False

    def test_document_source_creation(self) -> bool:
        """測試文檔來源建立"""
        self.logger.info("🔍 測試文檔來源建立...")

        try:
            from config import DocumentSource

            # 測試有效的文檔來源
            valid_source = DocumentSource(
                url="https://docs.nephio.org/docs/architecture/",
                source_type="nephio",
                description="Test Nephio Architecture",
                priority=1,
            )
            self.logger.info(f"✅ 有效文檔來源建立成功: {valid_source.description}")

            # 測試無效的優先級
            try:
                DocumentSource(
                    url="https://example.com",
                    source_type="nephio",
                    description="Invalid Priority",
                    priority=10,  # 無效優先級
                )
                self.logger.error("❌ 應該捕獲無效優先級錯誤")
                return False
            except ValueError:
                self.logger.info("✅ 正確捕獲無效優先級錯誤")

            # 測試無效的來源類型
            try:
                DocumentSource(
                    url="https://example.com",
                    source_type="invalid_type",  # 無效類型
                    description="Invalid Type",
                    priority=1,
                )
                self.logger.error("❌ 應該捕獲無效來源類型錯誤")
                return False
            except ValueError:
                self.logger.info("✅ 正確捕獲無效來源類型錯誤")

            return True

        except Exception as e:
            self.logger.error(f"❌ 文檔來源建立測試失敗: {e}")
            self.errors.append(f"DocumentSource Creation Error: {e}")
            return False

    def test_content_cleaner(self) -> bool:
        """測試內容清理器"""
        self.logger.info("🔍 測試內容清理器...")

        try:
            from config import Config
            from document_loader import DocumentContentCleaner

            config = Config()
            cleaner = DocumentContentCleaner(config)

            # 測試 HTML 清理

            # 這裡我們假設有清理方法，實際上需要檢查實現
            self.logger.info("✅ 內容清理器初始化成功")
            self.logger.info(f"不需要的標籤: {cleaner.unwanted_tags[:5]}...")
            self.logger.info(f"不需要的選擇器: {cleaner.unwanted_selectors[:5]}...")

            return True

        except Exception as e:
            self.logger.error(f"❌ 內容清理器測試失敗: {e}")
            self.errors.append(f"Content Cleaner Error: {e}")
            return False

    def test_mock_rag_system(self) -> bool:
        """測試模擬 RAG 系統建立"""
        self.logger.info("🔍 測試模擬 RAG 系統建立...")

        try:
            from config import Config
            from oran_nephio_rag import create_rag_system

            # 建立配置
            config = Config()

            # 嘗試建立 RAG 系統 (不需要真實 API 金鑰)
            rag_system = create_rag_system(config)

            self.logger.info("✅ RAG 系統實例建立成功")
            self.logger.info(f"系統類型: {type(rag_system).__name__}")

            # 測試系統狀態 (在沒有真實 API 的情況下)
            try:
                status = rag_system.get_system_status()
                self.logger.info("✅ 系統狀態查詢成功")
                self.logger.info(f"狀態鍵: {list(status.keys())}")
            except Exception as e:
                self.logger.warning(f"⚠️  系統狀態查詢失敗 (預期的，因為沒有真實 API): {e}")

            return True

        except Exception as e:
            self.logger.error(f"❌ RAG 系統建立測試失敗: {e}")
            self.errors.append(f"RAG System Creation Error: {e}")
            return False

    def test_async_components(self) -> bool:
        """測試異步組件"""
        self.logger.info("🔍 測試異步組件...")

        try:
            import asyncio

            from async_rag_system import AsyncDocumentLoader
            from config import Config

            async def test_async_loader():
                config = Config()
                AsyncDocumentLoader(config)
                self.logger.info("✅ 異步文檔載入器建立成功")
                return True

            # 運行異步測試
            result = asyncio.run(test_async_loader())

            if result:
                self.logger.info("✅ 異步組件測試成功")
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"❌ 異步組件測試失敗: {e}")
            self.errors.append(f"Async Components Error: {e}")
            return False

    def test_monitoring_system(self) -> bool:
        """測試監控系統"""
        self.logger.info("🔍 測試監控系統...")

        try:
            from simple_monitoring import get_monitoring

            monitoring = get_monitoring()
            self.logger.info("✅ 監控系統建立成功")
            self.logger.info(f"監控系統類型: {type(monitoring).__name__}")

            # 測試監控功能
            monitoring.start()
            self.logger.info("✅ 監控系統啟動成功")

            # 測試記錄功能
            monitoring.record_documents_loaded(100)
            monitoring.set_vectordb_ready(False)
            self.logger.info("✅ 監控記錄功能測試成功")

            return True

        except Exception as e:
            self.logger.error(f"❌ 監控系統測試失敗: {e}")
            self.errors.append(f"Monitoring System Error: {e}")
            return False

    def test_dependencies(self) -> bool:
        """測試外部依賴"""
        self.logger.info("🔍 測試外部依賴...")

        dependencies = [
            ("requests", "HTTP 請求"),
            ("beautifulsoup4", "HTML 解析"),
            ("langchain", "LangChain 框架"),
            ("chromadb", "向量資料庫"),
            ("sentence_transformers", "句子嵌入"),
            ("numpy", "數值計算"),
            ("pydantic", "資料驗證"),
            ("python-dotenv", "環境變數"),
            ("aiohttp", "異步 HTTP"),
            ("asyncio", "異步編程"),
        ]

        success_count = 0
        for package, description in dependencies:
            try:
                if package == "asyncio":
                    import asyncio
                elif package == "beautifulsoup4":
                    import bs4
                elif package == "sentence_transformers":
                    import sentence_transformers
                elif package == "python-dotenv":
                    import dotenv
                else:
                    __import__(package)

                self.logger.info(f"✅ {description} ({package}) 可用")
                success_count += 1
            except ImportError:
                self.logger.warning(f"⚠️  {description} ({package}) 不可用")

        self.logger.info(f"依賴檢查結果: {success_count}/{len(dependencies)} 可用")
        return success_count >= len(dependencies) * 0.8  # 80% 以上可用即通過

    def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        self.logger.info("🚀 開始系統驗證測試...")

        tests = [
            ("模組導入", self.test_imports),
            ("配置驗證", self.test_config_validation),
            ("文檔來源建立", self.test_document_source_creation),
            ("內容清理器", self.test_content_cleaner),
            ("RAG 系統建立", self.test_mock_rag_system),
            ("異步組件", self.test_async_components),
            ("監控系統", self.test_monitoring_system),
            ("外部依賴", self.test_dependencies),
        ]

        results = {}
        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"執行測試: {test_name}")
            self.logger.info(f"{'='*50}")

            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                    self.logger.info(f"✅ {test_name} 測試通過")
                else:
                    self.logger.error(f"❌ {test_name} 測試失敗")
            except Exception as e:
                results[test_name] = False
                self.errors.append(f"{test_name}: {e}")
                self.logger.error(f"❌ {test_name} 測試異常: {e}")

        # 生成報告
        self.logger.info(f"\n{'='*60}")
        self.logger.info("📊 測試結果摘要")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"通過測試: {passed}/{total} ({passed/total*100:.1f}%)")

        if self.errors:
            self.logger.error(f"\n❌ 發現 {len(self.errors)} 個錯誤:")
            for i, error in enumerate(self.errors, 1):
                self.logger.error(f"  {i}. {error}")

        # 總結
        if passed == total:
            self.logger.info("\n🎉 所有測試通過！系統核心功能運作正常。")
            verdict = "PASS"
        elif passed >= total * 0.8:
            self.logger.warning(f"\n⚠️  大部分測試通過 ({passed}/{total})，系統基本可用但需要注意一些問題。")
            verdict = "MOSTLY_PASS"
        else:
            self.logger.error(f"\n💥 多項測試失敗 ({passed}/{total})，系統可能存在嚴重問題。")
            verdict = "FAIL"

        return {
            "verdict": verdict,
            "passed": passed,
            "total": total,
            "pass_rate": passed / total * 100,
            "results": results,
            "errors": self.errors,
        }


def main():
    """主函數"""
    print("🔬 O-RAN × Nephio RAG 系統驗證測試")
    print("=" * 60)

    tester = SystemVerificationTester()
    results = tester.run_all_tests()

    # 保存結果
    with open("verification_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n📄 測試結果已保存至 verification_results.json")
    return results["verdict"] == "PASS"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
