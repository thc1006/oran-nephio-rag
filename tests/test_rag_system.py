"""
RAG 系統模組單元測試
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# Skip marker for tests requiring heavy dependencies
try:
    # Test if we can import the problematic modules
    import nltk
    import scipy.stats
    HEAVY_DEPS_AVAILABLE = True
except (ImportError, ValueError):
    HEAVY_DEPS_AVAILABLE = False

skip_if_no_heavy_deps = pytest.mark.skipif(
    not HEAVY_DEPS_AVAILABLE, 
    reason="Requires NLTK and SciPy dependencies which have compatibility issues"
)

# 導入待測試的模組
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Conditional imports - skip tests if dependencies not available
if HEAVY_DEPS_AVAILABLE:
    try:
        from src.oran_nephio_rag_fixed import PuterRAGSystem, SimplifiedVectorDatabase, create_rag_system, quick_query
        from src.config import Config, DocumentSource
    except ImportError:
        HEAVY_DEPS_AVAILABLE = False
        
if not HEAVY_DEPS_AVAILABLE:
    # Create dummy classes for test collection
    class PuterRAGSystem: pass
    class SimplifiedVectorDatabase: pass
    def create_rag_system(): pass
    def quick_query(): pass
    from config import Config, DocumentSource

@skip_if_no_heavy_deps
class TestSimplifiedVectorDatabase:
    """SimplifiedVectorDatabase 類別測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 創建測試配置
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            self.config = Config()
            self.config.VECTOR_DB_PATH = os.path.join(self.temp_dir, "test_vectordb")
            self.config.EMBEDDINGS_CACHE_PATH = os.path.join(self.temp_dir, "test_embeddings")
    
    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_components(self):
        """測試簡化向量資料庫初始化"""
        db_path = os.path.join(self.temp_dir, "test.json")
        manager = SimplifiedVectorDatabase(db_path)
        
        assert manager.db_path == db_path
        assert manager.documents == []
        assert manager.doc_index == {}
    
    def test_add_documents(self):
        """測試添加文檔到資料庫"""
        db_path = os.path.join(self.temp_dir, "test.json")
        manager = SimplifiedVectorDatabase(db_path)
        
        from langchain.docstore.document import Document
        test_docs = [
            Document(
                page_content="This is a test document about Nephio scaling operations with network functions.",
                metadata={"source": "test1", "source_type": "nephio"}
            ),
            Document(
                page_content="Another document about O-RAN deployment and cluster management with sufficient content length.",
                metadata={"source": "test2", "source_type": "oran_sc"}
            )
        ]
        
        manager.add_documents(test_docs)
        
        assert len(manager.documents) == 2
        assert len(manager.doc_index) == 2
        assert manager.documents[0]['content'] == test_docs[0].page_content
        assert manager.documents[1]['content'] == test_docs[1].page_content
    

