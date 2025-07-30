"""
O-RAN × Nephio RAG 系統核心模組
實現完整的檢索增強生成系統
"""
import os
import time
import logging
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any

# Core libraries
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

# Lightweight embeddings - removed heavy sentence-transformers dependency  
# Will use simple TF-IDF approaches for now
import nltk
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    # Fallback to basic text processing if sklearn not available
    SKLEARN_AVAILABLE = False
    import logging
    logging.getLogger(__name__).warning("sklearn not available, using basic text processing")

# CONSTRAINT COMPLIANT: Using Puter.js integration instead of direct Anthropic API
# Following: https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/
# REMOVED: from langchain_anthropic import ChatAnthropic (violates constraint)

try:
    from .config import Config
    from .document_loader import DocumentLoader
    from .simple_monitoring import get_monitoring, monitor_query
    from .puter_integration import PuterRAGManager, create_puter_rag_manager
except ImportError:
    from config import Config
    from document_loader import DocumentLoader
    from simple_monitoring import get_monitoring, monitor_query
    from puter_integration import PuterRAGManager, create_puter_rag_manager

# 設定模組日誌記錄器
logger = logging.getLogger(__name__)


class VectorDatabaseManager:
    """向量資料庫管理器"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.vectordb = None
        self.embeddings = None
        self.text_splitter = None
        self._setup_embeddings()
        self._setup_text_splitter()
    
    def _setup_embeddings(self):
        """設定輕量級嵌入模型 (使用 TF-IDF 代替 HuggingFace)"""
        try:
            cache_dir = self.config.EMBEDDINGS_CACHE_PATH
            os.makedirs(cache_dir, exist_ok=True)
            
            # 使用 TF-IDF 向量化器作為輕量級替代方案
            self.embeddings = TfidfVectorizer(
                max_features=5000,  # 限制特徵數量以節省記憶體
                stop_words='english',
                ngram_range=(1, 2),  # 使用 1-gram 和 2-gram
                min_df=2,  # 忽略出現次數少於2的詞
                max_df=0.8  # 忽略出現在超過80%文檔中的詞
            )
            
            logger.info("✅ 輕量級嵌入模型 (TF-IDF) 載入成功")
            
        except Exception as e:
            logger.error(f"❌ 嵌入模型載入失敗: {e}")
            raise
    
    def _setup_text_splitter(self):
        """設定文字分割器"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def build_vector_database(self, documents: List[Document]) -> bool:
        """建立向量資料庫"""
        try:
            if not documents:
                logger.error("沒有文件可建立向量資料庫")
                return False
            
            logger.info(f"開始建立向量資料庫，共 {len(documents)} 個文件...")
            
            # 分割文件
            all_chunks = []
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                all_chunks.extend(chunks)
            
            logger.info(f"文件分割完成，共 {len(all_chunks)} 個文字塊")
            
            # 建立向量資料庫
            self.vectordb = Chroma.from_documents(
                documents=all_chunks,
                embedding=self.embeddings,
                persist_directory=self.config.VECTOR_DB_PATH,
                collection_name=self.config.COLLECTION_NAME
            )
            
            # 持久化
            self.vectordb.persist()
            logger.info("✅ 向量資料庫建立成功")
            return True
            
        except ImportError as e:
            logger.error(f"❌ 缺少必要的依賴包: {e}")
            return False
        except MemoryError as e:  
            logger.error(f"❌ 記憶體不足，無法建立向量資料庫: {e}")
            return False
        except OSError as e:
            logger.error(f"❌ 檔案系統錯誤: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 建立向量資料庫時發生未預期的錯誤: {e}")
            return False
    
    def load_existing_database(self) -> bool:
        """載入現有向量資料庫"""
        try:
            if not os.path.exists(self.config.VECTOR_DB_PATH):
                logger.warning("向量資料庫不存在")
                return False
            
            self.vectordb = Chroma(
                persist_directory=self.config.VECTOR_DB_PATH,
                embedding_function=self.embeddings,
                collection_name=self.config.COLLECTION_NAME
            )
            
            # 檢查資料庫是否有內容
            collection = self.vectordb.get()
            if not collection.get('ids'):
                logger.warning("向量資料庫為空")
                return False
            
            logger.info(f"✅ 載入向量資料庫成功，包含 {len(collection['ids'])} 個文字塊")
            return True
            
        except Exception as e:
            logger.error(f"❌ 載入向量資料庫失敗: {e}")
            return False
    
    def get_retriever(self, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5):
        """取得檢索器"""
        if not self.vectordb:
            raise ValueError("向量資料庫未就緒")
        
        k = k or self.config.RETRIEVER_K
        fetch_k = fetch_k or self.config.RETRIEVER_FETCH_K
        lambda_mult = lambda_mult or self.config.RETRIEVER_LAMBDA_MULT
        
        return self.vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": fetch_k,
                "lambda_mult": lambda_mult
            }
        )
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """相似度搜尋"""
        if not self.vectordb:
            raise ValueError("向量資料庫未就緒")
        
        return self.vectordb.similarity_search(query, k=k)
    
    def get_database_info(self) -> Dict[str, Any]:
        """取得資料庫資訊"""
        if not self.vectordb:
            return {"error": "向量資料庫未就緒"}
        
        try:
            collection = self.vectordb.get()
            return {
                "document_count": len(collection.get('ids', [])),
                "collection_name": self.config.COLLECTION_NAME,
                "persist_directory": self.config.VECTOR_DB_PATH
            }
        except Exception as e:
            return {"error": str(e)}


