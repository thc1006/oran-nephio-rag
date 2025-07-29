"""
O-RAN × Nephio RAG 系統文件載入模組
"""
import time
import logging
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Comment
from langchain.docstore.document import Document

try:
    from .config import DocumentSource, Config
except ImportError:
    from config import DocumentSource, Config

# 設定模組日誌記錄器
logger = logging.getLogger(__name__)

class DocumentContentCleaner:
    """文件內容清理器"""
    
    def __init__(self, config: Optional['Config'] = None):
        try:
            from .config import Config
        except ImportError:
            from config import Config
        self.config = config or Config()
        
        # 不需要的 HTML 標籤
        self.unwanted_tags = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            'advertisement', 'ads', 'menu', 'sidebar', 'comments',
            'social-share', 'cookie-notice', 'breadcrumb'
        ]
        
        # 不需要的 CSS 類別和 ID
        self.unwanted_selectors = [
            '.navigation', '.nav', '.menu', '.sidebar', '.ads', 
            '.advertisement', '.social', '.share', '.comments', 
            '.footer', '.header', '.breadcrumb', '.cookie-notice',
            '#navigation', '#nav', '#menu', '#sidebar', '#ads',
            '#advertisement', '#social', '#share', '#comments',
            '#footer', '#header', '#breadcrumb'
        ]
        
        # 跳過的文字模式
        self.skip_patterns = [
            r'^(home|back|next|previous|menu|search)$',
            r'^(login|logout|register|subscribe|share)$',
            r'^(twitter|facebook|linkedin|github|youtube)$',
            r'^(cookie|privacy|terms|policy)$',
            r'^\s*\d+\s*$',  # 純數字
            r'^[<>]+$',      # 純符號
        ]
        
        # 編譯正則表達式以提高效能
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.skip_patterns]
    
    def clean_html(self, html_content: str, base_url: str = "") -> str:
        """清理 HTML 內容，提取主要文字"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除註解
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # 移除不需要的標籤
            for tag_name in self.unwanted_tags:
                for element in soup.find_all(tag_name):
                    element.decompose()
            
            # 移除不需要的選擇器
            for selector in self.unwanted_selectors:
                try:
                    for element in soup.select(selector):
                        element.decompose()
                except Exception as e:
                    logger.debug(f"選擇器 {selector} 處理失敗: {e}")
            
            # 嘗試找到主要內容區域
            main_content = self._extract_main_content(soup)
            
            if main_content:
                # 處理相對連結
                self._process_links(main_content, base_url)
                
                # 提取文字內容
                text_content = main_content.get_text(separator='\n', strip=True)
            else:
                # 如果找不到主要內容，使用整個 body
                body = soup.find('body')
                if body:
                    text_content = body.get_text(separator='\n', strip=True)
                else:
                    text_content = soup.get_text(separator='\n', strip=True)
            
            # 清理文字內容
            cleaned_text = self._clean_text_content(text_content)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"HTML 清理失敗: {e}")
            return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """提取主要內容區域"""
        # 優先選擇器列表，按優先級排序
        content_selectors = [
            'main',
            '.main-content',
            '.markdown-body',
            '.wiki-content',
            '.content',
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '#main-content',
            '#content',
            '.container .content',
            '.page-content'
        ]
        
        for selector in content_selectors:
            try:
                content_element = soup.select_one(selector)
                if content_element and len(content_element.get_text(strip=True)) > self.config.MIN_EXTRACTED_CONTENT_LENGTH:
                    logger.debug(f"使用選擇器 '{selector}' 找到主要內容")
                    return content_element
            except Exception as e:
                logger.debug(f"選擇器 {selector} 查找失敗: {e}")
        
        logger.debug("未找到特定的主要內容區域")
        return None
    
    def _process_links(self, content: BeautifulSoup, base_url: str):
        """處理相對連結"""
        if not base_url:
            return
        
        try:
            for link in content.find_all('a', href=True):
                href = link['href']
                if href.startswith('/') or not href.startswith('http'):
                    absolute_url = urljoin(base_url, href)
                    link['href'] = absolute_url
        except Exception as e:
            logger.debug(f"處理連結失敗: {e}")
    
    def _clean_text_content(self, text: str) -> str:
        """清理文字內容"""
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        prev_line = ""
        
        for line in lines:
            line = line.strip()
            
            # 跳過空行
            if not line:
                continue
            
            # 跳過太短的行（可能是導航元素）
            if len(line) < self.config.MIN_LINE_LENGTH:
                continue
            
            # 跳過符合跳過模式的行
            if any(pattern.match(line) for pattern in self.compiled_patterns):
                continue
            
            # 跳過重複的連續行
            if line == prev_line:
                continue
            
            # 移除多餘的空白字元
            line = re.sub(r'\s+', ' ', line)
            
            cleaned_lines.append(line)
            prev_line = line
        
        # 合併短行（可能是被錯誤分割的句子）
        merged_lines = self._merge_short_lines(cleaned_lines)
        
        return '\n'.join(merged_lines)
    
    def _merge_short_lines(self, lines: List[str]) -> List[str]:
        """合併可能被錯誤分割的短行"""
        if not lines:
            return lines
        
        merged = []
        current_line = ""
        
        for line in lines:
            # 如果當前行很短且不以句號結尾，可能需要與下一行合併
            if (len(current_line) > 0 and 
                len(current_line) < self.config.MAX_LINE_MERGE_LENGTH and 
                not current_line.endswith(('.', '!', '?', ':', ';', '。', '！', '？', '：', '；')) and
                not line.startswith(('#', '-', '*', '1.', '2.', '3.', '4.', '5.'))):
                current_line += " " + line
            else:
                if current_line:
                    merged.append(current_line)
                current_line = line
        
        if current_line:
            merged.append(current_line)
        
        return merged

class DocumentLoader:
    """強化的文件載入器"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.max_retries = self.config.MAX_RETRIES
        self.timeout = self.config.REQUEST_TIMEOUT
        
        # 初始化 HTTP 會話
        self.session = requests.Session()
        
        # 設定請求標頭
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        
        # 設定會話配置
        self.session.max_redirects = 5
        
        # 初始化內容清理器
        try:
            self.content_cleaner = DocumentContentCleaner(self.config)
        except Exception as e:
            logger.error(f"內容清理器初始化失敗: {e}")
            raise
        
        # 載入統計
        self.stats = {
            'total_attempts': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'retry_attempts': 0
        }
        
        logger.debug("文件載入器初始化完成")
    
    def load_document(self, source: DocumentSource) -> Optional[Document]:
        """載入單一文件來源"""
        if not source.enabled:
            logger.info(f"跳過已停用的來源: {source.url}")
            return None
        
        self.stats['total_attempts'] += 1
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    self.stats['retry_attempts'] += 1
                
                logger.info(f"載入文件 (嘗試 {attempt + 1}/{self.max_retries}): {source.description}")
                
                # 發送 HTTP 請求
                response = self._make_request(source.url)
                
                # 驗證回應
                self._validate_response(response, source)
                
                # 提取內容
                content = self._extract_content(response, source)
                
                # 驗證內容品質
                self._validate_content(content)
                
                # 建立文件物件
                doc = self._create_document(content, source, response)
                
                self.stats['successful_loads'] += 1
                logger.info(f"✅ 成功載入: {source.description} ({len(content)} 字元)")
                
                return doc
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"網路請求錯誤 (嘗試 {attempt + 1}): {str(e)}")
            except Exception as e:
                logger.warning(f"載入錯誤 (嘗試 {attempt + 1}): {str(e)}")
            
            # 重試前等待
            if attempt < self.max_retries - 1:
                wait_time = min(self.config.RETRY_DELAY_BASE ** attempt, self.config.MAX_RETRY_DELAY)  # 指數退避
                logger.info(f"等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
        
        self.stats['failed_loads'] += 1
        logger.error(f"❌ 無法載入文件: {source.url}")
        return None
    
    def _make_request(self, url: str) -> requests.Response:
        """發送 HTTP 請求"""
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                stream=False,
                verify=self.config.VERIFY_SSL  # 啟用 SSL 憑證驗證
            )
            response.raise_for_status()
            return response
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL 憑證驗證失敗: {e}")
            logger.warning("如果您確信網站安全，可在 .env 中設定 VERIFY_SSL=false")
            raise
        except Exception as e:
            logger.error(f"HTTP 請求失敗: {e}")
            raise
    
    def _validate_response(self, response: requests.Response, source: DocumentSource):
        """驗證 HTTP 回應"""
        # 檢查內容類型
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            logger.warning(f"非 HTML 內容類型: {content_type}")
        
        # 檢查內容長度
        content_length = len(response.content)
        if content_length < self.config.MIN_CONTENT_LENGTH:
            raise ValueError(f"回應內容太短 ({content_length} bytes，最少需要 {self.config.MIN_CONTENT_LENGTH} bytes)")
        
        # 檢查狀態碼
        if response.status_code != 200:
            raise ValueError(f"HTTP 狀態碼錯誤: {response.status_code}")
    
    def _extract_content(self, response: requests.Response, source: DocumentSource) -> str:
        """提取頁面內容"""
        # 取得編碼
        encoding = response.encoding or 'utf-8'
        
        try:
            html_content = response.content.decode(encoding)
        except UnicodeDecodeError:
            # 嘗試其他編碼
            for fallback_encoding in ['utf-8', 'iso-8859-1', 'cp1252']:
                try:
                    html_content = response.content.decode(fallback_encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("無法解碼 HTML 內容")
        
        # 清理 HTML 並提取文字
        content = self.content_cleaner.clean_html(html_content, response.url)
        
        return content
    
    def _validate_content(self, content: str):
        """驗證提取的內容品質"""
        if not content or len(content.strip()) < self.config.MIN_EXTRACTED_CONTENT_LENGTH:
            raise ValueError(f"提取的內容太短 ({len(content)} 字元，最少需要 {self.config.MIN_EXTRACTED_CONTENT_LENGTH} 字元)")
        
        # 檢查是否包含相關關鍵字（針對 O-RAN 和 Nephio 文件）
        relevant_keywords = [
            'nephio', 'o-ran', 'oran', 'kubernetes', 'gitops',
            'network function', 'nf', 'deployment', 'scale',
            'cluster', 'workload', 'operator'
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in relevant_keywords if keyword in content_lower)
        
        if keyword_count < self.config.MIN_KEYWORD_COUNT:
            logger.warning(f"內容可能不相關，找到的關鍵字數量: {keyword_count}，最少需要 {self.config.MIN_KEYWORD_COUNT} 個")
    
    def _create_document(self, content: str, source: DocumentSource, response: requests.Response) -> Document:
        """建立 LangChain Document 物件"""
        try:
            # 提取額外的 metadata
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = ""
            if soup.title:
                title = soup.title.get_text(strip=True)
            
            # 嘗試從 meta 標籤取得描述
            description_meta = soup.find('meta', attrs={'name': 'description'})
            meta_description = ""
            if description_meta:
                meta_description = description_meta.get('content', '')
            
        except Exception as e:
            logger.warning(f"提取 metadata 失敗: {e}")
            title = ""
            meta_description = ""
        
        # 建立 metadata
        metadata = {
            "source_url": source.url,
            "source_type": source.source_type,
            "description": source.description,
            "priority": source.priority,
            "last_updated": datetime.now().isoformat(),
            "content_length": len(content),
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type', ''),
            "title": title,
            "meta_description": meta_description,
            "final_url": response.url,  # 可能因重導向而不同
            "load_timestamp": time.time()
        }
        
        return Document(page_content=content, metadata=metadata)
    
    def load_all_documents(self, sources: List[DocumentSource]) -> List[Document]:
        """載入所有白名單文件，從根源封鎖雜訊"""
        logger.info(f"開始載入 {len(sources)} 個官方文件來源...")
        
        # 重置統計
        self.stats = {
            'total_attempts': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'retry_attempts': 0
        }
        
        documents = []
        start_time = time.time()
        
        for i, source in enumerate(sources, 1):
            logger.info(f"處理來源 {i}/{len(sources)}: {source.description}")
            
            # 載入文件
            doc = self.load_document(source)
            if doc:
                documents.append(doc)
            
            # 在請求間添加延遲，避免對伺服器造成壓力
            if i < len(sources):
                time.sleep(self.config.REQUEST_DELAY)
        
        end_time = time.time()
        
        # 記錄統計資訊
        logger.info(f"載入完成統計:")
        logger.info(f"  總載入時間: {end_time - start_time:.2f} 秒")
        logger.info(f"  成功載入: {self.stats['successful_loads']}/{len(sources)}")
        logger.info(f"  失敗載入: {self.stats['failed_loads']}")
        logger.info(f"  重試次數: {self.stats['retry_attempts']}")
        
        if not documents:
            raise ValueError("無法載入任何官方文件！請檢查網路連線和文件來源配置")
        
        return documents
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """取得載入統計資訊"""
        total_attempts = self.stats['total_attempts']
        success_rate = (self.stats['successful_loads'] / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "total_attempts": total_attempts,
            "successful_loads": self.stats['successful_loads'],
            "failed_loads": self.stats['failed_loads'],
            "retry_attempts": self.stats['retry_attempts'],
            "success_rate": round(success_rate, 2)
        }
    
    def __del__(self):
        """清理資源"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
        except Exception as e:
            logger.debug(f"資源清理失敗: {e}")

def create_document_loader(config: Optional[Config] = None) -> DocumentLoader:
    """建立文件載入器的工廠函數"""
    return DocumentLoader(config)
