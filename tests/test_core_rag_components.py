"""
Comprehensive unit tests for core RAG system components
Testing: VectorDatabaseManager, QueryProcessor, DocumentLoader with full mocking
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from typing import List, Dict, Any

# Test imports
from langchain.docstore.document import Document


class TestVectorDatabaseManager:
    """Unit tests for VectorDatabaseManager"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        config = MagicMock()
        config.VECTOR_DB_PATH = "./test_vectordb"
        config.COLLECTION_NAME = "test_collection"
        config.CHUNK_SIZE = 512
        config.CHUNK_OVERLAP = 100
        config.EMBEDDINGS_CACHE_PATH = "./test_embeddings"
        return config

    @pytest.fixture
    def mock_embeddings(self):
        """Mock embeddings model"""
        embeddings = MagicMock()
        embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]] * 5
        embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        embeddings.model_name = "test-model"
        return embeddings

    @pytest.fixture
    def sample_documents(self) -> List[Document]:
        """Sample documents for testing"""
        return [
            Document(
                page_content="Nephio is a Kubernetes-based cloud native intent automation platform designed for telecom networks.",
                metadata={"source": "https://docs.nephio.org/arch", "type": "nephio", "priority": 1}
            ),
            Document(
                page_content="O-RAN provides open interfaces and architecture for RAN disaggregation enabling multi-vendor interoperability.",
                metadata={"source": "https://docs.nephio.org/oran", "type": "nephio", "priority": 2}
            ),
            Document(
                page_content="Network Function scaling involves horizontal scale-out and vertical scale-up strategies for managing traffic loads.",
                metadata={"source": "https://docs.nephio.org/scaling", "type": "nephio", "priority": 1}
            )
        ]

    @patch('src.oran_nephio_rag.HUGGINGFACE_EMBEDDINGS_AVAILABLE', True)
    @patch('src.oran_nephio_rag.HuggingFaceEmbeddings')
    @patch('src.oran_nephio_rag.Chroma')
    @patch('src.oran_nephio_rag.os.makedirs')
    @patch('src.oran_nephio_rag.shutil.rmtree')
    def test_vector_db_manager_initialization(self, mock_rmtree, mock_makedirs, mock_chroma, mock_hf_embeddings, mock_config):
        """Test VectorDatabaseManager initialization"""
        from src.oran_nephio_rag import VectorDatabaseManager

        # Setup mocks
        mock_embeddings_instance = MagicMock()
        mock_hf_embeddings.return_value = mock_embeddings_instance

        # Initialize manager
        manager = VectorDatabaseManager(mock_config)

        # Assertions
        assert manager.config == mock_config
        assert manager.embeddings == mock_embeddings_instance
        assert manager.vectordb is None
        assert manager.last_update is None

        # Verify HuggingFace embeddings initialization
        mock_hf_embeddings.assert_called_once()

    @patch('src.oran_nephio_rag.HUGGINGFACE_EMBEDDINGS_AVAILABLE', False)
    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', True)
    def test_vector_db_manager_tfidf_fallback(self, mock_config):
        """Test VectorDatabaseManager falls back to TF-IDF when HuggingFace unavailable"""
        from src.oran_nephio_rag import VectorDatabaseManager

        manager = VectorDatabaseManager(mock_config)

        # Should use TF-IDF embeddings as fallback
        from src.oran_nephio_rag import SklearnTfidfEmbeddings
        assert isinstance(manager.embeddings, SklearnTfidfEmbeddings)

    @patch('src.oran_nephio_rag.Chroma')
    @patch('src.oran_nephio_rag.os.makedirs')
    @patch('src.oran_nephio_rag.shutil.rmtree')
    @patch('src.oran_nephio_rag.os.path.exists', return_value=True)
    def test_build_vector_database_success(self, mock_exists, mock_rmtree, mock_makedirs, mock_chroma, mock_config, mock_embeddings, sample_documents):
        """Test successful vector database building"""
        from src.oran_nephio_rag import VectorDatabaseManager

        # Setup mocks
        mock_vectordb = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectordb

        # Initialize manager with mock embeddings
        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings

        # Test building database
        result = manager.build_vector_database(sample_documents)

        # Assertions
        assert result is True
        assert manager.vectordb == mock_vectordb
        assert manager.last_update is not None

        # Verify cleanup and creation
        mock_rmtree.assert_called_once()
        mock_makedirs.assert_called()
        mock_chroma.from_documents.assert_called_once()
        mock_vectordb.persist.assert_called_once()

    def test_build_vector_database_empty_documents(self, mock_config, mock_embeddings):
        """Test building vector database with empty document list"""
        from src.oran_nephio_rag import VectorDatabaseManager

        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings

        result = manager.build_vector_database([])

        assert result is False
        assert manager.vectordb is None

    @patch('src.oran_nephio_rag.Chroma')
    @patch('src.oran_nephio_rag.os.path.exists', return_value=True)
    def test_load_existing_database_success(self, mock_exists, mock_chroma, mock_config, mock_embeddings):
        """Test successful loading of existing database"""
        from src.oran_nephio_rag import VectorDatabaseManager

        # Setup mocks
        mock_vectordb = MagicMock()
        mock_vectordb._collection.count.return_value = 100
        mock_chroma.return_value = mock_vectordb

        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings

        result = manager.load_existing_database()

        assert result is True
        assert manager.vectordb == mock_vectordb
        mock_chroma.assert_called_once_with(
            collection_name=mock_config.COLLECTION_NAME,
            embedding_function=mock_embeddings,
            persist_directory=mock_config.VECTOR_DB_PATH
        )

    @patch('src.oran_nephio_rag.os.path.exists', return_value=False)
    def test_load_existing_database_not_exists(self, mock_exists, mock_config, mock_embeddings):
        """Test loading database when it doesn't exist"""
        from src.oran_nephio_rag import VectorDatabaseManager

        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings

        result = manager.load_existing_database()

        assert result is False
        assert manager.vectordb is None

    def test_search_similar_no_vectordb(self, mock_config, mock_embeddings):
        """Test search when vector database is not initialized"""
        from src.oran_nephio_rag import VectorDatabaseManager

        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings

        results = manager.search_similar("test query")

        assert results == []

    def test_search_similar_success(self, mock_config, mock_embeddings):
        """Test successful similarity search"""
        from src.oran_nephio_rag import VectorDatabaseManager

        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings

        # Mock vectordb
        mock_vectordb = MagicMock()
        mock_doc = Document(page_content="test content", metadata={"source": "test"})
        mock_vectordb.similarity_search_with_score.return_value = [(mock_doc, 0.9)]
        manager.vectordb = mock_vectordb

        results = manager.search_similar("test query", k=5)

        assert len(results) == 1
        assert results[0][0] == mock_doc
        assert results[0][1] == 0.9
        mock_vectordb.similarity_search_with_score.assert_called_once_with("test query", k=5)

    def test_get_database_info(self, mock_config, mock_embeddings):
        """Test getting database information"""
        from src.oran_nephio_rag import VectorDatabaseManager

        manager = VectorDatabaseManager(mock_config)
        manager.embeddings = mock_embeddings
        manager.last_update = datetime(2024, 1, 15, 10, 30, 0)

        # Test without vectordb
        info = manager.get_database_info()

        expected_keys = [
            "database_path", "collection_name", "last_update", "database_exists",
            "embedding_model", "document_count", "database_ready", "error"
        ]

        for key in expected_keys:
            assert key in info

        assert info["database_path"] == mock_config.VECTOR_DB_PATH
        assert info["collection_name"] == mock_config.COLLECTION_NAME
        assert info["last_update"] == "2024-01-15T10:30:00"
        assert info["database_ready"] is False
        assert info["document_count"] == 0


