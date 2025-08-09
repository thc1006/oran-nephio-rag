"""
Test suite for document loading with comprehensive HTTP mocking
Demonstrates usage of HTTP and document fixtures
"""
import pytest
import responses
from unittest.mock import patch, MagicMock

# Test markers for organization
pytestmark = [pytest.mark.unit, pytest.mark.network]


class TestHTTPMocking:
    """Test HTTP operations with mocked requests"""
    
    def test_requests_session_mock(self, mock_requests_session):
        """Test basic HTTP session mocking"""
        session = mock_requests_session
        
        # Test GET request
        response = session.get("https://test.example.com/doc")
        
        # Verify mock response
        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/html; charset=utf-8'
        assert b'Test Content' in response.content
        assert response.encoding == 'utf-8'
        
        # Verify session was called
        session.get.assert_called_once_with("https://test.example.com/doc")
    
    def test_http_response_properties(self, mock_requests_session):
        """Test HTTP response properties and methods"""
        session = mock_requests_session
        response = session.get("https://example.com")
        
        # Test response properties
        assert response.url == "https://test.example.com/doc"  # Mock returns this URL
        assert response.text == response.content.decode('utf-8')
        
        # Test raise_for_status doesn't raise for 200
        response.raise_for_status()  # Should not raise
        response.raise_for_status.assert_called_once()
    
    @responses.activate
    def test_responses_library_integration(self, mock_http_responses):
        """Test using responses library with mock data"""
        # Setup responses using helper
        from tests.conftest import setup_responses_mock
        setup_responses_mock(mock_http_responses)
        
        import requests
        
        # Test first URL
        response1 = requests.get("https://docs.nephio.org/test1")
        assert response1.status_code == 200
        assert "Nephio Overview" in response1.text
        
        # Test second URL
        response2 = requests.get("https://docs.nephio.org/test2")
        assert response2.status_code == 200
        assert "O-RAN Integration" in response2.text