class QueryProcessor:
    """查詢處理器 - 使用符合約束的 Puter.js 整合"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.puter_manager = None
        self._setup_puter_integration()
    
    def _setup_puter_integration(self):
        """設定 Puter.js Claude 整合"""
        try:
            # 從配置獲取模型設定
            model = getattr(self.config, 'PUTER_MODEL', 'claude-sonnet-4')
            headless = True  # 預設使用無頭模式
            
            # 創建 Puter.js RAG 管理器
            self.puter_manager = create_puter_rag_manager(
                model=model,
                headless=headless
            )
            
            # 設定為主要的 LLM 管理器 (替代直接 API)
            self.llm_manager = self.puter_manager
            
            logger.info(f"✅ Puter.js Claude 整合設定成功 (模型: {model})")
            
        except Exception as e:
            logger.error(f"❌ Puter.js 整合設定失敗: {e}")
            raise e
    
    def setup_qa_chain(self, retriever) -> bool:
        """設定問答鏈 - 使用 Puter.js 模式"""
        try:
            # 儲存 retriever 以供 Puter.js 查詢使用
            self.retriever = retriever
            logger.info("✅ 檢索器設定成功 (Puter.js 模式)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 問答鏈設定失敗: {e}")
            return False
    
    @monitor_query("rag_query")
    def process_query(self, question: str) -> Dict[str, Any]:
        """處理查詢 - 支援多種 API 模式"""
        try:
            start_time = time.time()
            
            if self.qa_chain is not None:
                # 傳統 LangChain 模式
                result = self.qa_chain({"query": question})
                end_time = time.time()
                
                # 處理來源文件
                sources = []
                if result.get("source_documents"):
                    for doc in result["source_documents"]:
                        metadata = doc.metadata
                        sources.append({
                            "url": metadata.get("source_url", ""),
                            "type": metadata.get("source_type", ""),
                            "description": metadata.get("description", ""),
                            "title": metadata.get("title", ""),
                            "content_preview": doc.page_content[:self.config.CONTENT_PREVIEW_LENGTH] + "..." if len(doc.page_content) > self.config.CONTENT_PREVIEW_LENGTH else doc.page_content
                        })
                
                return {
                    "answer": result["result"],
                    "sources": sources,
                    "query_time": round(end_time - start_time, 2)
                }
                
            elif hasattr(self, 'retriever') and self.llm_manager:
                # 適配器模式
                # 1. 使用檢索器取得相關文件
                relevant_docs = self.retriever.get_relevant_documents(question)
                
                # 2. 構建上下文
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                # 3. 構建提示
                prompt = f"""你是一位專精於 O-RAN 和 Nephio 技術的專家助手。請根據提供的上下文資訊，用繁體中文回答問題。