class TestSklearnTfidfEmbeddings:
    """Unit tests for SklearnTfidfEmbeddings fallback implementation"""

    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', True)
    @patch('src.oran_nephio_rag.TfidfVectorizer')
    def test_tfidf_embeddings_initialization(self, mock_vectorizer):
        """Test TF-IDF embeddings initialization"""
        from src.oran_nephio_rag import SklearnTfidfEmbeddings

        mock_vectorizer_instance = MagicMock()
        mock_vectorizer.return_value = mock_vectorizer_instance

        embeddings = SklearnTfidfEmbeddings(max_features=1000)

        assert embeddings.max_features == 1000
        assert embeddings.model_name == "tfidf-sklearn"
        assert embeddings.vectorizer == mock_vectorizer_instance
        assert embeddings.is_fitted is False

    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', False)
    def test_tfidf_embeddings_no_sklearn(self):
        """Test TF-IDF embeddings when sklearn not available"""
        from src.oran_nephio_rag import SklearnTfidfEmbeddings

        embeddings = SklearnTfidfEmbeddings()

        assert embeddings.vectorizer is None

        # Should return simple features
        texts = ["This is a test document", "Another test document"]
        result = embeddings.embed_documents(texts)

        assert len(result) == 2
        assert len(result[0]) == 3  # [length, spaces, periods]
        assert all(isinstance(val, float) for val in result[0])

    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', True)
    def test_tfidf_embed_documents_first_time(self):
        """Test embedding documents for first time (training)"""
        from src.oran_nephio_rag import SklearnTfidfEmbeddings

        embeddings = SklearnTfidfEmbeddings()

        # Mock vectorizer
        mock_vectorizer = MagicMock()
        mock_matrix = MagicMock()
        mock_matrix.toarray.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_vectorizer.transform.return_value = mock_matrix
        embeddings.vectorizer = mock_vectorizer

        texts = ["nephio kubernetes", "oran network function"]
        result = embeddings.embed_documents(texts)

        # Should train vectorizer first time
        mock_vectorizer.fit.assert_called_once_with(texts)
        mock_vectorizer.transform.assert_called_once_with(texts)
        assert embeddings.is_fitted is True
        assert result == [[0.1, 0.2], [0.3, 0.4]]

    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', True)
    def test_tfidf_embed_query(self):
        """Test embedding single query"""
        from src.oran_nephio_rag import SklearnTfidfEmbeddings

        embeddings = SklearnTfidfEmbeddings()
        embeddings.is_fitted = True

        # Mock vectorizer
        mock_vectorizer = MagicMock()
        mock_matrix = MagicMock()
        mock_matrix.toarray.return_value = [[0.5, 0.6]]
        mock_vectorizer.transform.return_value = mock_matrix
        embeddings.vectorizer = mock_vectorizer

        result = embeddings.embed_query("test query")

        assert result == [0.5, 0.6]
        mock_vectorizer.transform.assert_called_once_with(["test query"])


