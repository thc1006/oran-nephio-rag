"""
Shared test configuration and fixtures for O-RAN × Nephio RAG system
Comprehensive mocking for all external services and dependencies
"""

import importlib
import os
import shutil
import tempfile
import time
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
import responses

# Mock API key for all tests
TEST_API_KEY = "test-anthropic-api-key-12345"

# Test configuration constants
TEST_VECTOR_DB_PATH = "./test_vectordb"
TEST_COLLECTION_NAME = "test_collection"
TEST_MODEL_NAME = "claude-sonnet-4"
TEST_EMBEDDINGS_DIM = 384


# Guard function to prevent API_MODE changes during tests
def prevent_api_mode_change(new_value):
    """Prevent API_MODE from being changed to anything other than 'mock' during tests"""
    if new_value != "mock":
        raise RuntimeError(
            f"API_MODE cannot be changed to '{new_value}' during tests. "
            f"Tests must run in 'mock' mode for stability and consistency. "
            f"Current API_MODE is locked to 'mock'."
        )


@pytest.fixture(scope="session", autouse=True)
def enforce_test_environment():
    """Enforce consistent test environment settings for entire session"""
    # Store original values
    original_api_mode = os.getenv("API_MODE")
    original_api_key = os.getenv("ANTHROPIC_API_KEY")

    # Set test environment
    os.environ["API_MODE"] = "mock"
    os.environ["ANTHROPIC_API_KEY"] = TEST_API_KEY

    try:
        yield {"API_MODE": "mock", "ANTHROPIC_API_KEY": TEST_API_KEY}
    finally:
        # Restore original values only if they existed
        if original_api_mode is not None:
            os.environ["API_MODE"] = original_api_mode
        else:
            os.environ.pop("API_MODE", None)

        if original_api_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = original_api_key
        else:
            os.environ.pop("ANTHROPIC_API_KEY", None)


