"""
配置模組單元測試
"""

import os
import shutil

# 導入待測試的模組
import sys
import tempfile
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config, DocumentSource, validate_config


class TestDocumentSource:
    """DocumentSource 類別測試"""

    def test_valid_document_source(self):
        """測試有效的 DocumentSource 建立"""
        source = DocumentSource(
            url="https://docs.nephio.org/test",
            source_type="nephio",
            description="Test Source",
            priority=1,
            enabled=True,
        )

        assert source.url == "https://docs.nephio.org/test"
        assert source.source_type == "nephio"
        assert source.description == "Test Source"
        assert source.priority == 1
        assert source.enabled is True

    def test_invalid_priority(self):
        """測試無效的優先級"""
        with pytest.raises(ValueError, match="優先級必須在 1-5 之間"):
            DocumentSource(url="https://test.com", source_type="nephio", description="Test", priority=0)  # 無效優先級

    def test_invalid_source_type(self):
        """測試無效的來源類型"""
        with pytest.raises(ValueError, match="來源類型必須是 'nephio' 或 'oran_sc'"):
            DocumentSource(url="https://test.com", source_type="invalid", description="Test", priority=1)  # 無效類型


class TestConfig:
    """Config 類別測試"""

    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    def test_valid_config(self):
        """測試有效配置"""
        with patch.object(Config, "_ensure_directories"):
            result = Config.validate()
            assert result is True

    def test_invalid_api_mode(self):
        """測試無效的 API 模式"""
        # 暫時修改 API_MODE 來測試驗證
        original_api_mode = Config.API_MODE
        Config.API_MODE = "invalid_mode"

        try:
            with pytest.raises(ValueError, match="API_MODE 必須是以下其中之一"):
                Config.validate()
        finally:
            # 恢復原始值
            Config.API_MODE = original_api_mode

    def test_invalid_temperature(self):
        """測試無效的溫度參數"""
        # 暫時修改 TEMPERATURE 來測試驗證
        original_temperature = Config.TEMPERATURE
        Config.TEMPERATURE = 1.5  # 無效值

        try:
            with pytest.raises(ValueError, match="TEMPERATURE 必須在 0-1 之間"):
                Config.validate()
        finally:
            # 恢復原始值
            Config.TEMPERATURE = original_temperature

    def test_get_enabled_sources(self):
        """測試取得啟用的來源"""
        enabled_sources = Config.get_enabled_sources()
        assert isinstance(enabled_sources, list)
        assert all(source.enabled for source in enabled_sources)

    def test_get_sources_by_type(self):
        """測試按類型取得來源"""
        nephio_sources = Config.get_sources_by_type("nephio")
        assert isinstance(nephio_sources, list)
        assert all(source.source_type == "nephio" for source in nephio_sources)

    def test_get_sources_by_priority(self):
        """測試按優先級取得來源"""
        high_priority_sources = Config.get_sources_by_priority(max_priority=1)
        assert isinstance(high_priority_sources, list)
        assert all(source.priority <= 1 for source in high_priority_sources)

    def test_add_custom_source(self):
        """測試添加自訂來源"""
        original_count = len(Config.OFFICIAL_SOURCES)

        custom_source = DocumentSource(
            url="https://custom.test.com", source_type="nephio", description="Custom Test Source", priority=3
        )

        Config.add_custom_source(custom_source)
        assert len(Config.OFFICIAL_SOURCES) == original_count + 1
        assert custom_source in Config.OFFICIAL_SOURCES

    def test_disable_enable_source(self):
        """測試停用和啟用來源"""
        # 取得第一個來源的 URL
        test_url = Config.OFFICIAL_SOURCES[0].url

        # 停用來源
        result = Config.disable_source_by_url(test_url)
        assert result is True
        assert not any(s.enabled for s in Config.OFFICIAL_SOURCES if s.url == test_url)

        # 重新啟用來源
        result = Config.enable_source_by_url(test_url)
        assert result is True
        assert any(s.enabled for s in Config.OFFICIAL_SOURCES if s.url == test_url)

    def test_get_config_summary(self):
        """測試取得配置摘要"""
        summary = Config.get_config_summary()
        assert isinstance(summary, dict)

        expected_keys = [
            "api_mode",
            "puter_model",
            "browser_headless",
            "browser_timeout",
            "vector_db_path",
            "total_sources",
            "enabled_sources",
            "nephio_sources",
            "oran_sc_sources",
            "auto_sync_enabled",
            "sync_interval_hours",
            "chunk_size",
            "chunk_overlap",
            "max_tokens",
            "temperature",
            "constraint_compliant",
            "integration_method",
        ]

        for key in expected_keys:
            assert key in summary


class TestConfigValidation:
    """配置驗證功能測試"""

    def test_validate_config_function(self):
        """測試 validate_config 函數"""
        with patch.object(Config, "_ensure_directories"):
            result = validate_config()
            assert result is True

    def test_validate_config_function_failure(self):
        """測試 validate_config 函數失敗情況"""
        # 暫時修改配置來觸發驗證失敗
        original_api_mode = Config.API_MODE
        Config.API_MODE = "invalid_mode"

        try:
            with pytest.raises(ValueError):
                validate_config()
        finally:
            # 恢復原始值
            Config.API_MODE = original_api_mode


# 整合測試
class TestConfigIntegration:
    """配置模組整合測試"""

    def test_full_config_workflow(self):
        """測試完整的配置工作流程"""
        # 驗證配置
        with patch.object(Config, "_ensure_directories"):
            Config.validate()

        # 取得配置摘要
        summary = Config.get_config_summary()
        # 使用默認值檢查，因為 Config 類別屬性在導入時設定
        assert summary["chunk_size"] == 1024  # 默認值
        assert summary["chunk_overlap"] == 200  # 默認值

        # 管理來源
        enabled_count_before = len(Config.get_enabled_sources())

        # 添加自訂來源
        custom_source = DocumentSource(
            url="https://integration.test.com", source_type="nephio", description="Integration Test Source", priority=2
        )
        Config.add_custom_source(custom_source)

        enabled_count_after = len(Config.get_enabled_sources())
        assert enabled_count_after == enabled_count_before + 1

        # 按類型過濾
        nephio_sources = Config.get_sources_by_type("nephio")
        assert any(s.url == "https://integration.test.com" for s in nephio_sources)


if __name__ == "__main__":
    pytest.main([__file__])