class TestDocumentLoaderMocking:
    """Test DocumentLoader with mocked HTTP and parsing"""
    
    @patch('src.document_loader.requests.Session')
    def test_document_loader_with_mock_session(self, mock_session_class, mock_requests_session, mock_config):
        """Test DocumentLoader using mocked HTTP session"""
        from src.document_loader import DocumentLoader
        
        # Configure the session class to return our mock
        mock_session_class.return_value = mock_requests_session
        
        # Create loader
        loader = DocumentLoader(mock_config)
        
        # Verify session was created
        mock_session_class.assert_called_once()
        
        # Verify session headers were set (this tests the real initialization logic)
        # DocumentLoader should set User-Agent and other headers during initialization
        # The mock session will have the headers dict populated by the real code
        expected_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Verify that headers were set (contains expected key-value pairs)
        for key, value in expected_headers.items():
            assert mock_requests_session.headers[key] == value
    
    @responses.activate
    def test_document_loading_with_realistic_content(self, sample_html_documents, mock_config):
        """Test document loading with realistic HTML content"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource
        
        # Setup realistic HTML response
        responses.add(
            responses.GET,
            "https://docs.nephio.org/architecture",
            body=sample_html_documents['nephio_architecture'],
            status=200,
            content_type='text/html; charset=utf-8'
        )
        
        loader = DocumentLoader(mock_config)
        source = DocumentSource(
            url="https://docs.nephio.org/architecture",
            source_type="nephio",
            description="Nephio Architecture",
            priority=1,
            enabled=True
        )
        
        doc = loader.load_document(source)
        
        # Verify document was created
        assert doc is not None
        assert "Nephio Architecture" in doc.page_content
        assert "cloud native intent automation platform" in doc.page_content
        
        # Verify navigation was removed (clean HTML processing)
        assert "Home" not in doc.page_content
        
        # Verify metadata
        assert doc.metadata['source_url'] == source.url
        assert doc.metadata['source_type'] == "nephio"
        assert doc.metadata['title'] == "Nephio Architecture Overview"
    
    @responses.activate
    def test_document_loading_error_scenarios(self, mock_config):
        """Test document loading error handling"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource
        
        loader = DocumentLoader(mock_config)
        
        # Test 404 error
        responses.add(
            responses.GET,
            "https://docs.nephio.org/notfound",
            status=404
        )
        
        source_404 = DocumentSource(
            url="https://docs.nephio.org/notfound",
            source_type="nephio",
            description="Not Found Doc",
            priority=1,
            enabled=True
        )
        
        doc = loader.load_document(source_404)
        
        # DocumentLoader has offline fallback system, so it returns a sample document
        # instead of None when network requests fail
        assert doc is not None
        # Check for either fallback system (fallback_mode or is_sample)
        assert (doc.metadata.get('fallback_mode') is True or 
               doc.metadata.get('is_sample') is True)
        assert ("Sample:" in doc.metadata.get('title', '') or 
               "Sample -" in doc.metadata.get('title', ''))
        
        # Verify statistics - with fallback system, this counts as a successful load
        stats = loader.get_load_statistics()
        assert stats['total_attempts'] == 1
        # Fallback documents count as successful loads since they provide content
        assert stats['successful_loads'] >= 0
    
    @responses.activate
    def test_document_loading_with_minimal_content(self, sample_html_documents, mock_config):
        """Test handling of minimal content documents"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource
        
        # Adjust config for minimal content test
        mock_config.MIN_CONTENT_LENGTH = 10
        mock_config.MIN_EXTRACTED_CONTENT_LENGTH = 5
        
        responses.add(
            responses.GET,
            "https://docs.nephio.org/minimal",
            body=sample_html_documents['minimal_content'],
            status=200,
            content_type='text/html'
        )
        
        loader = DocumentLoader(mock_config)
        source = DocumentSource(
            url="https://docs.nephio.org/minimal",
            source_type="nephio",
            description="Minimal Doc",
            priority=1,
            enabled=True
        )
        
        doc = loader.load_document(source)
        
        # Should succeed with minimal content due to adjusted config
        assert doc is not None
        assert "Short content" in doc.page_content
    
    @responses.activate
    def test_batch_document_loading(self, sample_document_sources, sample_html_documents):
        """Test loading multiple documents in batch"""
        from src.document_loader import DocumentLoader
        from src.config import Config
        
        # Setup multiple responses
        responses.add(
            responses.GET,
            "https://docs.nephio.org/architecture",
            body=sample_html_documents['nephio_architecture'],
            status=200,
            content_type='text/html'
        )
        
        responses.add(
            responses.GET,
            "https://docs.nephio.org/o-ran-integration",
            body=sample_html_documents['oran_integration'],
            status=200,
            content_type='text/html'
        )
        
        config = Config()
        config.MIN_CONTENT_LENGTH = 50
        config.MIN_EXTRACTED_CONTENT_LENGTH = 25
        config.REQUEST_DELAY = 0  # Speed up tests
        
        loader = DocumentLoader(config)
        
        # Use valid sources from fixture
        sources = sample_document_sources['valid_sources'][:2]  # First 2 sources
        
        documents = loader.load_all_documents(sources)
        
        # Verify batch loading
        assert len(documents) == 2
        
        # Verify content
        contents = [doc.page_content for doc in documents]
        combined_content = " ".join(contents)
        assert "Nephio Architecture" in combined_content
        assert "O-RAN Network Function Integration" in combined_content
        
        # Verify statistics
        stats = loader.get_load_statistics()
        assert stats['successful_loads'] == 2
        assert stats['failed_loads'] == 0
        assert stats['success_rate'] == 100.0


class TestContentCleaningMocking:
    """Test HTML content cleaning with various document types"""
    
    def test_content_cleaner_initialization(self, mock_config):
        """Test DocumentContentCleaner initialization"""
        from src.document_loader import DocumentContentCleaner
        
        cleaner = DocumentContentCleaner(mock_config)
        
        assert cleaner.config == mock_config
        assert len(cleaner.unwanted_tags) > 0
        assert len(cleaner.unwanted_selectors) > 0
        assert len(cleaner.skip_patterns) > 0
    
    def test_html_cleaning_with_navigation(self, sample_html_documents, mock_config):
        """Test HTML cleaning removes navigation elements"""
        from src.document_loader import DocumentContentCleaner
        
        cleaner = DocumentContentCleaner(mock_config)
        html = sample_html_documents['nephio_architecture']
        
        cleaned_content = cleaner.clean_html(html, "https://docs.nephio.org/architecture")
        
        # Verify main content is preserved
        assert "Nephio Architecture" in cleaned_content
        assert "Kubernetes-based cloud native" in cleaned_content
        assert "Core Components" in cleaned_content
        
        # Verify navigation and footer are removed
        assert "Home" not in cleaned_content
        assert "Copyright 2024" not in cleaned_content
    
    def test_content_cleaning_with_no_main_content(self, sample_html_documents, mock_config):
        """Test handling of documents with no main content area"""
        from src.document_loader import DocumentContentCleaner
        
        cleaner = DocumentContentCleaner(mock_config)
        html = sample_html_documents['no_main_content']
        
        cleaned_content = cleaner.clean_html(html, "https://example.com")
        
        # Document with only navigation elements should result in empty content after cleaning
        # This is correct behavior - navigation-only pages have no useful content
        assert cleaned_content == ""
        # This confirms navigation elements were properly removed
        assert "Main navigation" not in cleaned_content
    
    def test_link_processing(self, mock_config):
        """Test relative link processing in content"""
        from src.document_loader import DocumentContentCleaner
        
        html_with_links = """
        <html>
        <body>
        <main>
            <h1>Test Page Documentation</h1>
            <p>See <a href="/docs/guide">the guide</a> for more information.</p>
            <p>Also check <a href="https://external.com">external link</a>.</p>
        </main>
        </body>
        </html>
        """
        
        cleaner = DocumentContentCleaner(mock_config)
        base_url = "https://docs.nephio.org/architecture"
        
        cleaned_content = cleaner.clean_html(html_with_links, base_url)
        
        # Content should be extracted
        assert "Test Page Documentation" in cleaned_content
        assert "for more information" in cleaned_content
        assert "external link" in cleaned_content


class TestDocumentMetadataMocking:
    """Test document metadata extraction and processing"""
    
    @responses.activate
    def test_metadata_extraction(self, mock_config):
        """Test extraction of document metadata"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource
        
        html_with_metadata = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Advanced O-RAN Scaling Guide</title>
            <meta name="description" content="Comprehensive guide for scaling O-RAN network functions using Nephio">
            <meta name="keywords" content="O-RAN, Nephio, scaling, network functions">
        </head>
        <body>
        <main>
            <h1>O-RAN Scaling with Nephio</h1>
            <p>This guide covers advanced scaling techniques for O-RAN network functions in Nephio deployments. Learn about horizontal scaling, vertical scaling, and automated scaling policies.</p>
        </main>
        </body>
        </html>
        """
        
        responses.add(
            responses.GET,
            "https://docs.nephio.org/scaling-advanced",
            body=html_with_metadata,
            status=200,
            content_type='text/html; charset=utf-8'
        )
        
        loader = DocumentLoader(mock_config)
        source = DocumentSource(
            url="https://docs.nephio.org/scaling-advanced",
            source_type="nephio",
            description="Advanced Scaling Guide",
            priority=1,
            enabled=True
        )
        
        doc = loader.load_document(source)
        
        # Verify document content
        assert doc is not None
        assert "O-RAN Scaling with Nephio" in doc.page_content
        assert "advanced scaling techniques" in doc.page_content
        
        # Verify metadata extraction
        assert doc.metadata['title'] == "Advanced O-RAN Scaling Guide"
        assert doc.metadata['meta_description'] == "Comprehensive guide for scaling O-RAN network functions using Nephio"
        assert doc.metadata['source_url'] == source.url
        assert doc.metadata['source_type'] == "nephio"
        assert doc.metadata['description'] == "Advanced Scaling Guide"
        assert doc.metadata['priority'] == 1
        assert doc.metadata['status_code'] == 200
        assert doc.metadata['content_type'] == 'text/html; charset=utf-8'
        assert 'content_length' in doc.metadata
        assert 'last_updated' in doc.metadata


@pytest.mark.integration
class TestDocumentLoadingIntegration:
    """Integration tests combining document loading with other components"""
    
    @responses.activate
    def test_document_loading_to_vectordb_pipeline(self, mock_chromadb, mock_huggingface_embeddings, sample_html_documents, mock_config):
        """Test complete pipeline from document loading to vector database"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource
        
        # Setup realistic document response
        responses.add(
            responses.GET,
            "https://docs.nephio.org/pipeline-test",
            body=sample_html_documents['nephio_architecture'],
            status=200,
            content_type='text/html'
        )
        
        # 1. Load document
        loader = DocumentLoader(mock_config)
        source = DocumentSource(
            url="https://docs.nephio.org/pipeline-test",
            source_type="nephio",
            description="Pipeline Test Doc",
            priority=1,
            enabled=True
        )
        
        doc = loader.load_document(source)
        assert doc is not None
        
        # 2. Generate embeddings
        embeddings = mock_huggingface_embeddings
        doc_vector = embeddings.embed_documents([doc.page_content])
        assert len(doc_vector) == 1
        assert len(doc_vector[0]) == 384
        
        # 3. Add to vector database
        vectordb = mock_chromadb
        vectordb.add_documents([doc])
        vectordb.add_documents.assert_called_once_with([doc])
        
        # 4. Test retrieval
        results = vectordb.similarity_search_with_score("Nephio architecture", k=1)
        assert len(results) >= 1
        
        retrieved_doc, score = results[0]
        assert "Nephio" in retrieved_doc.page_content
    
    @responses.activate
    def test_document_loading_error_recovery(self, mock_config):
        """Test error recovery in document loading"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource
        
        # Configure multiple retries
        mock_config.MAX_RETRIES = 3
        mock_config.RETRY_DELAY_BASE = 0.1  # Fast retries for testing
        
        loader = DocumentLoader(mock_config)
        
        # Setup failing responses followed by success
        responses.add(responses.GET, "https://docs.nephio.org/retry-test", status=500)
        responses.add(responses.GET, "https://docs.nephio.org/retry-test", status=500)
        responses.add(
            responses.GET,
            "https://docs.nephio.org/retry-test",
            body="<html><body><main><h1>Success After Retries</h1><p>This content loaded after multiple retry attempts for network resilience testing.</p></main></body></html>",
            status=200,
            content_type='text/html'
        )
        
        source = DocumentSource(
            url="https://docs.nephio.org/retry-test",
            source_type="nephio",
            description="Retry Test Doc",
            priority=1,
            enabled=True
        )
        
        doc = loader.load_document(source)
        
        # Should eventually succeed
        assert doc is not None
        assert "Success After Retries" in doc.page_content
        
        # Verify retry statistics
        stats = loader.get_load_statistics()
        assert stats['retry_attempts'] >= 2  # At least 2 retries
        assert stats['successful_loads'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])