@pytest.fixture(scope="session", autouse=True)
def mock_anthropic_api():
    """Mock Anthropic API key for all tests"""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": TEST_API_KEY}):
        yield TEST_API_KEY


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration between tests to prevent state leakage"""
    import sys

    # Store original environment variables that might affect config
    original_env = {}
    env_vars_to_track = [
        "ANTHROPIC_API_KEY",
        "API_MODE",
        "BROWSER_HEADLESS",
        "BROWSER_TIMEOUT",
        "BROWSER_WAIT_TIME",
        "PUTER_MODEL",
        "CLAUDE_MODEL",
        "CLAUDE_TEMPERATURE",
        "VECTOR_DB_PATH",
        "EMBEDDINGS_CACHE_PATH",
        "LOG_LEVEL",
    ]

    for var in env_vars_to_track:
        if var in os.environ:
            original_env[var] = os.environ[var]

    # CRITICAL: Set API_MODE to 'mock' for all tests to ensure consistency
    # This prevents adapter type mismatches and cross-test interference
    os.environ["API_MODE"] = "mock"

    yield

    # After each test, clean up any module imports and reload config
    modules_to_reload = ["src.config", "src.document_loader", "src.oran_nephio_rag", "src.oran_nephio_rag_fixed"]

    for module_name in modules_to_reload:
        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
            except Exception:
                # If reload fails, remove from modules to force fresh import
                try:
                    del sys.modules[module_name]
                except KeyError:
                    pass

    # Clear any cached instances or global state that might interfere
    try:
        import gc

        gc.collect()  # Force garbage collection to clear any cached instances
    except Exception:
        pass

    # Restore original environment (but keep TEST_API_KEY for session and API_MODE as mock)
    for var in env_vars_to_track:
        if var == "ANTHROPIC_API_KEY":
            continue  # Keep the test API key
        if var == "API_MODE":
            # Always keep API_MODE as mock for test stability
            os.environ["API_MODE"] = "mock"
            continue
        if var in original_env:
            os.environ[var] = original_env[var]
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config(temp_dir):
    """Mock configuration with test settings"""
    with patch("src.config.Config") as mock_config_class:
        mock_config = MagicMock()
        mock_config.ANTHROPIC_API_KEY = TEST_API_KEY
        mock_config.VECTOR_DB_PATH = os.path.join(temp_dir, "test_vectordb")
        mock_config.COLLECTION_NAME = TEST_COLLECTION_NAME
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
        mock_config.MIN_EXTRACTED_CONTENT_LENGTH = 50
        mock_config.MIN_LINE_LENGTH = 10
        mock_config.MIN_KEYWORD_COUNT = 1
        mock_config.MAX_LINE_MERGE_LENGTH = 100
        mock_config.RETRY_DELAY_BASE = 1
        mock_config.MAX_RETRY_DELAY = 10
        mock_config.REQUEST_DELAY = 0.1
        mock_config.VERIFY_SSL = True

        mock_config_class.return_value = mock_config
        yield mock_config


@pytest.fixture
def mock_vectordb():
    """Mock vector database for testing"""
    mock_db = MagicMock()
    mock_db.similarity_search_with_score.return_value = [
        (
            MagicMock(
                page_content="Nephio is a Kubernetes-based cloud native intent automation platform.",
                metadata={"source": "https://docs.nephio.org/test1", "type": "nephio"},
            ),
            0.9,
        ),
        (
            MagicMock(
                page_content="O-RAN provides open interfaces and architecture for RAN.",
                metadata={"source": "https://docs.nephio.org/test2", "type": "nephio"},
            ),
            0.8,
        ),
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
                "type": "nephio",
            },
        ),
        Document(
            page_content="O-RAN (Open Radio Access Network) provides open interfaces and architecture for RAN disaggregation, enabling multi-vendor interoperability and innovation in 5G networks.",
            metadata={
                "source": "https://docs.nephio.org/docs/network-architecture/o-ran-integration/",
                "title": "O-RAN Integration with Nephio",
                "type": "nephio",
            },
        ),
        Document(
            page_content="Network Function (NF) scaling in Nephio involves both horizontal scaling (scale-out) and vertical scaling (scale-up) to handle varying traffic loads efficiently.",
            metadata={
                "source": "https://docs.nephio.org/docs/guides/scaling/",
                "title": "NF Scaling Guide",
                "type": "nephio",
            },
        ),
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
            enabled=True,
        ),
        DocumentSource(
            url="https://docs.nephio.org/test2",
            source_type="nephio",
            description="Test Nephio Doc 2",
            priority=2,
            enabled=True,
        ),
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
            """,
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
            """,
        },
    }
    return responses_data


# ============================================================================
# COMPREHENSIVE EXTERNAL SERVICE MOCKS
# ============================================================================


@pytest.fixture
def mock_selenium_webdriver():
    """Mock Selenium WebDriver for Puter.js browser automation"""
    mock_driver = MagicMock()

    # Mock WebDriver methods
    mock_driver.get = MagicMock()
    mock_driver.quit = MagicMock()
    mock_driver.execute_script = MagicMock()
    mock_driver.implicitly_wait = MagicMock()

    # Mock JavaScript execution results for Puter.js
    def mock_js_execution(script):
        if "typeof puter !== 'undefined'" in script:
            return True
        elif "typeof puter.ai !== 'undefined'" in script:
            return True
        elif "window.ragProcessing" in script:
            return False  # Not processing
        elif "window.ragResponse" in script:
            return {
                "answer": "Mock response from Puter.js Claude integration",
                "model": "claude-sonnet-4",
                "timestamp": "2024-01-15T10:30:00Z",
                "success": True,
            }
        elif "window.ragError" in script:
            return None
        return None

    mock_driver.execute_script.side_effect = mock_js_execution

    return mock_driver


@pytest.fixture
def mock_webdriver_manager():
    """Mock WebDriver Manager for Chrome driver installation"""
    with patch("webdriver_manager.chrome.ChromeDriverManager") as mock_manager:
        mock_manager.return_value.install.return_value = "/fake/chromedriver/path"
        yield mock_manager


@pytest.fixture
def mock_puter_adapter():
    """Mock PuterClaudeAdapter for browser automation testing"""
    import os

    mock_adapter = MagicMock()

    # Mock adapter properties
    mock_adapter.model = TEST_MODEL_NAME
    mock_adapter.headless = True
    mock_adapter.AVAILABLE_MODELS = ["claude-sonnet-4", "claude-opus-4", "claude-sonnet-3.5"]

    # Determine adapter type based on current API_MODE (should always be 'mock' in tests)
    api_mode = os.getenv("API_MODE", "mock")  # Default to mock for tests
    adapter_type = "puter_js_mock" if api_mode == "mock" else "puter_js_browser"
    integration_method = "mock" if api_mode == "mock" else "browser_automation"

    # Mock adapter methods
    mock_adapter.query.return_value = {
        "success": True,
        "answer": "Based on the O-RAN and Nephio documentation, here is the information you requested...",
        "model": TEST_MODEL_NAME,
        "timestamp": "2024-01-15T10:30:00Z",
        "adapter_type": adapter_type,
        "query_time": 2.5,
        "streamed": False,
    }

    mock_adapter.is_available.return_value = True
    mock_adapter.get_available_models.return_value = ["claude-sonnet-4", "claude-opus-4", "claude-sonnet-3.5"]
    mock_adapter.get_info.return_value = {
        "adapter_type": "PuterClaudeAdapter",
        "model": TEST_MODEL_NAME,
        "available_models": ["claude-sonnet-4", "claude-opus-4"],
        "integration_method": integration_method,
        "headless_mode": True,
        "mock_mode": api_mode == "mock",
        "selenium_available": api_mode != "mock",
    }

    return mock_adapter


@pytest.fixture
def mock_chromadb():
    """Comprehensive ChromaDB mock for vector database operations"""

    # Mock collection
    mock_collection = MagicMock()
    mock_collection.name = TEST_COLLECTION_NAME
    mock_collection.count.return_value = 150

    # Mock query results
    mock_query_result = {
        "ids": [["doc1", "doc2", "doc3"]],
        "distances": [[0.1, 0.3, 0.5]],
        "documents": [
            [
                "Nephio is a Kubernetes-based cloud native intent automation platform.",
                "O-RAN provides open interfaces and architecture for RAN disaggregation.",
                "Network Function scaling involves both horizontal and vertical scaling strategies.",
            ]
        ],
        "metadatas": [
            [
                {"source": "https://docs.nephio.org/architecture", "type": "nephio"},
                {"source": "https://docs.nephio.org/o-ran", "type": "nephio"},
                {"source": "https://docs.nephio.org/scaling", "type": "nephio"},
            ]
        ],
    }

    mock_collection.query.return_value = mock_query_result
    mock_collection.add.return_value = None
    mock_collection.delete.return_value = None
    mock_collection.get.return_value = mock_query_result

    # Mock client
    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client.list_collections.return_value = [mock_collection]
    mock_client.delete_collection.return_value = None

    # Mock Chroma class
    mock_chroma = MagicMock()
    mock_chroma._client = mock_client
    mock_chroma._collection = mock_collection
    mock_chroma.similarity_search_with_score.return_value = [
        (
            MagicMock(
                page_content="Nephio is a Kubernetes-based cloud native intent automation platform.",
                metadata={"source": "https://docs.nephio.org/architecture", "type": "nephio"},
            ),
            0.9,
        ),
        (
            MagicMock(
                page_content="O-RAN provides open interfaces and architecture for RAN disaggregation.",
                metadata={"source": "https://docs.nephio.org/o-ran", "type": "nephio"},
            ),
            0.8,
        ),
        (
            MagicMock(
                page_content="Network Function scaling involves both horizontal and vertical scaling strategies.",
                metadata={"source": "https://docs.nephio.org/scaling", "type": "nephio"},
            ),
            0.7,
        ),
    ]
    mock_chroma.add_documents.return_value = None
    mock_chroma.delete.return_value = None

    return mock_chroma


@pytest.fixture
def mock_huggingface_embeddings():
    """Mock HuggingFace embeddings model"""
    mock_embeddings = MagicMock()

    # Mock embeddings with consistent dimensions - using Mock objects for assertion support
    mock_embeddings.embed_documents = MagicMock(
        side_effect=lambda texts: [[0.1 + i * 0.01] * TEST_EMBEDDINGS_DIM for i in range(len(texts))]
    )

    mock_embeddings.embed_query = MagicMock(side_effect=lambda text: [0.5] * TEST_EMBEDDINGS_DIM)

    mock_embeddings.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    mock_embeddings.cache_folder = "./test_embeddings_cache"

    return mock_embeddings


@pytest.fixture
def mock_requests_session():
    """Mock requests Session for HTTP operations"""
    mock_session = MagicMock()

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/html; charset=utf-8"}
    mock_response.content = b"<html><body><h1>Test Content</h1><p>Mock response content with test content for Nephio and additional details to meet minimum length requirements for content validation. This content should be long enough to pass the 100-byte minimum requirement.</p></body></html>"
    mock_response.text = mock_response.content.decode("utf-8")
    mock_response.url = "https://test.example.com/doc"
    mock_response.encoding = "utf-8"
    mock_response.raise_for_status = MagicMock()

    mock_session.get.return_value = mock_response
    mock_session.headers = {}
    mock_session.max_redirects = 5
    mock_session.close = MagicMock()

    return mock_session


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude API client (fallback for non-Puter integrations)"""
    mock_client = MagicMock()

    # Mock message response
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Mock Claude response based on provided context.")]
    mock_message.id = "msg_test_123"
    mock_message.model = "claude-3-sonnet-20240229"
    mock_message.role = "assistant"
    mock_message.stop_reason = "end_turn"
    mock_message.usage = MagicMock(input_tokens=100, output_tokens=50)

    mock_client.messages.create.return_value = mock_message

    return mock_client


