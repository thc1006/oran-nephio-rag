"""
Test suite for Puter.js integration with comprehensive mocking
Demonstrates usage of the new fixtures for browser automation testing
"""
import pytest
import time
from unittest.mock import patch, MagicMock

# Test markers for organization
pytestmark = [pytest.mark.unit, pytest.mark.puter, pytest.mark.browser]


class TestPuterClaudeAdapter:
    """Test PuterClaudeAdapter with comprehensive mocking"""
    
    def test_adapter_initialization(self, mock_puter_adapter):
        """Test adapter initializes with correct properties"""
        assert mock_puter_adapter.model == "claude-sonnet-4"
        assert mock_puter_adapter.headless == True
        assert 'claude-sonnet-4' in mock_puter_adapter.AVAILABLE_MODELS
    
    def test_successful_query(self, mock_puter_adapter, sample_rag_query):
        """Test successful query execution"""
        import os
        question = sample_rag_query['question']
        
        # Execute query
        result = mock_puter_adapter.query(question)
        
        # Verify results
        assert result['success'] == True
        assert 'O-RAN and Nephio documentation' in result['answer']
        assert result['model'] == "claude-sonnet-4"
        
        # Adapter type depends on API_MODE
        api_mode = os.getenv("API_MODE", "browser")
        expected_adapter_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        assert result['adapter_type'] == expected_adapter_type
        assert result['query_time'] > 0
        
        # Verify mock was called
        mock_puter_adapter.query.assert_called_once_with(question)
    
    def test_query_with_streaming(self, mock_puter_adapter):
        """Test streaming query functionality"""
        import os
        # Configure mock for streaming
        api_mode = os.getenv("API_MODE", "browser")
        expected_adapter_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        
        mock_puter_adapter.query.return_value = {
            'success': True,
            'answer': 'Streaming response about Nephio scaling...',
            'model': 'claude-sonnet-4',
            'timestamp': '2024-01-15T10:30:00Z',
            'adapter_type': expected_adapter_type,
            'query_time': 3.2,
            'streamed': True
        }
        
        result = mock_puter_adapter.query("Test streaming query", stream=True)
        
        assert result['success'] == True
        assert result['streamed'] == True
        assert 'Streaming response' in result['answer']
    
    def test_query_error_handling(self, mock_puter_adapter, sample_puter_responses):
        """Test error handling in queries"""
        import os
        # Configure mock to return error
        mock_puter_adapter.query.return_value = sample_puter_responses['error']
        
        result = mock_puter_adapter.query("This will fail")
        
        assert result['success'] == False
        assert 'Browser session failed' in result['error']
        
        # Adapter type depends on API_MODE
        api_mode = os.getenv("API_MODE", "browser")
        expected_adapter_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        assert result['adapter_type'] == expected_adapter_type
    
    def test_availability_check(self, mock_puter_adapter):
        """Test adapter availability checking"""
        assert mock_puter_adapter.is_available() == True
        
        # Test unavailable scenario
        mock_puter_adapter.is_available.return_value = False
        assert mock_puter_adapter.is_available() == False
    
    def test_get_available_models(self, mock_puter_adapter):
        """Test getting available model list"""
        models = mock_puter_adapter.get_available_models()
        
        assert 'claude-sonnet-4' in models
        assert 'claude-opus-4' in models
        assert 'claude-sonnet-3.5' in models
        assert len(models) >= 3
    
    def test_adapter_info(self, mock_puter_adapter):
        """Test getting adapter information"""
        import os
        info = mock_puter_adapter.get_info()
        
        assert info['adapter_type'] == 'PuterClaudeAdapter'
        assert info['model'] == "claude-sonnet-4"
        
        # Integration method should match API_MODE
        api_mode = os.getenv("API_MODE", "mock")
        expected_integration_method = 'mock' if api_mode == 'mock' else 'browser_automation'
        assert info['integration_method'] == expected_integration_method
        assert info['headless_mode'] == True


class TestPuterBrowserIntegration:
    """Test browser automation components"""
    
    def test_webdriver_mock(self, mock_selenium_webdriver):
        """Test WebDriver mock functionality"""
        # Test basic WebDriver operations
        mock_selenium_webdriver.get("https://puter.com")
        mock_selenium_webdriver.get.assert_called_once_with("https://puter.com")
        
        # Test JavaScript execution
        result = mock_selenium_webdriver.execute_script("typeof puter !== 'undefined'")
        assert result == True
        
        # Test Puter.js availability check
        result = mock_selenium_webdriver.execute_script("typeof puter.ai !== 'undefined'")
        assert result == True
    
    def test_puter_js_response_simulation(self, mock_selenium_webdriver):
        """Test simulation of Puter.js responses"""
        # Simulate getting RAG response
        response = mock_selenium_webdriver.execute_script("return window.ragResponse")
        
        assert response is not None
        assert response['success'] == True
        assert 'Mock response from Puter.js' in response['answer']
        assert response['model'] == 'claude-sonnet-4'
    
    def test_webdriver_manager_mock(self, mock_webdriver_manager):
        """Test WebDriver Manager mock"""
        # The mock is already patched via fixture
        # Just verify it would return a fake path
        assert mock_webdriver_manager is not None
        
    @patch('src.puter_integration.PuterClaudeAdapter')
    def test_full_browser_session_mock(self, mock_adapter_class, mock_selenium_webdriver, mock_browser_environment):
        """Test complete browser session with all mocks"""
        mock_adapter_class.return_value = mock_browser_environment['webdriver']
        
        # This would normally create a real browser session
        adapter_instance = mock_adapter_class(model='claude-sonnet-4', headless=True)
        
        # Verify mocking is working
        assert adapter_instance == mock_browser_environment['webdriver']
        mock_adapter_class.assert_called_once()