@skip_if_no_heavy_deps
class TestPuterRAGSystemBasic:
    """PuterRAGSystem 基本功能測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            self.config = Config()
    
    
    
    @patch('src.oran_nephio_rag_fixed.create_puter_rag_manager')
    def test_basic_setup(self, mock_create_puter):
        """測試基本系統設置"""
        mock_create_puter.return_value = MagicMock()
        
        system = PuterRAGSystem(self.config)
        
        assert system.config == self.config
        assert system.vectordb is not None
        assert system.text_splitter is not None
        assert system.puter_manager is not None

@skip_if_no_heavy_deps
class TestPuterRAGSystemIntegration:
    """PuterRAGSystem 整合測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.DocumentLoader')
    @patch('src.oran_nephio_rag_fixed.VectorDatabaseManager')
    @patch('src.oran_nephio_rag_fixed.QueryProcessor')
    def test_init(self, mock_query_processor, mock_vector_manager, mock_doc_loader):
        """測試 RAG 系統初始化"""
        # 設定 mocks
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader.return_value = mock_doc_loader_instance
        
        mock_vector_manager_instance = MagicMock()
        mock_vector_manager.return_value = mock_vector_manager_instance
        
        mock_query_processor_instance = MagicMock()
        mock_query_processor.return_value = mock_query_processor_instance
        
        rag = ORANNephioRAG()
        
        assert rag.document_loader == mock_doc_loader_instance
        assert rag.vector_manager == mock_vector_manager_instance
        assert rag.query_processor == mock_query_processor_instance
        assert rag.vectordb is None
        assert rag.qa_chain is None
        assert rag._last_update is None
        assert isinstance(rag._initialization_time, datetime)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.DocumentLoader')
    @patch('src.oran_nephio_rag_fixed.VectorDatabaseManager')
    @patch('src.oran_nephio_rag_fixed.QueryProcessor')
    def test_build_vector_database(self, mock_query_processor, mock_vector_manager, mock_doc_loader):
        """測試建立向量資料庫"""
        # 設定 mocks
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader.return_value = mock_doc_loader_instance
        
        # 模擬載入文件
        from langchain.docstore.document import Document
        test_docs = [Document(page_content="Test content", metadata={})]
        mock_doc_loader_instance.load_all_documents.return_value = test_docs
        
        mock_vector_manager_instance = MagicMock()
        mock_vector_manager.return_value = mock_vector_manager_instance
        mock_vectordb = MagicMock()
        mock_vector_manager_instance.build_vector_database.return_value = mock_vectordb
        
        mock_query_processor.return_value = MagicMock()
        
        rag = ORANNephioRAG()
        result = rag.build_vector_database()
        
        assert result is True
        assert rag.vectordb == mock_vectordb
        assert rag._last_update is not None
        mock_doc_loader_instance.load_all_documents.assert_called_once()
        mock_vector_manager_instance.build_vector_database.assert_called_once_with(test_docs)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.DocumentLoader')
    @patch('src.oran_nephio_rag_fixed.VectorDatabaseManager') 
    @patch('src.oran_nephio_rag_fixed.QueryProcessor')
    def test_query_success(self, mock_query_processor, mock_vector_manager, mock_doc_loader):
        """測試成功查詢"""
        # 設定 mocks
        mock_doc_loader.return_value = MagicMock()
        mock_vector_manager.return_value = MagicMock()
        
        mock_query_processor_instance = MagicMock()
        mock_query_processor.return_value = mock_query_processor_instance
        
        # 設定 QA 鏈
        mock_qa_chain = MagicMock()
        from langchain.docstore.document import Document
        test_source_docs = [
            Document(
                page_content="Test content",
                metadata={
                    "source_url": "https://test.com",
                    "source_type": "nephio",
                    "description": "Test Doc"
                }
            )
        ]
        
        mock_qa_result = {
            "result": "This is a test answer about Nephio scaling.",
            "source_documents": test_source_docs
        }
        mock_qa_chain.return_value = mock_qa_result
        
        rag = ORANNephioRAG()
        rag.qa_chain = mock_qa_chain
        
        result = rag.query("Test question")
        
        assert "answer" in result
        assert "sources" in result
        assert "timestamp" in result
        assert result["answer"] == mock_qa_result["result"]
        assert len(result["sources"]) == 1
        assert result["sources"][0]["url"] == "https://test.com"
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.DocumentLoader')
    @patch('src.oran_nephio_rag_fixed.VectorDatabaseManager')
    @patch('src.oran_nephio_rag_fixed.QueryProcessor')
    def test_query_not_ready(self, mock_query_processor, mock_vector_manager, mock_doc_loader):
        """測試系統未準備就緒時的查詢"""
        mock_doc_loader.return_value = MagicMock()
        mock_vector_manager.return_value = MagicMock()
        mock_query_processor.return_value = MagicMock()
        
        rag = ORANNephioRAG()
        # 不設定 qa_chain，模擬未準備就緒狀態
        
        result = rag.query("Test question")
        
        assert "error" in result
        assert result["error"] == "qa_chain_not_ready"
        assert "系統尚未準備就緒" in result["answer"]
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.DocumentLoader')
    @patch('src.oran_nephio_rag_fixed.VectorDatabaseManager')
    @patch('src.oran_nephio_rag_fixed.QueryProcessor')
    def test_get_system_status(self, mock_query_processor, mock_vector_manager, mock_doc_loader):
        """測試取得系統狀態"""
        # 設定 mocks
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader.return_value = mock_doc_loader_instance
        mock_doc_loader_instance.get_load_statistics.return_value = {
            "success_rate": 85.5,
            "total_attempts": 10
        }
        
        mock_vector_manager.return_value = MagicMock()
        mock_query_processor.return_value = MagicMock()
        
        rag = ORANNephioRAG()
        rag.vectordb = MagicMock()  # 模擬已載入的向量資料庫
        rag.qa_chain = MagicMock()  # 模擬已設定的問答鏈
        
        # 模擬向量資料庫資訊
        mock_collection = {"ids": ["id1", "id2", "id3"]}
        rag.vectordb.get.return_value = mock_collection
        
        status = rag.get_system_status()
        
        assert isinstance(status, dict)
        assert status["vectordb_ready"] is True
        assert status["qa_chain_ready"] is True
        assert "initialization_time" in status
        assert "load_statistics" in status
        assert status["load_statistics"]["success_rate"] == 85.5

