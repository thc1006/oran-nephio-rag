"""
RAG 系統模組單元測試
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# 導入待測試的模組
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.oran_nephio_rag import ORANNephioRAG, VectorDatabaseManager, QueryProcessor, create_rag_system, quick_query
from src.config import Config, DocumentSource

class TestVectorDatabaseManager:
    """VectorDatabaseManager 類別測試"""
    
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
    
    @patch('src.oran_nephio_rag.HuggingFaceEmbeddings')
    def test_init_components(self, mock_embeddings):
        """測試組件初始化"""
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        manager = VectorDatabaseManager(self.config)
        
        assert manager.config == self.config
        assert manager.embeddings == mock_embeddings_instance
        assert manager.text_splitter is not None
        
        # 檢查 HuggingFaceEmbeddings 是否被正確調用
        mock_embeddings.assert_called_once()
        call_kwargs = mock_embeddings.call_args[1]
        assert call_kwargs['model_name'] == "sentence-transformers/all-mpnet-base-v2"
        assert call_kwargs['cache_folder'] == self.config.EMBEDDINGS_CACHE_PATH
    
    @patch('src.oran_nephio_rag.HuggingFaceEmbeddings')
    @patch('src.oran_nephio_rag.Chroma')
    def test_build_vector_database(self, mock_chroma, mock_embeddings):
        """測試建立向量資料庫"""
        # 設定 mocks
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_vectordb = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectordb
        
        # 創建測試文件
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
        
        manager = VectorDatabaseManager(self.config)
        result = manager.build_vector_database(test_docs)
        
        assert result == mock_vectordb
        mock_chroma.from_documents.assert_called_once()
        mock_vectordb.persist.assert_called_once()
    
    @patch('src.oran_nephio_rag.HuggingFaceEmbeddings')
    def test_handle_long_document(self, mock_embeddings):
        """測試處理長文件"""
        mock_embeddings.return_value = MagicMock()
        
        from langchain.docstore.document import Document
        
        # 創建一個長文件
        long_content = "This is about nephio scaling. " * 200  # 很長的內容
        long_doc = Document(
            page_content=long_content,
            metadata={"source": "test"}
        )
        
        manager = VectorDatabaseManager(self.config)
        processed_doc = manager._handle_long_document(long_doc)
        
        # 長文件應該被處理（截短或摘要）
        assert len(processed_doc.page_content) <= len(long_content)
        assert "processing_method" in processed_doc.metadata or processed_doc.page_content == long_content

class TestQueryProcessor:
    """QueryProcessor 類別測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            self.config = Config()
    
    @patch('src.oran_nephio_rag.ChatAnthropic')
    def test_init_llm(self, mock_claude):
        """測試 LLM 初始化"""
        mock_claude_instance = MagicMock()
        mock_claude.return_value = mock_claude_instance
        
        processor = QueryProcessor(self.config)
        
        assert processor.llm == mock_claude_instance
        mock_claude.assert_called_once_with(
            model=self.config.CLAUDE_MODEL,
            anthropic_api_key=self.config.ANTHROPIC_API_KEY,
            temperature=self.config.CLAUDE_TEMPERATURE,
            max_tokens=self.config.CLAUDE_MAX_TOKENS,
            timeout=60
        )
    
    @patch('src.oran_nephio_rag.ChatAnthropic')
    @patch('src.oran_nephio_rag.RetrievalQA')
    def test_create_qa_chain(self, mock_qa, mock_claude):
        """測試建立問答鏈"""
        # 設定 mocks
        mock_claude.return_value = MagicMock()
        mock_vectordb = MagicMock()
        mock_retriever = MagicMock()
        mock_vectordb.as_retriever.return_value = mock_retriever
        
        mock_qa_chain = MagicMock()
        mock_qa.from_chain_type.return_value = mock_qa_chain
        
        processor = QueryProcessor(self.config)
        result = processor.create_qa_chain(mock_vectordb)
        
        assert result == mock_qa_chain
        mock_vectordb.as_retriever.assert_called_once()
        mock_qa.from_chain_type.assert_called_once()
    
    @patch('src.oran_nephio_rag.ChatAnthropic')
    def test_format_answer_with_citations(self, mock_claude):
        """測試格式化答案並添加引用"""
        mock_claude.return_value = MagicMock()
        
        processor = QueryProcessor(self.config)
        
        answer = "This is a test answer about Nephio."
        sources = [
            {
                "type": "nephio",
                "description": "Nephio Documentation",
                "url": "https://docs.nephio.org/test"
            },
            {
                "type": "oran_sc",
                "description": "O-RAN SC Guide",
                "url": "https://o-ran-sc.org/test"
            }
        ]
        
        formatted = processor.format_answer_with_citations(answer, sources)
        
        assert answer in formatted
        assert "參考來源" in formatted
        assert "Nephio Documentation" in formatted
        assert "O-RAN SC Guide" in formatted
        assert "https://docs.nephio.org/test" in formatted

class TestORANNephioRAG:
    """ORANNephioRAG 主類別測試"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """每個測試方法執行後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    @patch('src.oran_nephio_rag.QueryProcessor')
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
    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    @patch('src.oran_nephio_rag.QueryProcessor')
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
    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager') 
    @patch('src.oran_nephio_rag.QueryProcessor')
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
    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    @patch('src.oran_nephio_rag.QueryProcessor')
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
    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.VectorDatabaseManager')
    @patch('src.oran_nephio_rag.QueryProcessor')
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

class TestUtilityFunctions:
    """測試工具函數"""
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag.ORANNephioRAG')
    def test_create_rag_system(self, mock_rag_class):
        """測試建立 RAG 系統工廠函數"""
        mock_rag_instance = MagicMock()
        mock_rag_class.return_value = mock_rag_instance
        
        result = create_rag_system()
        
        assert result == mock_rag_instance
        mock_rag_class.assert_called_once_with(None)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.oran_nephio_rag.create_rag_system')
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
    @patch('src.oran_nephio_rag.create_rag_system')
    def test_quick_query_failure(self, mock_create_rag):
        """測試快速查詢失敗情況"""
        # 模擬創建失敗
        mock_create_rag.side_effect = Exception("Creation failed")
        
        result = quick_query("Test question")
        
        assert "查詢失敗: Creation failed" in result

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
    @patch('src.oran_nephio_rag.HuggingFaceEmbeddings')
    @patch('src.oran_nephio_rag.ChatAnthropic')
    @patch('src.oran_nephio_rag.DocumentLoader')
    @patch('src.oran_nephio_rag.Chroma')
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