# ============================================================================
# COMPOSITE FIXTURES FOR DIFFERENT TESTING SCENARIOS
# ============================================================================


@pytest.fixture
def mock_full_rag_system(mock_chromadb, mock_huggingface_embeddings, mock_puter_adapter):
    """Complete RAG system mock with all external dependencies"""
    return {"vectordb": mock_chromadb, "embeddings": mock_huggingface_embeddings, "llm_adapter": mock_puter_adapter}


@pytest.fixture
def mock_browser_environment(mock_selenium_webdriver, mock_webdriver_manager):
    """Complete browser automation environment mock"""
    return {"webdriver": mock_selenium_webdriver, "webdriver_manager": mock_webdriver_manager}


@pytest.fixture
def mock_http_environment(mock_requests_session):
    """Complete HTTP environment mock for document loading"""
    return {"session": mock_requests_session}


# ============================================================================
# TEST DATA FIXTURES FOR VARIOUS SCENARIOS
# ============================================================================


@pytest.fixture
def sample_rag_query():
    """Sample RAG query for testing"""
    return {
        "question": "How do I scale O-RAN network functions using Nephio?",
        "expected_keywords": ["scale", "o-ran", "nephio", "network function"],
        "context_docs": 3,
        "min_response_length": 100,
    }


@pytest.fixture
def sample_puter_responses():
    """Sample Puter.js API responses for different scenarios"""
    # Determine adapter type based on current API_MODE (should be 'mock' in tests)
    api_mode = os.getenv("API_MODE", "mock")  # Default to mock for tests
    adapter_type = "puter_js_mock" if api_mode == "mock" else "puter_js_browser"

    return {
        "success": {
            "success": True,
            "answer": "To scale O-RAN network functions using Nephio, you need to create a ProvisioningRequest CRD with the desired replica count and resource constraints.",
            "model": "claude-sonnet-4",
            "timestamp": "2024-01-15T10:30:00Z",
            "adapter_type": adapter_type,
            "query_time": 2.1,
            "streamed": False,
        },
        "error": {
            "success": False,
            "error": "Browser session failed to initialize",
            "adapter_type": adapter_type,
            "timestamp": "2024-01-15T10:30:00Z",
        },
        "timeout": {"success": False, "error": "Query timed out after 60 seconds", "adapter_type": adapter_type},
    }


