"""
PuterRAGSystem 測試模組
Testing the new Puter.js-based RAG system implementation
"""

import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Skip marker for tests requiring heavy dependencies
try:
    # Test if we can import the problematic modules
    import nltk
    import scipy.stats

    HEAVY_DEPS_AVAILABLE = True
except (ImportError, ValueError):
    HEAVY_DEPS_AVAILABLE = False

skip_if_no_heavy_deps = pytest.mark.skipif(
    not HEAVY_DEPS_AVAILABLE, reason="Requires NLTK and SciPy dependencies which have compatibility issues"
)

# 導入待測試的模組
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Conditional imports - skip tests if dependencies not available
if HEAVY_DEPS_AVAILABLE:
    try:
        from src.config import Config
        from src.oran_nephio_rag_fixed import PuterRAGSystem, SimplifiedVectorDatabase
    except ImportError:
        HEAVY_DEPS_AVAILABLE = False

if not HEAVY_DEPS_AVAILABLE:
    # Create dummy classes for test collection
    class PuterRAGSystem:
        pass

    class SimplifiedVectorDatabase:
        pass

    from config import Config


@skip_if_no_heavy_deps
class TestPuterRAGSystem:
    """PuterRAGSystem 類別測試"""

    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()

        # 創建測試配置
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            self.config = Config()
            self.config.VECTOR_DB_PATH = os.path.join(self.temp_dir, "test_vectordb")
            self.config.EMBEDDINGS_CACHE_PATH = os.path.join(self.temp_dir, "test_embeddings")

    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_puter_rag_system_init(self, mock_create_puter):
        """測試 PuterRAGSystem 初始化"""
        mock_puter_manager = MagicMock()
        mock_create_puter.return_value = mock_puter_manager

        system = PuterRAGSystem(self.config)

        assert system.config == self.config
        assert system.vectordb is not None
        assert system.text_splitter is not None
        assert system.puter_manager == mock_puter_manager
        mock_create_puter.assert_called_once()

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_load_existing_database_success(self, mock_create_puter):
        """測試成功載入現有資料庫"""
        mock_create_puter.return_value = MagicMock()

        # 創建測試資料庫目錄和文件
        db_dir = os.path.join(self.temp_dir, "test_vectordb")
        os.makedirs(db_dir, exist_ok=True)

        # 創建一個模擬的資料庫文件
        db_file = os.path.join(db_dir, "simplified_vectordb.json")
        test_data = {
            "documents": [{"id": "test123", "content": "Test content about Nephio", "metadata": {"source": "test"}}],
            "doc_index": {"test123": ["nephio", "content", "test"]},
        }

        with open(db_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        system = PuterRAGSystem(self.config)

        # Mock the load method of SimplifiedVectorDatabase
        with patch.object(system.vectordb, "load", return_value=True):
            result = system.load_existing_database()

        assert result is True

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_load_existing_database_failure(self, mock_create_puter):
        """測試載入不存在的資料庫"""
        mock_create_puter.return_value = MagicMock()

        system = PuterRAGSystem(self.config)

        # Mock the load method to return False (database doesn't exist)
        with patch.object(system.vectordb, "load", return_value=False):
            result = system.load_existing_database()

        assert result is False

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_query_with_loaded_database(self, mock_create_puter):
        """測試在資料庫載入後的查詢"""
        mock_puter_manager = MagicMock()
        mock_create_puter.return_value = mock_puter_manager

        # Mock puter manager query response
        mock_puter_manager.query.return_value = {
            "answer": "Nephio is a cloud native automation platform",
            "model": "claude-sonnet-4",
        }

        system = PuterRAGSystem(self.config)

        # Setup system as if database is loaded
        system.retriever = system.vectordb

        # Mock similarity search to return relevant documents
        from langchain.docstore.document import Document

        mock_docs = [
            Document(
                page_content="Nephio is an automation platform for cloud native networks",
                metadata={
                    "source_url": "https://docs.nephio.org/test",
                    "source_type": "nephio",
                    "description": "Nephio Documentation",
                    "title": "What is Nephio",
                },
            )
        ]

        with patch.object(system.vectordb, "similarity_search", return_value=mock_docs):
            result = system.query("What is Nephio?")

        assert "answer" in result
        assert result["answer"] == "Nephio is a cloud native automation platform"
        assert "sources" in result
        assert len(result["sources"]) == 1
        assert result["sources"][0]["url"] == "https://docs.nephio.org/test"
        assert result["mode"] == "puter_js_rag"
        assert result["constraint_compliant"] is True
        assert "query_time" in result

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_query_system_not_ready(self, mock_create_puter):
        """測試系統未準備就緒時的查詢"""
        mock_create_puter.return_value = MagicMock()

        system = PuterRAGSystem(self.config)
        # Don't set up retriever - system not ready

        result = system.query("Test question")

        assert "error" in result
        assert result["error"] == "system_not_ready"
        assert "系統尚未準備就緒" in result["answer"]

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_query_no_relevant_docs(self, mock_create_puter):
        """測試沒有相關文檔時的查詢"""
        mock_puter_manager = MagicMock()
        mock_create_puter.return_value = mock_puter_manager

        # Mock direct query response
        mock_puter_manager.query.return_value = {
            "answer": "I don't have specific information about this topic",
            "model": "claude-sonnet-4",
        }

        system = PuterRAGSystem(self.config)
        system.retriever = system.vectordb

        # Mock similarity search to return no documents
        with patch.object(system.vectordb, "similarity_search", return_value=[]):
            result = system.query("Very obscure technical question")

        assert "answer" in result
        assert result["sources"] == []
        assert result["mode"] == "puter_js_rag"
        mock_puter_manager.query.assert_called_once_with("Very obscure technical question")

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    @patch("src.oran_nephio_rag_fixed.DocumentLoader")
    def test_build_vector_database(self, mock_doc_loader_class, mock_create_puter):
        """測試建立向量資料庫"""
        mock_create_puter.return_value = MagicMock()

        # Mock document loader
        mock_doc_loader = MagicMock()
        mock_doc_loader_class.return_value = mock_doc_loader

        from langchain.docstore.document import Document

        test_docs = [
            Document(
                page_content="Test document about Nephio architecture and deployment",
                metadata={"source": "test1", "source_type": "nephio"},
            ),
            Document(
                page_content="Another document about O-RAN Service Management and Orchestration",
                metadata={"source": "test2", "source_type": "oran_sc"},
            ),
        ]
        mock_doc_loader.load_all_documents.return_value = test_docs

        system = PuterRAGSystem(self.config)

        # Mock vectordb methods
        with (
            patch.object(system.vectordb, "add_documents") as mock_add,
            patch.object(system.vectordb, "save", return_value=True) as mock_save,
        ):

            result = system.build_vector_database()

            assert result is True
            mock_add.assert_called()
            mock_save.assert_called_once()

    @patch("src.oran_nephio_rag_fixed.create_puter_rag_manager")
    def test_setup_qa_chain(self, mock_create_puter):
        """測試設定問答鏈"""
        mock_create_puter.return_value = MagicMock()

        system = PuterRAGSystem(self.config)
        result = system.setup_qa_chain()

        assert result is True
        assert system.retriever == system.vectordb


@skip_if_no_heavy_deps
class TestSimplifiedVectorDatabase:
    """SimplifiedVectorDatabase 類別測試"""

    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_db.json")

    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_documents(self):
        """測試添加文檔到資料庫"""
        db = SimplifiedVectorDatabase(self.db_path)

        from langchain.docstore.document import Document

        test_docs = [
            Document(
                page_content="This is a test document about Nephio automation",
                metadata={"source": "test1", "type": "nephio"},
            ),
            Document(
                page_content="Another document about O-RAN network functions",
                metadata={"source": "test2", "type": "oran"},
            ),
        ]

        db.add_documents(test_docs)

        assert len(db.documents) == 2
        assert len(db.doc_index) == 2

        # Check if documents are properly indexed
        for doc_data in db.documents:
            assert "id" in doc_data
            assert "content" in doc_data
            assert "metadata" in doc_data
            assert doc_data["id"] in db.doc_index

    def test_extract_keywords(self):
        """測試關鍵字提取功能"""
        db = SimplifiedVectorDatabase(self.db_path)

        text = "nephio is an automation platform for o-ran network functions deployment"
        keywords = db._extract_keywords(text)

        # Should extract important O-RAN/Nephio terms
        assert "nephio" in keywords
        assert "automation" in keywords
        assert "o-ran" in keywords or "oran" in keywords
        assert "deployment" in keywords

    def test_similarity_search(self):
        """測試相似性搜索"""
        db = SimplifiedVectorDatabase(self.db_path)

        from langchain.docstore.document import Document

        test_docs = [
            Document(
                page_content="Nephio automation platform for cloud native networks",
                metadata={"source": "nephio_doc", "type": "nephio"},
            ),
            Document(
                page_content="O-RAN Service Management and Orchestration framework",
                metadata={"source": "oran_doc", "type": "oran"},
            ),
            Document(
                page_content="Kubernetes deployment strategies for edge computing",
                metadata={"source": "k8s_doc", "type": "kubernetes"},
            ),
        ]

        db.add_documents(test_docs)

        # Search for Nephio-related content
        results = db.similarity_search("What is Nephio automation?", k=2)

        assert len(results) <= 2
        # Should return the most relevant document first
        if results:
            assert "nephio" in results[0].page_content.lower()

    def test_save_and_load(self):
        """測試保存和載入資料庫"""
        db = SimplifiedVectorDatabase(self.db_path)

        from langchain.docstore.document import Document

        test_docs = [Document(page_content="Test content for save/load", metadata={"source": "test"})]

        db.add_documents(test_docs)

        # Test save
        db.save()  # save() doesn't return a value
        # Verify the file was created
        assert os.path.exists(self.db_path)

        # Test load
        new_db = SimplifiedVectorDatabase(self.db_path)
        load_result = new_db.load()

        assert load_result is True
        assert len(new_db.documents) == 1
        assert len(new_db.doc_index) == 1
        assert new_db.documents[0]["content"] == "Test content for save/load"

    def test_load_nonexistent_database(self):
        """測試載入不存在的資料庫"""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        db = SimplifiedVectorDatabase(nonexistent_path)

        result = db.load()
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
