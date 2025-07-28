"""
O-RAN × Nephio RAG 系統核心模組
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate

from .config import Config
from .document_loader import DocumentLoader

logger = logging.getLogger(__name__)

class ORANNephioRAG:
    """O-RAN × Nephio 專用的受控檢索系統"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.config.validate()
        
        # 初始化組件
        self._init_embeddings()
        self._init_text_splitter()
        self._init_llm()
        self._init_document_loader()
        
        # 運行時狀態
        self.vectordb = None
        self.qa_chain = None
        self._last_update = None
    
    def _init_embeddings(self):
        """初始化嵌入模型"""
        try:
            logger.info("初始化嵌入模型...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-mpnet-base-v2",
                cache_folder="./embeddings_cache",
                model_kwargs={
                    'device': 'cpu',  # 強制使用 CPU，避免 CUDA 問題
                    'trust_remote_code': False
                }
            )
            logger.info("✅ 嵌入模型初始化成功")
        except Exception as e:
            logger.error(f"❌ 嵌入模型初始化失敗: {e}")
            raise
    
    def _init_text_splitter(self):
        """初始化文本分割器"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _init_llm(self):
        """初始化 Claude LLM"""
        try:
            logger.info("初始化 Claude LLM...")
            self.llm = ChatAnthropic(
                model=self.config.CLAUDE_MODEL,
                anthropic_api_key=self.config.ANTHROPIC_API_KEY,
                temperature=self.config.CLAUDE_TEMPERATURE,
                max_tokens=self.config.CLAUDE_MAX_TOKENS
            )
            logger.info("✅ Claude LLM 初始化成功")
        except Exception as e:
            logger.error(f"❌ Claude LLM 初始化失敗: {e}")
            raise
    
    def _init_document_loader(self):
        """初始化文件載入器"""
        self.document_loader = DocumentLoader()
    
    def build_vector_database(self) -> bool:
        """建立向量資料庫"""
        try:
            logger.info("開始建立向量資料庫...")
            
            # 載入所有文件
            documents = self.document_loader.load_all_documents(
                self.config.OFFICIAL_SOURCES
            )
            
            if not documents:
                logger.error("沒有成功載入任何文件")
                return False
            
            # 分割文件
            logger.info(f"分割 {len(documents)} 個文件...")
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"分割後產生 {len(split_docs)} 個文件塊")
            
            # 建立向量資料庫
            logger.info("建立向量索引...")
            
            # 如果資料庫已存在，先刪除
            if os.path.exists(self.config.VECTOR_DB_PATH):
                import shutil
                shutil.rmtree(self.config.VECTOR_DB_PATH)
            
            self.vectordb = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=self.config.VECTOR_DB_PATH,
                collection_name=self.config.COLLECTION_NAME
            )
            
            self._last_update = datetime.now()
            logger.info("✅ 向量資料庫建立成功！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 建立向量資料庫失敗: {e}")
            return False
    
    def load_existing_database(self) -> bool:
        """載入既有向量資料庫"""
        try:
            if (os.path.exists(self.config.VECTOR_DB_PATH) and 
                os.listdir(self.config.VECTOR_DB_PATH)):
                
                logger.info("載入既有向量資料庫...")
                self.vectordb = Chroma(
                    persist_directory=self.config.VECTOR_DB_PATH,
                    embedding_function=self.embeddings,
                    collection_name=self.config.COLLECTION_NAME
                )
                logger.info("✅ 向量資料庫載入成功")
                return True
            else:
                logger.info("未找到既有資料庫，建立新的...")
                return self.build_vector_database()
                
        except Exception as e:
            logger.warning(f"載入既有資料庫失敗: {e}，將重新建立")
            return self.build_vector_database()
    
    def setup_qa_chain(self) -> bool:
        """設定問答鏈"""
        try:
            if not self.vectordb:
                if not self.load_existing_database():
                    return False
            
            # 自訂提示模板
            prompt_template = """你是一個專精於 O-RAN 和 Nephio 整合的技術專家。請根據以下官方文件內容回答問題。

重要規則：
1. 只能根據提供的官方文件內容回答，不得添加文件中沒有的資訊
2. 如果文件中沒有相關資訊，請明確說明「根據提供的官方文件，暫無此項資訊」
3. 回答時請標明資訊來源（例如：「根據 Nephio 官方文件...」）
4. 專注於 O-RAN Network Function (NF) 的 scale-out 和 scale-in 實作細節
5. 如果文件中有具體的程式碼範例、配置範例或指令，請完整提供
6. 使用繁體中文回答，保持專業和準確
7. 對於複雜的技術概念，提供清晰的解釋和結構化的答案

官方文件內容：
{context}

問題：{question}

請提供詳細、準確且實用的回答："""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # 設定檢索器
            retriever = self.vectordb.as_retriever(
                search_type="mmr",  # Maximum Marginal Relevance
                search_kwargs={
                    "k": 6,  # 返回最相關的 6 個片段
                    "fetch_k": 15,  # 從 15 個候選中選擇
                    "lambda_mult": 0.7  # 平衡相關性和多樣性
                }
            )
            
            # 建立 QA 鏈
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logger.info("✅ 問答鏈設定成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 問答鏈設定失敗: {e}")
            return False
    
    def query(self, question: str) -> Dict[str, Any]:
        """執行查詢"""
        if not self.qa_chain:
            if not self.setup_qa_chain():
                return {
                    "answer": "系統初始化失敗，請稍後再試。",
                    "sources": [],
                    "timestamp": datetime.now().isoformat(),
                    "error": "qa_chain_not_ready"
                }
        
        try:
            logger.info(f"處理查詢: {question[:50]}...")
            
            # 執行查詢
            result = self.qa_chain({"query": question})
            
            # 整理來源資訊
            sources = []
            seen_sources = set()
            
            for doc in result.get("source_documents", []):
                source_url = doc.metadata.get("source_url", "Unknown")
                if source_url not in seen_sources:
                    source_info = {
                        "url": source_url,
                        "type": doc.metadata.get("source_type", "Unknown"),
                        "description": doc.metadata.get("description", ""),
                        "priority": doc.metadata.get("priority", 5),
                        "last_updated": doc.metadata.get("last_updated", "")
                    }
                    sources.append(source_info)
                    seen_sources.add(source_url)
            
            # 按優先級排序來源
            sources.sort(key=lambda x: x["priority"])
            
            return {
                "answer": result["result"],
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "source_count": len(sources)
            }
            
        except Exception as e:
            logger.error(f"查詢處理錯誤: {str(e)}")
            return {
                "answer": f"查詢過程中發生錯誤：{str(e)}",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "vectordb_ready": self.vectordb is not None,
            "qa_chain_ready": self.qa_chain is not None,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "vector_db_path": self.config.VECTOR_DB_PATH,
            "source_count": len(self.config.OFFICIAL_SOURCES),
            "enabled_sources": len([s for s in self.config.OFFICIAL_SOURCES if s.enabled])
        }
    
    def update_database(self) -> bool:
        """更新向量資料庫"""
        logger.info("開始更新向量資料庫...")
        
        if self.build_vector_database():
            # 重新設定 QA 鏈
            return self.setup_qa_chain()
        
        return False