@pytest.fixture
def sample_vector_search_results():
    """Sample vector database search results"""
    return {
        "high_similarity": [
            {
                "content": "Nephio uses Kubernetes operators to manage network function lifecycle and scaling.",
                "metadata": {"source": "https://docs.nephio.org/operators", "type": "nephio"},
                "score": 0.95,
            },
            {
                "content": "O-RAN scale-out requires coordination between RIC, CU, DU, and RU components.",
                "metadata": {"source": "https://docs.nephio.org/o-ran-scale", "type": "nephio"},
                "score": 0.89,
            },
        ],
        "medium_similarity": [
            {
                "content": "Container orchestration in cloud-native environments supports horizontal scaling.",
                "metadata": {"source": "https://docs.nephio.org/containers", "type": "nephio"},
                "score": 0.72,
            }
        ],
        "low_similarity": [
            {
                "content": "General information about Kubernetes deployment strategies.",
                "metadata": {"source": "https://kubernetes.io/docs", "type": "external"},
                "score": 0.45,
            }
        ],
    }


@pytest.fixture
def sample_document_sources():
    """Extended sample document sources for testing"""
    from src.config import DocumentSource

    return {
        "valid_sources": [
            DocumentSource(
                url="https://docs.nephio.org/architecture",
                source_type="nephio",
                description="Nephio Architecture Overview",
                priority=1,
                enabled=True,
            ),
            DocumentSource(
                url="https://docs.nephio.org/o-ran-integration",
                source_type="nephio",
                description="O-RAN Integration Guide",
                priority=2,
                enabled=True,
            ),
            DocumentSource(
                url="https://docs.nephio.org/scaling-guide",
                source_type="nephio",
                description="Network Function Scaling Guide",
                priority=3,
                enabled=True,
            ),
        ],
        "disabled_sources": [
            DocumentSource(
                url="https://docs.nephio.org/deprecated",
                source_type="nephio",
                description="Deprecated Documentation",
                priority=5,
                enabled=False,
            )
        ],
        "problematic_sources": [
            DocumentSource(
                url="https://nonexistent.nephio.org/404",
                source_type="nephio",
                description="Non-existent Document",
                priority=5,
                enabled=True,
            )
        ],
    }


