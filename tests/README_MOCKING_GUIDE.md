# Comprehensive Mocking Guide for O-RAN × Nephio RAG System

This guide explains how to use the comprehensive mocking infrastructure for testing the O-RAN × Nephio RAG system without external dependencies.

## Overview

The mocking infrastructure provides complete isolation from external services:
- **Puter.js Browser Automation**: Selenium WebDriver and browser interactions
- **ChromaDB Vector Database**: All vector operations and storage
- **HTTP Requests**: Document fetching and API calls
- **HuggingFace Embeddings**: Text vectorization
- **File System Operations**: Temporary files and directories

## Quick Start

### Basic Test with All Services Mocked

```python
import pytest

def test_basic_rag_query(mock_all_external_services, sample_rag_query):
    \"\"\"Test a complete RAG query with all services mocked\"\"\"
    services = mock_all_external_services
    question = sample_rag_query['question']
    
    # 1. Vector search
    vectordb = services['chromadb']
    search_results = vectordb.similarity_search_with_score(question, k=3)
    
    # 2. LLM query
    llm_adapter = services['puter_adapter']
    response = llm_adapter.query(question)
    
    # Verify results
    assert len(search_results) == 3
    assert response['success'] == True
```

### Individual Service Testing

```python
def test_puter_integration_only(mock_puter_adapter):
    \"\"\"Test only Puter.js integration\"\"\"
    result = mock_puter_adapter.query("How to scale O-RAN?")
    
    assert result['success'] == True
    assert result['adapter_type'] == 'puter_js_browser'
    assert result['model'] == 'claude-sonnet-4'

def test_vector_database_only(mock_chromadb):
    \"\"\"Test only ChromaDB operations\"\"\"
    results = mock_chromadb.similarity_search_with_score("test query", k=5)
    
    assert len(results) == 3  # Mock returns 3 results
    for doc, score in results:
        assert 0 <= score <= 1
```

## Available Fixtures

### Core Service Mocks

| Fixture | Description | Usage |
|---------|-------------|-------|
| `mock_puter_adapter` | Puter.js Claude integration | Browser automation testing |
| `mock_chromadb` | ChromaDB vector database | Vector search and storage |
| `mock_huggingface_embeddings` | HuggingFace embeddings | Text vectorization |
| `mock_requests_session` | HTTP requests session | Document loading |
| `mock_selenium_webdriver` | Selenium WebDriver | Browser automation |

### Composite Fixtures

| Fixture | Description | Components |
|---------|-------------|-----------|
| `mock_all_external_services` | All services at once | All core services |
| `mock_full_rag_system` | Complete RAG system | Vector DB + Embeddings + LLM |
| `mock_browser_environment` | Browser automation | WebDriver + Manager |
| `mock_http_environment` | HTTP operations | Requests session |

### Test Data Fixtures

| Fixture | Description | Content |
|---------|-------------|---------|
| `sample_rag_query` | Standard RAG query | Question + expected keywords |
| `sample_puter_responses` | Puter.js responses | Success/error/timeout scenarios |
| `sample_vector_search_results` | Vector search results | High/medium/low similarity |
| `sample_html_documents` | HTML document types | Architecture/integration/minimal |
| `sample_document_sources` | Document sources | Valid/disabled/problematic |

## Test Patterns

### 1. Unit Tests with Full Mocking

```python
@pytest.mark.unit
class TestPuterAdapter:
    def test_successful_query(self, mock_puter_adapter, sample_rag_query):
        result = mock_puter_adapter.query(sample_rag_query['question'])
        assert result['success'] == True
        
    def test_error_handling(self, mock_puter_adapter, sample_puter_responses):
        mock_puter_adapter.query.return_value = sample_puter_responses['error']
        result = mock_puter_adapter.query("test")
        assert result['success'] == False
```

### 2. Integration Tests with Selective Mocking