class TestQueryProcessor:
    """Unit tests for QueryProcessor"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = MagicMock()
        config.PUTER_MODEL = "claude-sonnet-4"
        config.BROWSER_HEADLESS = True
        config.RETRIEVER_K = 5
        return config

    @pytest.fixture
    def mock_vector_manager(self):
        """Mock vector database manager"""
        manager = MagicMock()
        mock_doc1 = Document(
            page_content="Nephio provides intent-driven automation for network functions",
            metadata={"source": "https://docs.nephio.org/1", "type": "nephio"}
        )
        mock_doc2 = Document(
            page_content="O-RAN enables disaggregated radio access networks",
            metadata={"source": "https://docs.nephio.org/2", "type": "nephio"}
        )
        manager.search_similar.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.8)
        ]
        return manager

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    def test_query_processor_initialization(self, mock_create_manager, mock_config, mock_vector_manager):
        """Test QueryProcessor initialization"""
        from src.oran_nephio_rag import QueryProcessor

        mock_rag_manager = MagicMock()
        mock_create_manager.return_value = mock_rag_manager

        processor = QueryProcessor(mock_config, mock_vector_manager)

        assert processor.config == mock_config
        assert processor.vector_manager == mock_vector_manager
        assert processor.rag_manager == mock_rag_manager

        mock_create_manager.assert_called_once_with(
            model=mock_config.PUTER_MODEL,
            headless=mock_config.BROWSER_HEADLESS
        )

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    def test_query_processor_init_failure(self, mock_create_manager, mock_config, mock_vector_manager):
        """Test QueryProcessor initialization failure"""
        from src.oran_nephio_rag import QueryProcessor

        mock_create_manager.side_effect = Exception("Browser init failed")

        processor = QueryProcessor(mock_config, mock_vector_manager)

        assert processor.rag_manager is None

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    @patch('src.oran_nephio_rag.time.time')
    def test_process_query_success(self, mock_time, mock_create_manager, mock_config, mock_vector_manager):
        """Test successful query processing"""
        from src.oran_nephio_rag import QueryProcessor

        # Setup time mock
        mock_time.side_effect = [0.0, 2.5]  # start_time, end_time

        # Setup RAG manager mock
        mock_rag_manager = MagicMock()
        mock_rag_manager.query.return_value = {
            "success": True,
            "answer": "Nephio is a cloud native automation platform for telecom networks."
        }
        mock_create_manager.return_value = mock_rag_manager

        processor = QueryProcessor(mock_config, mock_vector_manager)

        result = processor.process_query("What is Nephio?")

        # Verify result structure
        assert result["success"] is True
        assert "answer" in result
        assert "sources" in result
        assert "query_time" in result
        assert "retrieval_scores" in result
        assert result["constraint_compliant"] is True
        assert result["generation_method"] == "puter_js_browser"

        # Verify vector search was called
        mock_vector_manager.search_similar.assert_called_once_with("What is Nephio?", k=5)

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    def test_process_query_no_relevant_docs(self, mock_create_manager, mock_config, mock_vector_manager):
        """Test query processing when no relevant documents found"""
        from src.oran_nephio_rag import QueryProcessor

        # Setup empty search results
        mock_vector_manager.search_similar.return_value = []

        mock_rag_manager = MagicMock()
        mock_create_manager.return_value = mock_rag_manager

        processor = QueryProcessor(mock_config, mock_vector_manager)

        result = processor.process_query("Irrelevant query")

        assert result["success"] is False
        assert "無法找到相關資訊" in result["answer"]
        assert result["error"] == "no_relevant_docs"
        assert result["sources"] == []

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    def test_process_query_puter_failure_fallback(self, mock_create_manager, mock_config, mock_vector_manager):
        """Test query processing with Puter.js failure and fallback"""
        from src.oran_nephio_rag import QueryProcessor

        # Setup failed RAG manager
        mock_rag_manager = MagicMock()
        mock_rag_manager.query.return_value = {
            "success": False,
            "error": "Browser session failed"
        }
        mock_create_manager.return_value = mock_rag_manager

        processor = QueryProcessor(mock_config, mock_vector_manager)

        result = processor.process_query("What is O-RAN?")

        # Should use fallback method
        assert "success" in result
        assert "answer" in result
        assert "method" in result

    def test_generate_fallback_answer(self, mock_config, mock_vector_manager):
        """Test fallback answer generation"""
        from src.oran_nephio_rag import QueryProcessor

        processor = QueryProcessor.__new__(QueryProcessor)  # Create without __init__
        processor.config = mock_config

        context_docs = [
            "Nephio is a Kubernetes-based platform. It provides automation for network functions.",
            "O-RAN enables disaggregated radio access. It supports multi-vendor interoperability.",
            "Network function scaling can be horizontal or vertical. Nephio supports both approaches."
        ]

        result = processor._generate_fallback_answer("What is Nephio?", context_docs)

        assert result["success"] is True
        assert result["method"] == "keyword_fallback"
        assert "nephio" in result["answer"].lower()

    def test_generate_fallback_answer_no_matches(self, mock_config, mock_vector_manager):
        """Test fallback answer when no keyword matches"""
        from src.oran_nephio_rag import QueryProcessor

        processor = QueryProcessor.__new__(QueryProcessor)
        processor.config = mock_config

        context_docs = [
            "Some unrelated content without keywords",
            "More irrelevant information here"
        ]

        result = processor._generate_fallback_answer("What is Nephio?", context_docs)

        assert result["success"] is True
        assert result["method"] == "keyword_fallback"
        assert "無法生成具體的回答" in result["answer"]


class TestORANNephioRAG:
    """Unit tests for main ORANNephioRAG class"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = MagicMock()
        config.validate.return_value = True
        return config

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_oran_nephio_rag_initialization(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test ORANNephioRAG initialization"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup mocks
        mock_doc_loader_instance = MagicMock()
        mock_vector_manager_instance = MagicMock()
        mock_doc_loader.return_value = mock_doc_loader_instance
        mock_vector_manager.return_value = mock_vector_manager_instance

        rag = ORANNephioRAG(mock_config)

        assert rag.config == mock_config
        assert rag.document_loader == mock_doc_loader_instance
        assert rag.vector_manager == mock_vector_manager_instance
        assert rag.query_processor is None
        assert rag.is_ready is False
        assert rag.last_build_time is None

        # Verify config validation
        mock_config.validate.assert_called_once()

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    @patch('src.oran_nephio_rag.QueryProcessor')
    def test_initialize_system_success(self, mock_query_processor, mock_vector_manager, mock_doc_loader, mock_config):
        """Test successful system initialization"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup mocks
        mock_vector_manager_instance = MagicMock()
        mock_vector_manager_instance.load_existing_database.return_value = True
        mock_vector_manager.return_value = mock_vector_manager_instance

        mock_query_processor_instance = MagicMock()
        mock_query_processor.return_value = mock_query_processor_instance

        rag = ORANNephioRAG(mock_config)

        result = rag.initialize_system()

        assert result is True
        assert rag.is_ready is True
        assert rag.last_build_time is not None
        assert rag.query_processor == mock_query_processor_instance

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_initialize_system_build_database(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test system initialization with database building"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup mocks
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader_instance.load_all_documents.return_value = [
            Document(page_content="test doc", metadata={"source": "test"})
        ]
        mock_doc_loader.return_value = mock_doc_loader_instance

        mock_vector_manager_instance = MagicMock()
        mock_vector_manager_instance.load_existing_database.return_value = False
        mock_vector_manager_instance.build_vector_database.return_value = True
        mock_vector_manager.return_value = mock_vector_manager_instance

        rag = ORANNephioRAG(mock_config)

        result = rag.initialize_system()

        assert result is True
        mock_doc_loader_instance.load_all_documents.assert_called_once()
        mock_vector_manager_instance.build_vector_database.assert_called_once()

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_initialize_system_no_documents(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test system initialization failure due to no documents"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup mocks
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader_instance.load_all_documents.return_value = []
        mock_doc_loader.return_value = mock_doc_loader_instance

        mock_vector_manager_instance = MagicMock()
        mock_vector_manager_instance.load_existing_database.return_value = False
        mock_vector_manager.return_value = mock_vector_manager_instance

        rag = ORANNephioRAG(mock_config)

        result = rag.initialize_system()

        assert result is False
        assert rag.is_ready is False

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_query_system_not_ready(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test query when system is not ready"""
        from src.oran_nephio_rag import ORANNephioRAG

        rag = ORANNephioRAG(mock_config)
        # Don't initialize system

        with patch.object(rag, 'initialize_system', return_value=False):
            result = rag.query("test question")

        assert result["success"] is False
        assert "system_not_ready" in result["error"]

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_query_success(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test successful query execution"""
        from src.oran_nephio_rag import ORANNephioRAG

        rag = ORANNephioRAG(mock_config)
        rag.is_ready = True

        # Mock query processor
        mock_query_processor = MagicMock()
        mock_query_processor.process_query.return_value = {
            "success": True,
            "answer": "Mock answer",
            "sources": []
        }
        rag.query_processor = mock_query_processor

        result = rag.query("test question")

        assert result["success"] is True
        assert result["answer"] == "Mock answer"
        mock_query_processor.process_query.assert_called_once_with("test question")

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_update_documents_success(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test successful document update"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup mocks
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader_instance.load_all_documents.return_value = [
            Document(page_content="updated doc", metadata={"source": "test"})
        ]
        mock_doc_loader.return_value = mock_doc_loader_instance

        mock_vector_manager_instance = MagicMock()
        mock_vector_manager_instance.build_vector_database.return_value = True
        mock_vector_manager.return_value = mock_vector_manager_instance

        rag = ORANNephioRAG(mock_config)

        result = rag.update_documents()

        assert result is True
        assert rag.last_build_time is not None
        mock_doc_loader_instance.load_all_documents.assert_called_once()
        mock_vector_manager_instance.build_vector_database.assert_called_once()

    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    def test_get_system_status(self, mock_vector_manager, mock_doc_loader, mock_config):
        """Test getting system status"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup mocks
        mock_vector_manager_instance = MagicMock()
        mock_vector_manager_instance.get_database_info.return_value = {
            "database_ready": True,
            "document_count": 100
        }
        mock_vector_manager.return_value = mock_vector_manager_instance

        mock_doc_loader_instance = MagicMock()
        mock_doc_loader_instance.get_load_statistics.return_value = {
            "total_sources": 10,
            "enabled_sources": 8,
            "success_rate": 95.5
        }
        mock_doc_loader.return_value = mock_doc_loader_instance

        rag = ORANNephioRAG(mock_config)
        rag.is_ready = True
        rag.last_build_time = datetime(2024, 1, 15, 10, 30, 0)

        # Mock query processor
        rag.query_processor = MagicMock()

        status = rag.get_system_status()

        # Verify status structure
        expected_keys = [
            "system_ready", "last_build_time", "config_valid",
            "vectordb_ready", "vectordb_info", "qa_chain_ready",
            "total_sources", "enabled_sources", "load_statistics",
            "constraint_compliant", "integration_method"
        ]

        for key in expected_keys:
            assert key in status

        assert status["system_ready"] is True
        assert status["config_valid"] is True
        assert status["qa_chain_ready"] is True
        assert status["constraint_compliant"] is True
        assert status["integration_method"] == "browser_automation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])