@skip_if_no_heavy_deps
class TestUtilityFunctions:
    """測試工具函數"""
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.PuterRAGSystem')
    def test_create_rag_system(self, mock_rag_class):
        """測試建立 RAG 系統工廠函數"""
        mock_rag_instance = MagicMock()
        mock_rag_class.return_value = mock_rag_instance
        
        result = create_rag_system()
        
        assert result == mock_rag_instance
        mock_rag_class.assert_called_once_with(None)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.create_rag_system')
    def test_quick_query(self, mock_create_rag):
        """測試快速查詢函數"""
        # 設定 mock RAG 系統
        mock_rag = MagicMock()
        mock_create_rag.return_value = mock_rag
        
        mock_rag.load_existing_database.return_value = True
        mock_rag.setup_qa_chain.return_value = True
        mock_rag.query.return_value = {"answer": "Test answer"}
        
        result = quick_query("Test question")
        
        assert result == "Test answer"
        mock_rag.load_existing_database.assert_called_once()
        mock_rag.setup_qa_chain.assert_called_once()
        mock_rag.query.assert_called_once_with("Test question")
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag_fixed.create_rag_system')
    def test_quick_query_failure(self, mock_create_rag):
        """測試快速查詢失敗情況"""
        # 模擬創建失敗
        mock_create_rag.side_effect = Exception("Creation failed")
        
        result = quick_query("Test question")
        
        assert "查詢失敗: Creation failed" in result

@skip_if_no_heavy_deps
class TestRAGSystemIntegration:
    """RAG 系統整合測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('src.oran_nephio_rag_fixed.HuggingFaceEmbeddings')
    @patch('src.oran_nephio_rag_fixed.ChatAnthropic')
    @patch('src.oran_nephio_rag_fixed.DocumentLoader')
    @patch('src.oran_nephio_rag_fixed.Chroma')
    def test_full_workflow(self, mock_chroma, mock_doc_loader, mock_claude, mock_embeddings):
        """測試完整工作流程"""
        # 設定所有 mocks
        mock_embeddings.return_value = MagicMock()
        mock_claude.return_value = MagicMock()
        
        # 文件載入器 mock
        mock_doc_loader_instance = MagicMock()
        mock_doc_loader.return_value = mock_doc_loader_instance
        
        from langchain.docstore.document import Document
        test_docs = [
            Document(
                page_content="Comprehensive content about Nephio network function scaling and deployment with O-RAN integration.",
                metadata={"source_url": "https://test.com", "source_type": "nephio"}
            )
        ]
        mock_doc_loader_instance.load_all_documents.return_value = test_docs
        mock_doc_loader_instance.get_load_statistics.return_value = {"success_rate": 100}
        
        # 向量資料庫 mock
        mock_vectordb = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectordb
        mock_chroma.return_value = mock_vectordb
        mock_vectordb.get.return_value = {"ids": ["id1"]}
        
        # 建立 RAG 系統並執行完整流程
        rag = ORANNephioRAG()
        
        # 1. 建立向量資料庫
        build_result = rag.build_vector_database()
        assert build_result is True
        
        # 2. 設定問答鏈
        setup_result = rag.setup_qa_chain()
        assert setup_result is True
        
        # 3. 檢查系統狀態
        status = rag.get_system_status()
        assert status["vectordb_ready"] is True
        assert status["qa_chain_ready"] is True
        
        # 驗證 mocks 被正確調用
        mock_doc_loader_instance.load_all_documents.assert_called()
        mock_chroma.from_documents.assert_called()

if __name__ == "__main__":
    pytest.main([__file__])