請遵循以下原則：
1. 只根據提供的上下文資訊回答問題
2. 如果上下文中沒有相關資訊，請明確說明
3. 回答要準確、詳細且有條理
4. 優先引用官方文件的內容
5. 如果涉及技術實作，請提供具體的步驟或範例

上下文資訊：
{context}

問題：{question}

回答："""
                
                # 4. 使用 LLM 管理器查詢
                llm_result = self.llm_manager.query(prompt)
                end_time = time.time()
                
                # 5. 處理來源文件
                sources = []
                for doc in relevant_docs:
                    metadata = doc.metadata
                    sources.append({
                        "url": metadata.get("source_url", ""),
                        "type": metadata.get("source_type", ""),
                        "description": metadata.get("description", ""),
                        "title": metadata.get("title", ""),
                        "content_preview": doc.page_content[:self.config.CONTENT_PREVIEW_LENGTH] + "..." if len(doc.page_content) > self.config.CONTENT_PREVIEW_LENGTH else doc.page_content
                    })
                
                return {
                    "answer": llm_result.get("answer", "無法取得回答"),
                    "sources": sources,
                    "query_time": round(end_time - start_time, 2),
                    "adapter_mode": llm_result.get("adapter_mode"),
                    "model": llm_result.get("model"),
                    "error": llm_result.get("error")
                }
            else:
                return {
                    "error": "system_not_ready",
                    "answer": "系統尚未準備就緒，請稍後再試。"
                }
            
        except Exception as e:
            logger.error(f"查詢處理失敗: {e}")
            return {
                "error": str(e),
                "answer": f"查詢處理時發生錯誤: {str(e)}"
            }


class ORANNephioRAG:
    """O-RAN × Nephio RAG 系統主類別"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.document_loader = DocumentLoader(self.config)
        self.vector_manager = VectorDatabaseManager(self.config)
        self.query_processor = QueryProcessor(self.config)
        
        # 初始化監控
        self.monitoring = get_monitoring()
        self.monitoring.start()
        
        logger.info("✅ O-RAN × Nephio RAG 系統初始化完成")
    
    def build_vector_database(self) -> bool:
        """建立向量資料庫"""
        try:
            logger.info("開始建立向量資料庫...")
            
            # 載入文件
            enabled_sources = [source for source in self.config.OFFICIAL_SOURCES if source.enabled]
            documents = self.document_loader.load_all_documents(enabled_sources)
            
            # 記錄載入的文件數量
            self.monitoring.record_documents_loaded(len(documents))
            
            # 建立向量資料庫
            success = self.vector_manager.build_vector_database(documents)
            
            # 更新向量資料庫狀態
            self.monitoring.set_vectordb_ready(success)
            
            return success
            
        except Exception as e:
            logger.error(f"建立向量資料庫失敗: {e}")
            return False
    
    def load_existing_database(self) -> bool:
        """載入現有向量資料庫"""
        success = self.vector_manager.load_existing_database()
        self.monitoring.set_vectordb_ready(success)
        return success
    
    def setup_qa_chain(self) -> bool:
        """設定問答鏈"""
        try:
            retriever = self.vector_manager.get_retriever()
            return self.query_processor.setup_qa_chain(retriever)
        except Exception as e:
            logger.error(f"設定問答鏈失敗: {e}")
            return False
    
    def query(self, question: str, include_citations: bool = True) -> Dict[str, Any]:
        """執行查詢"""
        return self.query_processor.process_query(question)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """相似度搜尋"""
        return self.vector_manager.similarity_search(query, k)
    
    def update_database(self) -> bool:
        """更新向量資料庫"""
        logger.info("開始更新向量資料庫...")
        
        # 備份現有資料庫
        backup_path = None
        if os.path.exists(self.config.VECTOR_DB_PATH):
            backup_path = f"{self.config.VECTOR_DB_PATH}_backup_{int(time.time())}"
            shutil.copytree(self.config.VECTOR_DB_PATH, backup_path)
            logger.info(f"已備份現有資料庫至: {backup_path}")
        
        try:
            # 重新建立資料庫
            success = self.build_vector_database()
            
            if success:
                # 重新設定問答鏈
                self.setup_qa_chain()
                
                # 刪除備份
                if backup_path and os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                    logger.info("備份已清理")
                
                logger.info("✅ 向量資料庫更新成功")
                return True
            else:
                # 恢復備份
                if backup_path and os.path.exists(backup_path):
                    if os.path.exists(self.config.VECTOR_DB_PATH):
                        shutil.rmtree(self.config.VECTOR_DB_PATH)
                    shutil.move(backup_path, self.config.VECTOR_DB_PATH)
                    logger.info("已恢復備份資料庫")
                
                return False
                
        except Exception as e:
            logger.error(f"更新向量資料庫失敗: {e}")
            
            # 恢復備份
            if backup_path and os.path.exists(backup_path):
                if os.path.exists(self.config.VECTOR_DB_PATH):
                    shutil.rmtree(self.config.VECTOR_DB_PATH)
                shutil.move(backup_path, self.config.VECTOR_DB_PATH)
                logger.info("已恢復備份資料庫")
            
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """取得系統狀態"""
        try:
            # 檢查向量資料庫
            vectordb_ready = self.vector_manager.vectordb is not None
            vectordb_info = self.vector_manager.get_database_info()
            
            # 檢查問答鏈/檢索器
            qa_chain_ready = (self.query_processor.qa_chain is not None or 
                            hasattr(self.query_processor, 'retriever'))
            
            # 檢查 LLM 管理器狀態
            llm_status = {}
            if hasattr(self.query_processor, 'llm_manager') and self.query_processor.llm_manager:
                llm_status = self.query_processor.llm_manager.get_status()
            
            # 檢查文件來源
            total_sources = len(self.config.OFFICIAL_SOURCES)
            enabled_sources = len([s for s in self.config.OFFICIAL_SOURCES if s.enabled])
            
            # 載入統計
            load_stats = self.document_loader.get_load_statistics()
            
            return {
                "vectordb_ready": vectordb_ready,
                "qa_chain_ready": qa_chain_ready,
                "vectordb_info": vectordb_info,
                "llm_status": llm_status,
                "total_sources": total_sources,
                "enabled_sources": enabled_sources,
                "load_statistics": load_stats,
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"取得系統狀態失敗: {e}")
            return {"error": str(e)}
    
    def switch_api_mode(self, new_mode: str) -> Dict[str, Any]:
        """切換 API 模式"""
        try:
            if hasattr(self.query_processor, 'llm_manager') and self.query_processor.llm_manager:
                success = self.query_processor.llm_manager.switch_mode(new_mode)
                
                if success:
                    # 重新設定問答鏈
                    if hasattr(self.query_processor, 'retriever'):
                        self.setup_qa_chain()
                    
                    return {
                        "success": True,
                        "message": f"已切換到 {new_mode} 模式",
                        "new_status": self.query_processor.llm_manager.get_status()
                    }
                else:
                    return {
                        "success": False,
                        "message": f"不支援的 API 模式: {new_mode}"
                    }
            else:
                return {
                    "success": False,
                    "message": "LLM 管理器未初始化"
                }
                
        except Exception as e:
            logger.error(f"切換 API 模式失敗: {e}")
            return {
                "success": False,
                "message": f"切換失敗: {str(e)}"
            }


def create_rag_system(config: Optional[Config] = None) -> ORANNephioRAG:
    """建立 RAG 系統的工廠函數"""
    return ORANNephioRAG(config)


def quick_query(question: str, config: Optional[Config] = None) -> str:
    """快速查詢函數，適用於簡單的一次性查詢"""
    try:
        rag = create_rag_system(config)
        
        # 載入向量資料庫
        if not rag.load_existing_database():
            return "❌ 向量資料庫載入失敗，請先建立資料庫"
        
        # 設定問答鏈
        if not rag.setup_qa_chain():
            return "❌ 問答鏈設定失敗"
        
        # 執行查詢
        result = rag.query(question)
        
        if result.get("error"):
            return f"查詢失敗: {result['error']}"
        
        return result.get("answer", "無法取得回答")
        
    except Exception as e:
        logger.error(f"快速查詢失敗: {e}")
        return f"查詢失敗: {str(e)}"