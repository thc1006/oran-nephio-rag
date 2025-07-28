"""
文件載入和處理模組
"""
import time
import logging
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from datetime import datetime

from .config import DocumentSource

logger = logging.getLogger(__name__)

class DocumentLoader:
    """改進的文件載入器"""
    
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        
        # 設定通用請求標頭
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def load_document(self, source: DocumentSource) -> Optional[Document]:
        """載入單一文件"""
        if not source.enabled:
            logger.info(f"跳過已禁用的來源: {source.url}")
            return None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"載入文件 (嘗試 {attempt + 1}/{self.max_retries}): {source.description}")
                
                response = self.session.get(source.url, timeout=self.timeout)
                response.raise_for_status()
                
                # 檢查內容類型
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' not in content_type:
                    logger.warning(f"非 HTML 內容: {content_type}")
                
                content = self._extract_content(response.text, source)
                
                if len(content.strip()) < 100:
                    raise ValueError(f"內容太短 ({len(content)} 字元)，可能載入失敗")
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source_url": source.url,
                        "source_type": source.source_type,
                        "description": source.description,
                        "priority": source.priority,
                        "last_updated": datetime.now().isoformat(),
                        "content_length": len(content),
                        "status_code": response.status_code,
                        "content_type": content_type
                    }
                )
                
                logger.info(f"✅ 成功載入: {source.description} ({len(content)} 字元)")
                return doc
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"請求錯誤 (嘗試 {attempt + 1}): {str(e)}")
            except Exception as e:
                logger.warning(f"處理錯誤 (嘗試 {attempt + 1}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                sleep_time = 2 ** attempt
                logger.info(f"等待 {sleep_time} 秒後重試...")
                time.sleep(sleep_time)
        
        logger.error(f"❌ 無法載入文件: {source.url}")
        return None
    
    def _extract_content(self, html: str, source: DocumentSource) -> str:
        """提取頁面主要內容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除不需要的元素
        unwanted_tags = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            'advertisement', 'ads', 'menu', 'sidebar', 'comments'
        ]
        
        for tag_name in unwanted_tags:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # 移除不需要的 class 和 id
        unwanted_classes = [
            'navigation', 'nav', 'menu', 'sidebar', 'ads', 'advertisement',
            'social', 'share', 'comments', 'footer', 'header'
        ]
        
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=class_name):
                element.decompose()
        
        # 嘗試找到主要內容區域
        content_selectors = [
            'main',
            '.main-content',
            '.content',
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '#main-content',
            '.markdown-body',
            '.wiki-content'
        ]
        
        content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content = content_element.get_text(separator='\n', strip=True)
                logger.debug(f"使用選擇器 '{selector}' 提取內容")
                break
        
        # 如果沒有找到特定的內容區域，使用整個 body
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
        
        # 清理內容
        content = self._clean_content(content)
        
        return content
    
    def _clean_content(self, content: str) -> str:
        """清理提取的內容"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳過空行
            if not line:
                continue
            
            # 跳過太短的行（可能是導航元素）
            if len(line) < 3:
                continue
            
            # 跳過可能的導航文字
            skip_patterns = [
                'home', 'back', 'next', 'previous', 'menu', 'search',
                'login', 'logout', 'register', 'subscribe', 'share',
                'twitter', 'facebook', 'linkedin', 'github'
            ]
            
            if any(pattern in line.lower() for pattern in skip_patterns) and len(line) < 20:
                continue
            
            cleaned_lines.append(line)
        
        # 移除重複的連續行
        final_lines = []
        prev_line = ""
        
        for line in cleaned_lines:
            if line != prev_line:
                final_lines.append(line)
                prev_line = line
        
        return '\n'.join(final_lines)
    
    def load_all_documents(self, sources: List[DocumentSource]) -> List[Document]:
        """載入所有文件"""
        documents = []
        successful_count = 0
        
        logger.info(f"開始載入 {len(sources)} 個文件來源...")
        
        for i, source in enumerate(sources, 1):
            logger.info(f"處理來源 {i}/{len(sources)}: {source.description}")
            
            doc = self.load_document(source)
            if doc:
                documents.append(doc)
                successful_count += 1
            
            # 在請求間添加小延遲，避免過於頻繁
            if i < len(sources):
                time.sleep(1)
        
        logger.info(f"成功載入 {successful_count}/{len(sources)} 個文件來源")
        
        if successful_count == 0:
            raise ValueError("無法載入任何文件！請檢查網路連線和文件來源")
        
        return documents
    
    def __del__(self):
        """清理資源"""
        if hasattr(self, 'session'):
            self.session.close()