```python
@pytest.mark.integration
@responses.activate
def test_document_to_vector_pipeline(mock_chromadb, mock_huggingface_embeddings):
    # Use real HTTP with mocked responses
    responses.add(responses.GET, "https://test.com", body="<html>...</html>")
    
    # Mock only vector operations
    # ... test implementation
```

### 3. End-to-End Tests with Complete Mocking

```python
@pytest.mark.integration
def test_complete_workflow(mock_all_external_services, sample_html_documents):
    services = mock_all_external_services
    
    # Test complete RAG pipeline
    # 1. Document loading (mocked HTTP)
    # 2. Embedding generation (mocked)
    # 3. Vector storage (mocked)
    # 4. Query processing (mocked)
    # 5. LLM response (mocked)
```

## Mock Configuration

### Configuring Mock Responses

```python
def test_custom_puter_response(mock_puter_adapter):
    # Configure custom response
    mock_puter_adapter.query.return_value = {
        'success': True,
        'answer': 'Custom response for testing',
        'model': 'claude-sonnet-4',
        'query_time': 1.5
    }
    
    result = mock_puter_adapter.query("test")
    assert result['answer'] == 'Custom response for testing'

def test_custom_vector_results(mock_chromadb):
    # Configure custom search results
    from unittest.mock import MagicMock
    custom_results = [
        (MagicMock(page_content="Custom doc", metadata={"source": "test"}), 0.95)
    ]
    mock_chromadb.similarity_search_with_score.return_value = custom_results
    
    results = mock_chromadb.similarity_search_with_score("query", k=1)
    assert len(results) == 1
    assert results[0][1] == 0.95
```

### Simulating Errors

```python
def test_vector_database_error(mock_chromadb):
    # Configure database error
    mock_chromadb.similarity_search_with_score.side_effect = Exception("DB unavailable")
    
    with pytest.raises(Exception) as exc_info:
        mock_chromadb.similarity_search_with_score("test", k=1)
    assert "DB unavailable" in str(exc_info.value)

def test_puter_timeout(mock_puter_adapter, sample_puter_responses):
    mock_puter_adapter.query.return_value = sample_puter_responses['timeout']
    
    result = mock_puter_adapter.query("test")
    assert result['success'] == False
    assert 'timed out' in result['error']
```

## HTTP Mocking Patterns

### Using responses Library

```python
import responses

@responses.activate
def test_document_loading():
    # Mock HTTP responses
    responses.add(
        responses.GET,
        "https://docs.nephio.org/test",
        body="<html><body>Test content</body></html>",
        status=200,
        content_type='text/html'
    )
    
    import requests
    response = requests.get("https://docs.nephio.org/test")
    assert response.status_code == 200
```

### Using Mock Session

```python
def test_with_mock_session(mock_requests_session):
    # Configure custom response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<html>Custom content</html>"
    mock_requests_session.get.return_value = mock_response
    
    response = mock_requests_session.get("https://test.com")
    assert response.status_code == 200
```

## Advanced Testing Scenarios

### Testing Error Recovery

```python
def test_system_recovery(mock_all_external_services):
    services = mock_all_external_services
    
    # Simulate failure
    services['vectordb'].similarity_search_with_score.side_effect = Exception("Failure")
    
    # Test failure handling
    with pytest.raises(Exception):
        services['vectordb'].similarity_search_with_score("test", k=1)
    
    # Simulate recovery
    services['vectordb'].similarity_search_with_score.side_effect = None
    services['vectordb'].similarity_search_with_score.return_value = []
    
    # Test recovery
    results = services['vectordb'].similarity_search_with_score("test", k=1)
    assert results == []
```

### Performance Testing

```python
def test_performance_simulation(mock_all_external_services):
    services = mock_all_external_services
    
    # Configure different response times
    fast_response = {'success': True, 'query_time': 0.5, 'answer': 'Fast'}
    slow_response = {'success': True, 'query_time': 5.0, 'answer': 'Slow'}
    
    services['puter_adapter'].query.side_effect = [fast_response, slow_response]
    
    # Test performance characteristics
    result1 = services['puter_adapter'].query("simple query")
    result2 = services['puter_adapter'].query("complex query")
    
    assert result1['query_time'] < result2['query_time']
```

