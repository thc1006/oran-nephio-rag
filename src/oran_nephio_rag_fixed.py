"""
O-RAN × Nephio RAG 系統核心模組 - PUTER.JS 版本
實現完整的檢索增強生成系統，符合 Puter.js 約束要求
Following: https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/
"""
import os
import time
import logging
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any

# Core libraries for text processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Lightweight text processing without heavy ML dependencies
import json
import hashlib

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


class SimplifiedVectorDatabase:
    """
    簡化版向量資料庫 - 不依賴重型 ML 庫
    使用文本相似度和關鍵字匹配進行文檔檢索
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.documents = []
        self.doc_index = {}
        
    def add_documents(self, documents: List[Document]):
        """添加文檔到資料庫"""
        for doc in documents:
            doc_id = hashlib.md5(doc.page_content.encode()).hexdigest()
            self.documents.append({
                'id': doc_id,
                'content': doc.page_content,
                'metadata': doc.metadata
            })
            # 建立關鍵字索引
            keywords = self._extract_keywords(doc.page_content.lower())
            self.doc_index[doc_id] = keywords
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵字 (簡化版)"""
        # O-RAN 和 Nephio 相關關鍵字
        important_terms = [
            'nephio', 'oran', 'o-ran', 'smo', 'o-cu', 'o-du', 'o-ru',
            'kubernetes', 'gitops', 'network function', 'nf', 'automation',
            'edge', 'cloud', 'deployment', 'scaling', 'orchestration'
        ]
        
        words = text.split()
        keywords = []
        
        # 添加重要術語
        for term in important_terms:
            if term in text:
                keywords.append(term)
        
        # 添加長詞 (可能是專業術語)
        keywords.extend([word for word in words if len(word) > 6])
        
        return list(set(keywords))
    
    def similarity_search(self, query: str, k: int = 6) -> List[Document]:
        """基於關鍵字的相似性搜索"""
        query_keywords = self._extract_keywords(query.lower())
        
        # 計算文檔相關性分數
        doc_scores = []
        for doc in self.documents:
            doc_keywords = self.doc_index[doc['id']]
            # 計算關鍵字重疊度
            overlap = len(set(query_keywords) & set(doc_keywords))
            score = overlap / max(len(query_keywords), 1)
            doc_scores.append((score, doc))
        
        # 按分數排序並返回前 k 個
        doc_scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in doc_scores[:k]:
            if score > 0:  # 只返回有相關性的文檔
                results.append(Document(
                    page_content=doc['content'],
                    metadata=doc['metadata']
                ))
        
        return results
    
    def save(self):
        """儲存資料庫"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump({
                'documents': self.documents,
                'doc_index': self.doc_index
            }, f, ensure_ascii=False, indent=2)
    
    def load(self) -> bool:
        """載入資料庫"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.doc_index = data.get('doc_index', {})
                return True
        except Exception as e:
            logger.error(f"載入資料庫失敗: {e}")
        return False