@pytest.fixture
def sample_html_documents():
    """Sample HTML documents with various content types"""
    return {
        "nephio_architecture": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nephio Architecture Overview</title>
            <meta name="description" content="Comprehensive guide to Nephio architecture">
        </head>
        <body>
            <nav><a href="/">Home</a></nav>
            <main class="content">
                <h1>Nephio Architecture</h1>
                <p>Nephio is a Kubernetes-based cloud native intent automation platform designed for telecom network management.</p>
                <h2>Core Components</h2>
                <ul>
                    <li>Porch for configuration management</li>
                    <li>Nephio Controllers for automation</li>
                    <li>Resource Backend for inventory</li>
                </ul>
                <h2>Scaling Strategies</h2>
                <p>Network functions can be scaled horizontally using replica sets and vertically by adjusting resource limits.</p>
            </main>
            <footer>Copyright 2024</footer>
        </body>
        </html>
        """,
        "oran_integration": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>O-RAN Integration with Nephio</title>
        </head>
        <body>
            <article>
                <h1>O-RAN Network Function Integration</h1>
                <p>This guide covers the integration of O-RAN network functions with Nephio for automated deployment and scaling.</p>
                <section>
                    <h2>Scale-out Procedures</h2>
                    <p>To scale out O-RAN components:</p>
                    <ol>
                        <li>Create ProvisioningRequest CRD</li>
                        <li>Specify target cluster and resource requirements</li>
                        <li>Apply scaling policies</li>
                    </ol>
                    <code>kubectl apply -f scaling-config.yaml</code>
                </section>
            </article>
        </body>
        </html>
        """,
        "minimal_content": """
        <html><body><p>Short content</p></body></html>
        """,
        "no_main_content": """
        <!DOCTYPE html>
        <html>
        <head><title>Navigation Only</title></head>
        <body>
            <nav>Main navigation</nav>
            <header>Site header</header>
            <footer>Site footer</footer>
        </body>
        </html>
        """,
    }


@pytest.fixture
def mock_claude_response():
    """Mock Claude API response for testing"""
    return {
        "content": [
            {
                "text": "Based on the provided documentation, Nephio is a Kubernetes-based cloud native intent automation platform that helps service providers deploy and manage network functions. For O-RAN scale-out, you would typically use Nephio's intent-driven automation to deploy additional O-RAN components across edge locations.",
                "type": "text",
            }
        ],
        "id": "msg_test_123",
        "model": "claude-3-sonnet-20240229",
        "role": "assistant",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "type": "message",
        "usage": {"input_tokens": 100, "output_tokens": 150},
    }


# ============================================================================
# CONTEXT MANAGERS FOR COMPREHENSIVE MOCKING
# ============================================================================


