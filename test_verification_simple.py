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
        self.logger.info("Testing module imports...")

        try:
            # 測試核心模組導入
            from config import Config, DocumentSource
            from document_loader import DocumentContentCleaner
            from oran_nephio_rag import ORANNephioRAG, create_rag_system

            self.logger.info("SUCCESS: Core modules imported")

            # 測試異步模組導入
            from async_rag_system import AsyncDocumentLoader

            self.logger.info("SUCCESS: Async modules imported")

            # 測試監控模組導入
            from simple_monitoring import get_monitoring

            self.logger.info("SUCCESS: Monitoring modules imported")

            return True

        except ImportError as e:
            self.logger.error(f"FAILED: Module import failed: {e}")
            self.errors.append(f"Import Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"FAILED: Unexpected import error: {e}")
            self.errors.append(f"Unexpected Import Error: {e}")
            return False

    def test_config_validation(self) -> bool:
        """測試配置驗證"""
        self.logger.info("Testing configuration validation...")

        try:
            from config import Config

            # 測試基本配置
            config = Config()
            self.logger.info(f"Claude model: {config.CLAUDE_MODEL}")
            self.logger.info(f"Vector DB path: {config.VECTOR_DB_PATH}")
            self.logger.info(f"Document sources count: {len(config.OFFICIAL_SOURCES)}")

            # 測試文檔來源配置
            enabled_sources = config.get_enabled_sources()
            self.logger.info(f"Enabled sources: {len(enabled_sources)}")

            for source in enabled_sources[:3]:  # 顯示前3個
                self.logger.info(f"  - {source.description}")

            # 測試配置摘要
            summary = config.get_config_summary()
            self.logger.info(f"Config summary keys: {list(summary.keys())}")

            self.logger.info("SUCCESS: Configuration validation passed")
            return True

        except Exception as e:
            self.logger.error(f"FAILED: Configuration validation failed: {e}")
            self.errors.append(f"Config Validation Error: {e}")
            return False

    def test_dependencies(self) -> bool:
        """測試外部依賴"""
        self.logger.info("Testing external dependencies...")

        dependencies = [
            ("requests", "HTTP requests"),
            ("bs4", "HTML parsing"),
            ("langchain", "LangChain framework"),
            ("chromadb", "Vector database"),
            ("sentence_transformers", "Sentence embeddings"),
            ("numpy", "Numerical computing"),
            ("pydantic", "Data validation"),
            ("dotenv", "Environment variables"),
            ("aiohttp", "Async HTTP"),
        ]

        success_count = 0
        for package, description in dependencies:
            try:
                __import__(package)
                self.logger.info(f"SUCCESS: {description} ({package}) available")
                success_count += 1
            except ImportError:
                self.logger.warning(f"WARNING: {description} ({package}) not available")

        self.logger.info(f"Dependencies check: {success_count}/{len(dependencies)} available")
        return success_count >= len(dependencies) * 0.7  # 70% 以上可用即通過

    def test_mock_rag_system(self) -> bool:
        """測試模擬 RAG 系統建立"""
        self.logger.info("Testing mock RAG system creation...")

        try:
            from config import Config
            from oran_nephio_rag import create_rag_system

            # 建立配置
            config = Config()

            # 嘗試建立 RAG 系統 (不需要真實 API 金鑰)
            rag_system = create_rag_system(config)

            self.logger.info("SUCCESS: RAG system instance created")
            self.logger.info(f"System type: {type(rag_system).__name__}")

            return True

        except Exception as e:
            self.logger.error(f"FAILED: RAG system creation failed: {e}")
            self.errors.append(f"RAG System Creation Error: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        self.logger.info("Starting system verification tests...")

        tests = [
            ("Module Imports", self.test_imports),
            ("Configuration Validation", self.test_config_validation),
            ("External Dependencies", self.test_dependencies),
            ("RAG System Creation", self.test_mock_rag_system),
        ]

        results = {}
        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Running test: {test_name}")
            self.logger.info(f"{'='*50}")

            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                    self.logger.info(f"PASS: {test_name}")
                else:
                    self.logger.error(f"FAIL: {test_name}")
            except Exception as e:
                results[test_name] = False
                self.errors.append(f"{test_name}: {e}")
                self.logger.error(f"ERROR: {test_name} - {e}")

        # 生成報告
        self.logger.info(f"\n{'='*60}")
        self.logger.info("Test Results Summary")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Passed tests: {passed}/{total} ({passed/total*100:.1f}%)")

        if self.errors:
            self.logger.error(f"\nFound {len(self.errors)} errors:")
            for i, error in enumerate(self.errors, 1):
                self.logger.error(f"  {i}. {error}")

        # 總結
        if passed == total:
            self.logger.info("\nSUCCESS: All tests passed! Core system functionality works.")
            verdict = "PASS"
        elif passed >= total * 0.7:
            self.logger.warning(f"\nWARNING: Most tests passed ({passed}/{total}), system mostly functional.")
            verdict = "MOSTLY_PASS"
        else:
            self.logger.error(f"\nFAILED: Multiple tests failed ({passed}/{total}), system has serious issues.")
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
    print("O-RAN x Nephio RAG System Verification Test")
    print("=" * 60)

    tester = SystemVerificationTester()
    results = tester.run_all_tests()

    # 保存結果
    with open("verification_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nTest results saved to verification_results.json")
    return results["verdict"] in ["PASS", "MOSTLY_PASS"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