### Testing Concurrent Operations

```python
def test_concurrent_queries(mock_all_external_services):
    services = mock_all_external_services
    
    queries = ["query1", "query2", "query3"]
    results = []
    
    for i, query in enumerate(queries):
        # Configure unique response for each query
        services['puter_adapter'].query.return_value = {
            'success': True,
            'answer': f'Response {i}',
            'model': 'claude-sonnet-4'
        }
        
        result = services['puter_adapter'].query(query)
        results.append(result)
    
    assert len(results) == 3
    assert all(r['success'] for r in results)
```

## Test Markers

Use pytest markers to organize tests:

```python
@pytest.mark.unit          # Fast unit tests with full mocking
@pytest.mark.integration   # Integration tests with selective mocking
@pytest.mark.slow          # Tests that take >5 seconds
@pytest.mark.browser       # Tests requiring browser automation
@pytest.mark.network       # Tests requiring network access
@pytest.mark.puter         # Puter.js specific tests
@pytest.mark.vectordb      # Vector database tests
@pytest.mark.llm           # LLM API tests
```

Run specific test types:

```bash
# Run only unit tests
pytest -m unit

# Run integration tests but skip slow ones
pytest -m "integration and not slow"

# Run all Puter.js tests
pytest -m puter

# Run with coverage
pytest --cov=src --cov-report=html -m unit
```

## Helper Functions

The mocking infrastructure includes helper functions:

```python
from conftest import (
    mock_puter_query_success,
    mock_puter_query_error,
    create_mock_document,
    setup_responses_mock
)

def test_with_helpers():
    # Create success response
    success_response = mock_puter_query_success("test query", stream=True)
    assert success_response['success'] == True
    assert success_response['streamed'] == True
    
    # Create error response
    error_response = mock_puter_query_error("Connection failed")
    assert error_response['success'] == False
    
    # Create mock document
    doc = create_mock_document("content", "https://test.com", "nephio")
    assert doc['page_content'] == "content"
```

## Best Practices

1. **Use Appropriate Fixtures**: Choose the right level of mocking for your test
2. **Configure Realistic Responses**: Mock responses should reflect real system behavior
3. **Test Error Scenarios**: Include failure cases in your tests
4. **Verify Mock Calls**: Assert that mocks were called as expected
5. **Reset Mock State**: Use fresh mocks for each test
6. **Use Test Markers**: Organize tests with appropriate markers
7. **Keep Tests Fast**: Unit tests should complete in <1 second
8. **Document Custom Mocks**: Explain complex mock configurations

## Common Patterns

### Testing with Context

```python
def test_rag_with_context(mock_full_rag_system, sample_vector_search_results):
    rag_system = mock_full_rag_system
    
    # Prepare context from vector search
    high_sim_docs = sample_vector_search_results['high_similarity']
    context = "\\n".join([doc['content'] for doc in high_sim_docs])
    
    # Query with context
    llm_adapter = rag_system['llm_adapter']
    response = llm_adapter.query(f"Context: {context}\\nQuestion: How to scale?")
    
    assert response['success'] == True
```

### Testing Configuration Variations

```python
@pytest.mark.parametrize("model,expected_dim", [
    ("all-MiniLM-L6-v2", 384),
    ("all-mpnet-base-v2", 768),
])
def test_different_embedding_models(mock_huggingface_embeddings, model, expected_dim):
    mock_huggingface_embeddings.model_name = model
    mock_huggingface_embeddings.embed_query.return_value = [0.1] * expected_dim
    
    vector = mock_huggingface_embeddings.embed_query("test")
    assert len(vector) == expected_dim
```

This comprehensive mocking infrastructure enables thorough testing of the O-RAN × Nephio RAG system while maintaining fast, reliable, and deterministic tests.