class PuterRAGSystem:
    """
    基於 Puter.js 的 RAG 系統
    完全符合約束要求的實現
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.vectordb = None
        self.text_splitter = None
        self.puter_manager = None
        self.retriever = None
        
        self._setup_components()
    
    def _setup_components(self):
        """設定系統組件"""
        # 設定文字分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 設定簡化版向量資料庫
        db_file = os.path.join(self.config.VECTOR_DB_PATH, "simplified_vectordb.json")
        self.vectordb = SimplifiedVectorDatabase(db_file)
        
        # 設定 Puter.js 管理器
        model = getattr(self.config, 'PUTER_MODEL', 'claude-sonnet-4')
        self.puter_manager = create_puter_rag_manager(model=model, headless=True)
        
        logger.info("✅ Puter.js RAG 系統組件初始化完成")
    
    def build_vector_database(self) -> bool:
        """建立向量資料庫"""
        try:
            # 載入文檔
            loader = DocumentLoader(self.config)
            documents = loader.load_all_documents(self.config.OFFICIAL_SOURCES)
            
            if not documents:
                logger.error("沒有文檔可建立向量資料庫")
                return False
            
            logger.info(f"開始建立向量資料庫，共 {len(documents)} 個文檔...")
            
            # 分割文檔
            all_chunks = []
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                all_chunks.extend(chunks)
            
            logger.info(f"文檔分割完成，共 {len(all_chunks)} 個文字塊")
            
            # 添加到向量資料庫
            self.vectordb.add_documents(all_chunks)
            
            # 儲存資料庫
            self.vectordb.save()
            
            logger.info("✅ 向量資料庫建立完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 向量資料庫建立失敗: {e}")
            return False
    
    def load_existing_database(self) -> bool:
        """載入現有資料庫"""
        try:
            if self.vectordb.load():
                logger.info("✅ 向量資料庫載入成功")
                return True
            else:
                logger.warning("⚠️ 向量資料庫不存在，請先建立資料庫")
                return False
        except Exception as e:
            logger.error(f"❌ 向量資料庫載入失敗: {e}")
            return False
    
    def setup_qa_chain(self) -> bool:
        """設定問答鏈"""
        try:
            # 設定檢索器
            self.retriever = self.vectordb
            logger.info("✅ Puter.js 問答鏈設定成功")
            return True
        except Exception as e:
            logger.error(f"❌ 問答鏈設定失敗: {e}")
            return False
    
    @monitor_query("puter_rag_query")
    def query(self, question: str) -> Dict[str, Any]:
        """執行 RAG 查詢"""
        try:
            start_time = time.time()
            
            if not self.retriever:
                return {
                    "error": "system_not_ready",
                    "answer": "系統尚未準備就緒，請先載入資料庫並設定問答鏈。"
                }
            
            # 1. 檢索相關文檔
            relevant_docs = self.retriever.similarity_search(question, k=self.config.RETRIEVER_K)
            
            if not relevant_docs:
                # 如果沒有找到相關文檔，直接查詢
                result = self.puter_manager.query(question)
            else:
                # 2. 構建上下文
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                # 3. 使用 Puter.js 查詢
                result = self.puter_manager.query(question, context=context)
            
            end_time = time.time()
            
            # 4. 處理來源文檔
            sources = []
            for doc in relevant_docs:
                metadata = doc.metadata
                sources.append({
                    "url": metadata.get("source_url", ""),
                    "type": metadata.get("source_type", ""),
                    "description": metadata.get("description", ""),
                    "title": metadata.get("title", ""),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
            # 5. 返回結果
            response = {
                "answer": result.get("answer", "無法取得回答"),
                "sources": sources,
                "query_time": round(end_time - start_time, 2),
                "mode": "puter_js_rag",
                "model": result.get("model"),
                "integration_type": "browser_automation",
                "constraint_compliant": True,
                "tutorial_source": "https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/"
            }
            
            if result.get("error"):
                response["error"] = result["error"]
            
            return response
            
        except Exception as e:
            logger.error(f"Puter.js RAG 查詢失敗: {e}")
            return {
                "error": str(e),
                "answer": f"查詢處理時發生錯誤: {str(e)}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """取得系統狀態"""
        try:
            vectordb_ready = len(self.vectordb.documents) > 0 if self.vectordb else False
            qa_chain_ready = self.retriever is not None
            
            puter_status = self.puter_manager.get_status() if self.puter_manager else {}
            
            return {
                "vectordb_ready": vectordb_ready,
                "qa_chain_ready": qa_chain_ready,
                "puter_integration": puter_status,
                "total_documents": len(self.vectordb.documents) if self.vectordb else 0,
                "last_update": datetime.now().isoformat(),
                "integration_type": "puter_js_browser",
                "constraint_compliant": True
            }
            
        except Exception as e:
            logger.error(f"取得系統狀態失敗: {e}")
            return {"error": str(e)}
    
    def update_database(self) -> bool:
        """更新資料庫"""
        return self.build_vector_database()


# 工廠函數和便利函數
def create_rag_system(config: Optional[Config] = None) -> PuterRAGSystem:
    """建立 Puter.js RAG 系統的工廠函數"""
    return PuterRAGSystem(config)


def quick_query(question: str, config: Optional[Config] = None) -> str:
    """快速查詢函數，使用 Puter.js 整合"""
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


# 向後兼容的別名
ORANNephioRAG = PuterRAGSystem
VectorDatabaseManager = SimplifiedVectorDatabase
QueryProcessor = PuterRAGSystem