@pytest.fixture
def mock_all_external_services(
    mock_chromadb,
    mock_huggingface_embeddings,
    mock_puter_adapter,
    mock_selenium_webdriver,
    mock_webdriver_manager,
    mock_requests_session,
):
    """Context manager that mocks all external services at once"""
    patches = [
        patch("src.puter_integration.PuterClaudeAdapter", return_value=mock_puter_adapter),
        patch("selenium.webdriver.Chrome", return_value=mock_selenium_webdriver),
        patch("webdriver_manager.chrome.ChromeDriverManager", return_value=mock_webdriver_manager),
        patch("chromadb.Client", return_value=mock_chromadb._client),
        patch("langchain.vectorstores.Chroma", return_value=mock_chromadb),
        patch("langchain.embeddings.HuggingFaceEmbeddings", return_value=mock_huggingface_embeddings),
        patch("requests.Session", return_value=mock_requests_session),
    ]

    started_patches = []
    try:
        for p in patches:
            started_patches.append(p.start())
        yield {
            "puter_adapter": mock_puter_adapter,
            "llm_adapter": mock_puter_adapter,
            "chromadb": mock_chromadb,
            "vectordb": mock_chromadb,
            "embeddings": mock_huggingface_embeddings,
            "session": mock_requests_session,
            "webdriver": mock_selenium_webdriver,
        }
    finally:
        for p in started_patches:
            try:
                p.stop()
            except RuntimeError:
                pass  # Already stopped


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test"""
    yield
    # Clean up any test files that might have been created
    test_patterns = ["test_*.log", "test_vectordb*", "test_embeddings*", "test_*.html", "chromedriver*"]

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
        "vectordb_info": {"document_count": 150, "collection_name": TEST_COLLECTION_NAME, "error": None},
        "load_statistics": {"success_rate": 95.5, "total_documents": 10, "successful_loads": 9, "failed_loads": 1},
        "llm_adapter_info": {
            "adapter_type": "puter_js_browser",
            "model": TEST_MODEL_NAME,
            "available": True,
            "last_query": "2024-01-15T10:25:00",
        },
    }


# ============================================================================
# TEST UTILITIES AND HELPER FUNCTIONS
# ============================================================================


def create_test_environment(temp_dir: str) -> Dict[str, str]:
    """Create a test environment with necessary directories"""
    dirs = {
        "logs": os.path.join(temp_dir, "logs"),
        "vectordb": os.path.join(temp_dir, "vectordb"),
        "embeddings": os.path.join(temp_dir, "embeddings"),
        "cache": os.path.join(temp_dir, "cache"),
    }

    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)

    return dirs


def assert_log_contains(log_file: str, message: str):
    """Assert that log file contains specific message"""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert message in content, f"Log message '{message}' not found in {log_file}"
    else:
        pytest.fail(f"Log file {log_file} does not exist")


def mock_puter_query_success(prompt: str, **kwargs) -> Dict[str, Any]:
    """Helper to create successful Puter.js query responses"""
    # Determine adapter type based on current API_MODE
    api_mode = os.getenv("API_MODE", "mock")  # Default to mock for tests
    adapter_type = "puter_js_mock" if api_mode == "mock" else "puter_js_browser"

    return {
        "success": True,
        "answer": f"Mock response for: {prompt[:50]}...",
        "model": TEST_MODEL_NAME,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "adapter_type": adapter_type,
        "query_time": 1.5,
        "streamed": kwargs.get("stream", False),
    }


def mock_puter_query_error(error_message: str) -> Dict[str, Any]:
    """Helper to create error Puter.js query responses"""
    # Determine adapter type based on current API_MODE
    api_mode = os.getenv("API_MODE", "mock")  # Default to mock for tests
    adapter_type = "puter_js_mock" if api_mode == "mock" else "puter_js_browser"

    return {
        "success": False,
        "error": error_message,
        "adapter_type": adapter_type,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def create_mock_document(content: str, source_url: str, doc_type: str = "nephio") -> Dict[str, Any]:
    """Helper to create mock document objects"""
    return {
        "page_content": content,
        "metadata": {
            "source": source_url,
            "type": doc_type,
            "title": f"Mock Document - {doc_type}",
            "content_length": len(content),
            "last_updated": time.strftime("%Y-%m-%d"),
        },
    }


def setup_responses_mock(responses_data: Dict[str, Dict[str, Any]]):
    """Helper to setup responses mock with multiple URLs"""
    for url, response_config in responses_data.items():
        responses.add(
            responses.GET,
            url,
            body=response_config.get("content", ""),
            status=response_config.get("status_code", 200),
            content_type=response_config.get("content_type", "text/html"),
        )


# ============================================================================
# PYTEST MARKERS FOR DIFFERENT TEST TYPES
# ============================================================================


def pytest_configure(config):
    """Configure custom pytest markers and test environment"""
    config.addinivalue_line("markers", "unit: Unit tests with full mocking")
    config.addinivalue_line("markers", "integration: Integration tests with selective mocking")
    config.addinivalue_line("markers", "slow: Slow tests that take more than 5 seconds")
    config.addinivalue_line("markers", "browser: Tests requiring browser automation")
    config.addinivalue_line("markers", "network: Tests requiring network access")
    config.addinivalue_line("markers", "puter: Tests specific to Puter.js integration")
    config.addinivalue_line("markers", "vectordb: Tests involving vector database operations")
    config.addinivalue_line("markers", "llm: Tests involving LLM API calls")

    # Ensure API_MODE is consistently set to mock for all test sessions
    os.environ["API_MODE"] = "mock"
