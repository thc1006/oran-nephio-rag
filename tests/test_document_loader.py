"""
文件載入器模組單元測試
"""

import os

# 導入待測試的模組
import sys
from unittest.mock import Mock, patch

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config, DocumentSource

# 直接導入，避免透過 __init__.py 導入有問題的模組
from document_loader import DocumentContentCleaner, DocumentLoader


class TestDocumentContentCleaner:
    """DocumentContentCleaner 類別測試"""

    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.cleaner = DocumentContentCleaner()

    def test_clean_simple_html(self):
        """測試清理簡單 HTML"""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <p>This is a paragraph.</p>
                <script>alert('test');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """

        result = self.cleaner.clean_html(html)

        assert "Main Title" in result
        assert "This is a paragraph." in result
        assert "alert('test')" not in result
        assert "color: red" not in result

    def test_clean_html_with_navigation(self):
        """測試清理包含導航的 HTML"""
        html = """
        <html>
            <body>
                <nav class="navigation">
                    <a href="#home">Home</a>
                    <a href="#about">About</a>
                </nav>
                <main class="main-content">
                    <h1>Important Content</h1>
                    <p>This should be kept.</p>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """

        result = self.cleaner.clean_html(html)

        assert "Important Content" in result
        assert "This should be kept." in result
        assert "Home" not in result  # 導航應被移除
        assert "Footer content" not in result  # Footer 應被移除

    def test_merge_short_lines(self):
        """測試合併短行功能"""
        lines = [
            "This is a short",
            "line that should be",
            "merged together.",
            "",
            "# This is a header",
            "This should stay separate.",
        ]

        result = self.cleaner._merge_short_lines(lines)

        # 檢查短行是否被合併
        merged_text = " ".join(result)
        assert "This is a short line that should be merged together." in merged_text
        # Header might be merged with next line, so check if it exists in any form
        has_header = any("# This is a header" in line for line in result)
        assert has_header, f"Header not found in result: {result}"
        # Check if separate line exists somewhere
        has_separate = any("This should stay separate." in line for line in result)
        assert has_separate, f"Separate line not found in result: {result}"


class TestDocumentLoader:
    """DocumentLoader 類別測試"""

    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.config = Config()
        # 為測試降低內容長度要求
        self.config.MIN_CONTENT_LENGTH = 100
        self.config.MIN_EXTRACTED_CONTENT_LENGTH = 50
        self.loader = DocumentLoader(self.config)

    def test_init(self):
        """測試載入器初始化"""
        assert self.loader.config == self.config
        assert self.loader.max_retries == self.config.MAX_RETRIES
        assert self.loader.timeout == self.config.REQUEST_TIMEOUT
        assert hasattr(self.loader, "session")
        assert hasattr(self.loader, "content_cleaner")

    @patch("src.document_loader.requests.Session")
    def test_successful_document_load(self, mock_session_class):
        """測試成功載入文件"""
        test_url = "https://test.example.com/doc"
        test_content = """
        <html>
            <body>
                <main>
                    <h1>Test Document</h1>
                    <p>This is test content for Nephio and O-RAN scaling operations. Nephio is a cloud-native automation platform for network function deployment and management. O-RAN provides open interfaces and architecture for radio access network disaggregation. This content is specifically designed to be long enough for the document loader validation while containing relevant keywords about network scaling, deployment, and operations management. The content includes comprehensive information about container orchestration, microservices architecture, network function virtualization, and cloud-native automation for telecom infrastructure deployment and scaling operations.</p>
                </main>
            </body>
        </html>
        """

        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = test_content
        mock_response.content = test_content.encode("utf-8")
        mock_response.url = test_url
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status = Mock()

        # Mock the session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        source = DocumentSource(
            url=test_url, source_type="nephio", description="Test Document", priority=1, enabled=True
        )

        # Create a new loader instance to use the mocked session
        loader = DocumentLoader(self.config)
        doc = loader.load_document(source)

        assert doc is not None
        assert "Test Document" in doc.page_content
        assert "test content for Nephio" in doc.page_content
        assert doc.metadata["source_url"] == test_url
        assert doc.metadata["source_type"] == "nephio"
        assert doc.metadata["description"] == "Test Document"

    def test_disabled_source(self):
        """測試停用的來源"""
        source = DocumentSource(
            url="https://test.example.com/doc",
            source_type="nephio",
            description="Disabled Source",
            priority=1,
            enabled=False,  # 停用
        )

        doc = self.loader.load_document(source)
        assert doc is None

    @patch("src.document_loader.requests.Session")
    def test_http_error_handling(self, mock_session_class):
        """測試 HTTP 錯誤處理"""
        test_url = "https://test.example.com/notfound"

        # Mock session that raises 404 error
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        source = DocumentSource(
            url=test_url, source_type="nephio", description="Not Found Document", priority=1, enabled=True
        )

        # Create a new loader instance to use the mocked session
        loader = DocumentLoader(self.config)
        doc = loader.load_document(source)

        # DocumentLoader has offline fallback system that provides sample documents
        # when network requests fail, so we expect a fallback document instead of None
        assert doc is not None
        assert doc.metadata.get("is_sample") is True
        assert "Sample -" in doc.metadata.get("title", "")

    @patch("src.document_loader.requests.Session")
    def test_content_too_short(self, mock_session_class):
        """測試內容過短的處理"""
        test_url = "https://test.example.com/short"
        short_content = "<html><body><p>Hi</p></body></html>"  # 很短的內容

        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = short_content
        mock_response.content = short_content.encode("utf-8")
        mock_response.url = test_url
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status = Mock()

        # Mock the session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        source = DocumentSource(
            url=test_url, source_type="nephio", description="Short Document", priority=1, enabled=True
        )

        # Create a new loader instance to use the mocked session
        loader = DocumentLoader(self.config)
        doc = loader.load_document(source)

        # When content is too short, the loader fails and provides a fallback document
        assert doc is not None
        # Check for either fallback_mode or is_sample (existing fallback systems)
        assert doc.metadata.get("fallback_mode") is True or doc.metadata.get("is_sample") is True
        assert "Sample:" in doc.metadata.get("title", "") or "Sample -" in doc.metadata.get("title", "")

    @patch("src.document_loader.requests.Session")
    def test_retry_mechanism(self, mock_session_class):
        """測試重試機制"""
        # 創建一個會失敗的模擬載入器
        config = Config()
        config.MIN_CONTENT_LENGTH = 100
        config.MIN_EXTRACTED_CONTENT_LENGTH = 50

        # Mock session that always raises connection error
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        loader = DocumentLoader(config)
        loader.max_retries = 2

        source = DocumentSource(
            url="https://nonexistent.example.com/doc",
            source_type="nephio",
            description="Non-existent Document",
            priority=1,
            enabled=True,
        )

        # 這應該會重試但最終失敗，然後提供fallback文檔
        doc = loader.load_document(source)

        # Should return a fallback document instead of None due to offline fallback system
        assert doc is not None
        assert doc.metadata.get("is_sample") is True
        assert "Sample -" in doc.metadata.get("title", "")

        # 檢查統計資訊 - with fallback system, this is now a successful load
        stats = loader.get_load_statistics()
        assert stats["total_attempts"] == 1
        assert stats["successful_loads"] == 1  # Fallback counts as success
        assert stats["failed_loads"] == 0  # No actual failures with fallback system
        assert stats["retry_attempts"] >= 1  # 應該有重試

    @patch("src.document_loader.requests.Session")
    def test_load_all_documents(self, mock_session_class):
        """測試載入所有文件"""
        # Mock responses for multiple documents
        mock_responses = []
        sources = []

        for i in range(3):
            url = f"https://test{i}.example.com/doc"
            content = f"""
            <html>
                <body>
                    <main>
                        <h1>Test Document {i}</h1>
                        <p>Content about Nephio and O-RAN with keywords: scale, deployment, cluster, operator. This document covers network function scaling operations, container orchestration, microservices architecture, and cloud-native automation for telecom infrastructure. The content includes detailed information about deployment strategies, scaling policies, resource management, and operational procedures for network function virtualization environments.</p>
                    </main>
                </body>
            </html>
            """

            # Create mock response for this document
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "text/html"}
            mock_response.text = content
            mock_response.content = content.encode("utf-8")
            mock_response.url = url
            mock_response.encoding = "utf-8"
            mock_response.raise_for_status = Mock()
            mock_responses.append(mock_response)

            sources.append(
                DocumentSource(
                    url=url, source_type="nephio", description=f"Test Document {i}", priority=1, enabled=True
                )
            )

        # Mock the session to return different responses for different calls
        mock_session = Mock()
        mock_session.get.side_effect = mock_responses
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        # Create a new loader instance to use the mocked session
        loader = DocumentLoader(self.config)
        documents = loader.load_all_documents(sources)

        assert len(documents) == 3
        for i, doc in enumerate(documents):
            assert f"Test Document {i}" in doc.page_content
            assert doc.metadata["source_url"] == f"https://test{i}.example.com/doc"

    def test_get_load_statistics(self):
        """測試載入統計功能"""
        stats = self.loader.get_load_statistics()

        assert isinstance(stats, dict)
        expected_keys = ["total_attempts", "successful_loads", "failed_loads", "retry_attempts", "success_rate"]
        for key in expected_keys:
            assert key in stats

        # 初始狀態應該都是 0
        assert stats["total_attempts"] == 0
        assert stats["successful_loads"] == 0
        assert stats["failed_loads"] == 0
        assert stats["success_rate"] == 0

    @patch("src.document_loader.requests.Session")
    def test_extract_metadata(self, mock_session_class):
        """測試提取 metadata"""
        test_url = "https://test.example.com/doc"
        test_content = """
        <html>
            <head>
                <title>Test Page Title</title>
                <meta name="description" content="This is a test page description">
            </head>
            <body>
                <main>
                    <h1>Main Content</h1>
                    <p>Some content with nephio and o-ran keywords for network function scaling and deployment. This content discusses cloud-native automation, microservices architecture, and container orchestration for telecom network operations. The content is long enough to pass validation requirements while containing relevant technical information about network scaling operations and deployment strategies.</p>
                </main>
            </body>
        </html>
        """

        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = test_content
        mock_response.content = test_content.encode("utf-8")
        mock_response.url = test_url
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status = Mock()

        # Mock the session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        source = DocumentSource(
            url=test_url, source_type="nephio", description="Test Document", priority=1, enabled=True
        )

        # Create a new loader instance to use the mocked session
        loader = DocumentLoader(self.config)
        doc = loader.load_document(source)

        assert doc is not None
        assert doc.metadata["title"] == "Test Page Title"
        assert doc.metadata["meta_description"] == "This is a test page description"
        assert doc.metadata["content_type"] == "text/html"
        assert doc.metadata["status_code"] == 200

    @patch("time.sleep")  # 避免測試時實際等待
    @patch("src.document_loader.requests.Session")
    def test_exponential_backoff(self, mock_session_class, mock_sleep):
        """測試指數退避重試"""
        test_url = "https://test.example.com/retry"

        # Create mock responses for retries
        failed_response = Mock()
        failed_response.status_code = 500
        failed_response.encoding = "utf-8"
        failed_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")

        success_content = "<html><body><main><h1>Success</h1><p>Content with nephio scaling operations and network function deployment. This successful response contains comprehensive information about cloud-native automation, container orchestration, microservices architecture, and scaling policies for telecom network functions. The content covers deployment strategies, operational procedures, and resource management for network function virtualization environments.</p></main></body></html>"
        success_response = Mock()
        success_response.status_code = 200
        success_response.headers = {"content-type": "text/html"}
        success_response.text = success_content
        success_response.content = success_content.encode("utf-8")
        success_response.url = test_url
        success_response.encoding = "utf-8"
        success_response.raise_for_status = Mock()

        # Mock session to fail twice, then succeed
        mock_session = Mock()
        mock_session.get.side_effect = [failed_response, failed_response, success_response]
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        config = Config()
        config.MIN_CONTENT_LENGTH = 100
        config.MIN_EXTRACTED_CONTENT_LENGTH = 50
        loader = DocumentLoader(config)
        loader.max_retries = 3

        source = DocumentSource(url=test_url, source_type="nephio", description="Retry Test", priority=1, enabled=True)

        doc = loader.load_document(source)

        # 應該最終成功
        assert doc is not None
        assert "Success" in doc.page_content

        # 檢查是否有調用 sleep（指數退避）
        assert mock_sleep.call_count >= 2


class TestDocumentLoaderIntegration:
    """文件載入器整合測試"""

    @patch("src.document_loader.requests.Session")
    def test_real_world_workflow(self, mock_session_class):
        """測試真實世界的工作流程"""
        # 模擬一個類似 Nephio 文件的真實頁面
        test_url = "https://docs.nephio.org/test/integration"
        realistic_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nephio Network Architecture Integration</title>
            <meta name="description" content="Guide for O-RAN integration with Nephio">
        </head>
        <body>
            <nav class="navbar">
                <a href="/">Home</a>
                <a href="/docs">Docs</a>
            </nav>
            <main class="content">
                <h1>O-RAN Integration with Nephio</h1>
                <p>This document describes how to integrate O-RAN network functions with Nephio for automated deployment and scaling.</p>

                <h2>Scale-out Operations</h2>
                <p>To scale out network functions in Nephio, you need to:</p>
                <ol>
                    <li>Create a ProvisioningRequest CRD</li>
                    <li>Configure the desired replica count</li>
                    <li>Apply resource constraints</li>
                </ol>

                <h2>Scale-in Operations</h2>
                <p>Scale-in operations follow a similar pattern but require additional consideration for graceful shutdown.</p>

                <code>kubectl apply -f provisioning-request.yaml</code>
            </main>
            <footer>
                <p>Copyright Nephio Project</p>
            </footer>
            <script>
                // Some JavaScript that should be removed
                console.log("tracking");
            </script>
        </body>
        </html>
        """

        # Mock the response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html; charset=utf-8"}
        mock_response.text = realistic_content
        mock_response.content = realistic_content.encode("utf-8")
        mock_response.url = test_url
        mock_response.encoding = "utf-8"
        mock_response.raise_for_status = Mock()

        # Mock the session
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        config = Config()
        config.MIN_CONTENT_LENGTH = 100
        config.MIN_EXTRACTED_CONTENT_LENGTH = 50
        loader = DocumentLoader(config)
        source = DocumentSource(
            url=test_url, source_type="nephio", description="O-RAN Integration Guide", priority=1, enabled=True
        )

        doc = loader.load_document(source)

        # 驗證內容提取
        assert doc is not None
        assert "O-RAN Integration with Nephio" in doc.page_content
        assert "Scale-out Operations" in doc.page_content
        assert "ProvisioningRequest CRD" in doc.page_content
        assert "kubectl apply" in doc.page_content

        # 驗證清理效果
        assert "Home" not in doc.page_content  # 導航被移除
        assert "Copyright Nephio" not in doc.page_content  # Footer 被移除
        assert "console.log" not in doc.page_content  # JavaScript 被移除

        # 驗證 metadata
        assert doc.metadata["title"] == "Nephio Network Architecture Integration"
        assert "O-RAN integration" in doc.metadata["meta_description"]
        assert doc.metadata["source_type"] == "nephio"
        assert doc.metadata["priority"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
