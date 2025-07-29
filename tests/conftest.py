"""
Shared test configuration and fixtures for O-RAN × Nephio RAG system
"""
import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock
from typing import Generator, Dict, Any

# Mock API key for all tests
TEST_API_KEY = "test-anthropic-api-key-12345"


@pytest.fixture(scope="session", autouse=True)
def mock_anthropic_api():
    """Mock Anthropic API key for all tests"""
    with patch.dict(os.environ, {'ANTHROPIC_API_KEY': TEST_API_KEY}):
        yield TEST_API_KEY


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config(temp_dir):
    """Mock configuration with test settings"""
    with patch('src.config.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config.ANTHROPIC_API_KEY = TEST_API_KEY
        mock_config.VECTOR_DB_PATH = os.path.join(temp_dir, "test_vectordb")
        mock_config.COLLECTION_NAME = "test_collection"
        mock_config.EMBEDDINGS_CACHE_PATH = os.path.join(temp_dir, "test_embeddings")
        mock_config.LOG_FILE = os.path.join(temp_dir, "test.log")
        mock_config.LOG_LEVEL = "DEBUG"
        mock_config.CLAUDE_MODEL = "claude-3-sonnet-20240229"
        mock_config.CLAUDE_MAX_TOKENS = 1000
        mock_config.CLAUDE_TEMPERATURE = 0.1
        mock_config.CHUNK_SIZE = 512
        mock_config.CHUNK_OVERLAP = 100
        mock_config.MAX_RETRIES = 2
        mock_config.REQUEST_TIMEOUT = 10
        mock_config.RETRIEVER_K = 3
        mock_config.RETRIEVER_FETCH_K = 6
        mock_config.RETRIEVER_LAMBDA_MULT = 0.7
        mock_config.MIN_CONTENT_LENGTH = 100
        mock_config.VERIFY_SSL = True
        
        mock_config_class.return_value = mock_config
        yield mock_config


@pytest.fixture
def mock_vectordb():
    """Mock vector database for testing"""
    mock_db = MagicMock()
    mock_db.similarity_search_with_score.return_value = [
        (MagicMock(
            page_content="Nephio is a Kubernetes-based cloud native intent automation platform.",
            metadata={"source": "https://docs.nephio.org/test1", "type": "nephio"}
        ), 0.9),
        (MagicMock(
            page_content="O-RAN provides open interfaces and architecture for RAN.",
            metadata={"source": "https://docs.nephio.org/test2", "type": "nephio"}
        ), 0.8)
    ]
    mock_db._collection.count.return_value = 100
    return mock_db


@pytest.fixture
def mock_embeddings():
    """Mock embeddings model for testing"""
    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 10
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    return mock_embeddings


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    from langchain.docstore.document import Document
    
    return [
        Document(
            page_content="Nephio is a Kubernetes-based cloud native intent automation platform designed to help service providers deploy and manage complex network functions across large scale edge deployments.",
            metadata={
                "source": "https://docs.nephio.org/docs/architecture/",
                "title": "Nephio Architecture Overview",
                "type": "nephio"
            }
        ),
        Document(
            page_content="O-RAN (Open Radio Access Network) provides open interfaces and architecture for RAN disaggregation, enabling multi-vendor interoperability and innovation in 5G networks.",
            metadata={
                "source": "https://docs.nephio.org/docs/network-architecture/o-ran-integration/",
                "title": "O-RAN Integration with Nephio",
                "type": "nephio"
            }
        ),
        Document(
            page_content="Network Function (NF) scaling in Nephio involves both horizontal scaling (scale-out) and vertical scaling (scale-up) to handle varying traffic loads efficiently.",
            metadata={
                "source": "https://docs.nephio.org/docs/guides/scaling/",
                "title": "NF Scaling Guide",
                "type": "nephio"
            }
        )
    ]


@pytest.fixture
def mock_document_sources():
    """Mock document sources for testing"""
    from src.config import DocumentSource
    
    return [
        DocumentSource(
            url="https://docs.nephio.org/test1",
            source_type="nephio",
            description="Test Nephio Doc 1",
            priority=1,
            enabled=True
        ),
        DocumentSource(
            url="https://docs.nephio.org/test2",
            source_type="nephio", 
            description="Test Nephio Doc 2",
            priority=2,
            enabled=True
        )
    ]


@pytest.fixture
def mock_http_responses():
    """Mock HTTP responses for document loading tests"""
    responses_data = {
        "https://docs.nephio.org/test1": {
            "status_code": 200,
            "content": """
            <html>
            <head><title>Test Doc 1</title></head>
            <body>
                <main>
                    <h1>Nephio Overview</h1>
                    <p>Nephio is a cloud native network automation platform.</p>
                    <p>It helps manage network functions at scale.</p>
                </main>
            </body>
            </html>
            """
        },
        "https://docs.nephio.org/test2": {
            "status_code": 200,
            "content": """
            <html>
            <head><title>Test Doc 2</title></head>
            <body>
                <article>
                    <h1>O-RAN Integration</h1>
                    <p>O-RAN provides open interfaces for radio access networks.</p>
                    <p>Integration with Nephio enables automated O-RAN deployments.</p>
                </article>
            </body>
            </html>
            """
        }
    }
    return responses_data


@pytest.fixture
def mock_claude_response():
    """Mock Claude API response for testing"""
    return {
        "content": [
            {
                "text": "Based on the provided documentation, Nephio is a Kubernetes-based cloud native intent automation platform that helps service providers deploy and manage network functions. For O-RAN scale-out, you would typically use Nephio's intent-driven automation to deploy additional O-RAN components across edge locations.",
                "type": "text"
            }
        ],
        "id": "msg_test_123",
        "model": "claude-3-sonnet-20240229",
        "role": "assistant",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "type": "message",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 150
        }
    }


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test"""
    yield
    # Clean up any test files that might have been created
    test_patterns = [
        "test_*.log",
        "test_vectordb*",
        "test_embeddings*"
    ]
    
    import glob
    for pattern in test_patterns:
        for file_path in glob.glob(pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path, ignore_errors=True)
            except Exception:
                pass  # Ignore cleanup errors


@pytest.fixture
def mock_system_status():
    """Mock system status for testing"""
    return {
        "vectordb_ready": True,
        "qa_chain_ready": True,
        "total_sources": 10,
        "enabled_sources": 8,
        "last_update": "2024-01-15T10:30:00",
        "vectordb_info": {
            "document_count": 150,
            "collection_name": "test_collection",
            "error": None
        },
        "load_statistics": {
            "success_rate": 95.5,
            "total_documents": 10,
            "successful_loads": 9,
            "failed_loads": 1
        }
    }


# Test utilities
def create_test_environment(temp_dir: str) -> Dict[str, str]:
    """Create a test environment with necessary directories"""
    dirs = {
        "logs": os.path.join(temp_dir, "logs"),
        "vectordb": os.path.join(temp_dir, "vectordb"),
        "embeddings": os.path.join(temp_dir, "embeddings")
    }
    
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs


def assert_log_contains(log_file: str, message: str):
    """Assert that log file contains specific message"""
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert message in content, f"Log message '{message}' not found in {log_file}"
    else:
        pytest.fail(f"Log file {log_file} does not exist")