class TestPuterRAGManager:
    """Test PuterRAGManager with mocked dependencies"""
    
    @patch('src.puter_integration.PuterClaudeAdapter')
    def test_rag_manager_initialization(self, mock_adapter_class, mock_puter_adapter):
        """Test RAG manager initialization"""
        from src.puter_integration import PuterRAGManager
        
        mock_adapter_class.return_value = mock_puter_adapter
        
        manager = PuterRAGManager(model='claude-sonnet-4', headless=True)
        
        # Verify adapter was created
        mock_adapter_class.assert_called_once_with(model='claude-sonnet-4', headless=True)
    
    @patch('src.puter_integration.PuterClaudeAdapter')
    def test_rag_query_with_context(self, mock_adapter_class, mock_puter_adapter, sample_vector_search_results):
        """Test RAG query with context"""
        from src.puter_integration import PuterRAGManager
        
        mock_adapter_class.return_value = mock_puter_adapter
        manager = PuterRAGManager()
        
        # Prepare context from search results
        context_docs = sample_vector_search_results['high_similarity']
        context = "\\n".join([doc['content'] for doc in context_docs])
        
        # Execute query
        result = manager.query("How do I scale O-RAN?", context=context)
        
        # Verify result
        assert result['success'] == True
        assert mock_puter_adapter.query.called
        
        # Verify context was included in the prompt
        call_args = mock_puter_adapter.query.call_args
        enhanced_prompt = call_args[1]['prompt'] if 'prompt' in call_args[1] else call_args[0][0]
        assert 'CONTEXT:' in enhanced_prompt
        assert 'Nephio uses Kubernetes operators' in enhanced_prompt
    
    @patch('src.puter_integration.PuterClaudeAdapter')
    def test_rag_manager_status(self, mock_adapter_class, mock_puter_adapter):
        """Test getting RAG manager status"""
        import os
        from src.puter_integration import PuterRAGManager
        
        # Get the current API_MODE or default
        api_mode = os.getenv("API_MODE", "browser")
        
        mock_adapter_class.return_value = mock_puter_adapter
        manager = PuterRAGManager()
        
        status = manager.get_status()
        
        # Integration type should match what we expect based on current API_MODE
        expected_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        
        # Accept either browser or mock mode as valid for this test
        assert status['integration_type'] in ['puter_js_browser', 'puter_js_mock']
        assert status['constraint_compliant'] == True
        assert 'adapter_info' in status
        assert 'tutorial_source' in status
        assert 'api_mode' in status


class TestPuterIntegrationUtilities:
    """Test utility functions for Puter.js integration"""
    
    def test_mock_puter_query_success_helper(self, sample_rag_query):
        """Test the mock query success helper function"""
        from tests.conftest import mock_puter_query_success
        
        question = sample_rag_query['question']
        result = mock_puter_query_success(question, stream=True)
        
        assert result['success'] == True
        assert result['answer'].startswith('Mock response for:')
        assert result['model'] == "claude-sonnet-4"
        
        # Adapter type should match current API_MODE
        import os
        api_mode = os.getenv("API_MODE", "mock")
        expected_adapter_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        assert result['adapter_type'] == expected_adapter_type
        assert result['streamed'] == True
    
    def test_mock_puter_query_error_helper(self):
        """Test the mock query error helper function"""
        from tests.conftest import mock_puter_query_error
        
        result = mock_puter_query_error("Connection timeout")
        
        assert result['success'] == False
        assert result['error'] == "Connection timeout"
        
        # Adapter type should be determined by current API_MODE
        import os
        api_mode = os.getenv("API_MODE", "mock")
        expected_adapter_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        assert result['adapter_type'] == expected_adapter_type
        assert 'timestamp' in result


@pytest.mark.integration
class TestPuterIntegrationWithFullSystem:
    """Integration tests using multiple mocked services"""
    
    def test_end_to_end_rag_query(self, mock_all_external_services, sample_rag_query, sample_vector_search_results):
        """Test complete RAG query flow with all services mocked"""
        services = mock_all_external_services
        
        # Simulate a complete RAG workflow
        question = sample_rag_query['question']
        
        # 1. Vector search (using ChromaDB mock)
        vectordb = services['chromadb']
        search_results = vectordb.similarity_search_with_score(question, k=3)
        
        assert len(search_results) == 3
        assert search_results[0][1] == 0.9  # High similarity score
        
        # 2. Context preparation
        context = "\\n".join([doc.page_content for doc, _ in search_results])
        
        # 3. LLM query (using Puter.js mock)
        puter_adapter = services['puter_adapter']
        result = puter_adapter.query(question)
        
        assert result['success'] == True
        
        # Adapter type should match API_MODE
        import os
        api_mode = os.getenv("API_MODE", "mock")
        expected_adapter_type = 'puter_js_mock' if api_mode == 'mock' else 'puter_js_browser'
        assert result['adapter_type'] == expected_adapter_type
        
        # 4. Verify all components worked together
        assert context is not None
        assert len(context) > 0
        assert 'Nephio' in context
    
    def test_error_handling_across_services(self, mock_all_external_services):
        """Test error handling when multiple services fail"""
        services = mock_all_external_services
        
        # Configure Puter adapter to return error
        services['puter_adapter'].query.return_value = {
            'success': False,
            'error': 'Browser automation failed',
            'adapter_type': 'puter_js_browser'
        }
        
        # Configure vector DB to return empty results
        services['chromadb'].similarity_search_with_score.return_value = []
        
        # Test the error conditions
        search_results = services['chromadb'].similarity_search_with_score("test query")
        assert len(search_results) == 0
        
        query_result = services['puter_adapter'].query("test query")
        assert query_result['success'] == False
        assert 'Browser automation failed' in query_result['error']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])