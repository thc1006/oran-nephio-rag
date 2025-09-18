"""
Enhanced Document Preprocessor for O-RAN × Nephio RAG System
Advanced preprocessing with domain-specific optimization for telecom documentation
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup, Comment
from langchain.docstore.document import Document

# Import configuration
try:
    from .config import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)


@dataclass
class ProcessingMetrics:
    """Document processing metrics"""
    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    total_chars_processed: int = 0
    total_chars_extracted: int = 0
    processing_time: float = 0.0
    technical_terms_extracted: int = 0
    code_blocks_found: int = 0
    diagrams_detected: int = 0


class TelecomTermExtractor:
    """Specialized extractor for O-RAN and Nephio technical terms"""
    
    def __init__(self):
        # O-RAN specific terms
        self.oran_terms = {
            'o-cu', 'o-du', 'o-ru', 'o-cloud', 'smo', 'ric', 'xapp', 'rapp',
            'e2', 'a1', 'o1', 'o2', 'fronthaul', 'midhaul', 'backhaul',
            'open-ran', 'disaggregated-ran', 'ran-intelligent-controller',
            'network-slice', 'massive-mimo', 'beamforming', 'nr', '5g-nr'
        }
        
        # Nephio specific terms
        self.nephio_terms = {
            'porch', 'gitops', 'kpt', 'config-as-data', 'workload-identity',
            'network-function', 'nf', 'cnf', 'vnf', 'provisioning-request',
            'package-orchestration', 'topology-controller', 'repository-controller',
            'interface-controller', 'resource-backend', 'inventory-management'
        }
        
        # Kubernetes and cloud-native terms
        self.k8s_terms = {
            'kubernetes', 'k8s', 'pod', 'deployment', 'service', 'ingress',
            'namespace', 'configmap', 'secret', 'pvc', 'helm', 'operator',
            'crd', 'custom-resource', 'controller', 'reconciliation', 'admission-webhook'
        }
        
        # Network and telecom general terms
        self.telecom_terms = {
            'network-function', 'service-mesh', 'load-balancer', 'autoscaling',
            'edge-computing', 'multi-cluster', 'federation', 'observability',
            'telemetry', 'monitoring', 'alerting', 'sla', 'slo', 'latency',
            'throughput', 'availability', 'fault-tolerance', 'disaster-recovery'
        }
        
        self.all_terms = (
            self.oran_terms | self.nephio_terms | 
            self.k8s_terms | self.telecom_terms
        )
        
        # Compile regex patterns for efficient matching
        self.term_patterns = {
            term: re.compile(r'\b' + re.escape(term.replace('-', r'[-\s]?')) + r'\b', re.IGNORECASE)
            for term in self.all_terms
        }
    
    def extract_terms(self, text: str) -> Dict[str, List[str]]:
        """Extract technical terms from text"""
        found_terms = {
            'oran': [],
            'nephio': [],
            'k8s': [],
            'telecom': []
        }
        
        text_lower = text.lower()
        
        for term in self.oran_terms:
            if self.term_patterns[term].search(text):
                found_terms['oran'].append(term)
        
        for term in self.nephio_terms:
            if self.term_patterns[term].search(text):
                found_terms['nephio'].append(term)
        
        for term in self.k8s_terms:
            if self.term_patterns[term].search(text):
                found_terms['k8s'].append(term)
        
        for term in self.telecom_terms:
            if self.term_patterns[term].search(text):
                found_terms['telecom'].append(term)
        
        return found_terms


class CodeBlockExtractor:
    """Extract and process code blocks from documentation"""
    
    def __init__(self):
        # Pattern for code blocks
        self.code_patterns = [
            r'```[\w]*\n([\s\S]*?)```',  # Markdown code blocks
            r'<code[^>]*>([\s\S]*?)</code>',  # HTML code tags
            r'<pre[^>]*>([\s\S]*?)</pre>',  # HTML pre tags
            r'`([^`\n]+)`',  # Inline code
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.MULTILINE) for pattern in self.code_patterns]
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extract code blocks with metadata"""
        code_blocks = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.finditer(text)
            for match in matches:
                code_content = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                # Determine code type
                code_type = self._identify_code_type(code_content)
                
                code_blocks.append({
                    'content': code_content.strip(),
                    'type': code_type,
                    'pattern_index': i,
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'length': len(code_content)
                })
        
        return code_blocks
    
    def _identify_code_type(self, code: str) -> str:
        """Identify the type of code block"""
        code_lower = code.lower()
        
        if 'apiversion:' in code_lower or 'kind:' in code_lower:
            return 'kubernetes_yaml'
        elif 'kubectl' in code_lower:
            return 'kubectl_command'
        elif 'helm' in code_lower:
            return 'helm_command'
        elif 'docker' in code_lower:
            return 'docker_command'
        elif code.startswith('#!/'):
            return 'shell_script'
        elif any(lang in code_lower for lang in ['def ', 'class ', 'import ', 'from ']):
            return 'python'
        elif any(lang in code_lower for lang in ['function', 'const', 'let', 'var']):
            return 'javascript'
        elif '{' in code and '}' in code:
            return 'json_or_config'
        else:
            return 'generic'


class DiagramDetector:
    """Detect and extract diagram references from documentation"""
    
    def __init__(self):
        self.diagram_indicators = [
            'figure', 'diagram', 'chart', 'graph', 'architecture',
            'topology', 'flow', 'sequence', 'component', 'deployment'
        ]
        
        self.image_patterns = [
            r'!\[[^\]]*\]\([^)]+\)',  # Markdown images
            r'<img[^>]+>',  # HTML images
            r'<figure[^>]*>([\s\S]*?)</figure>',  # HTML figures
        ]
        
        self.compiled_image_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.image_patterns]
    
    def detect_diagrams(self, text: str, html_content: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detect diagram references and descriptions"""
        diagrams = []
        
        # Check for explicit diagram mentions
        for indicator in self.diagram_indicators:
            pattern = re.compile(r'\b' + indicator + r'\s+\d+[:.\s]*([^\n]{1,200})', re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                diagrams.append({
                    'type': 'diagram_reference',
                    'indicator': indicator,
                    'description': match.group(1).strip(),
                    'position': match.start()
                })
        
        # Extract image references
        for pattern in self.compiled_image_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                diagrams.append({
                    'type': 'image_reference',
                    'content': match.group(0),
                    'position': match.start()
                })
        
        return diagrams


class EnhancedDocumentPreprocessor:
    """Enhanced document preprocessor with O-RAN/Nephio optimization"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.term_extractor = TelecomTermExtractor()
        self.code_extractor = CodeBlockExtractor()
        self.diagram_detector = DiagramDetector()
        self.metrics = ProcessingMetrics()
        
        # Preprocessing rules
        self.noise_patterns = [
            r'\b(click|here|more|info|details|link|url)\b',
            r'\b(home|back|next|previous|menu|search)\b',
            r'\b(login|logout|register|subscribe|share)\b',
            r'\b(twitter|facebook|linkedin|github|youtube)\b',
            r'©\s*\d{4}',  # Copyright notices
            r'\bpowered\s+by\b',
            r'\b(privacy|policy|terms|conditions)\b'
        ]
        
        self.compiled_noise_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.noise_patterns]
        
        logger.info("Enhanced document preprocessor initialized")
    
    async def process_documents(self, documents: List[Document]) -> List[Document]:
        """Process multiple documents concurrently"""
        start_time = datetime.now()
        self.metrics.total_documents = len(documents)
        
        logger.info(f"Starting processing of {len(documents)} documents")
        
        # Process documents in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, self.process_single_document, doc)
                for doc in documents
            ]
            
            processed_docs = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed documents and exceptions
        valid_docs = []
        for doc in processed_docs:
            if isinstance(doc, Document):
                valid_docs.append(doc)
                self.metrics.processed_documents += 1
            else:
                self.metrics.failed_documents += 1
                if isinstance(doc, Exception):
                    logger.error(f"Document processing failed: {doc}")
        
        # Update metrics
        self.metrics.processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Processing complete: {self.metrics.processed_documents} successful, "
                   f"{self.metrics.failed_documents} failed, {self.metrics.processing_time:.2f}s")
        
        return valid_docs
    
    def process_single_document(self, document: Document) -> Document:
        """Process a single document with enhanced preprocessing"""
        try:
            original_content = document.page_content
            self.metrics.total_chars_processed += len(original_content)
            
            # Clean HTML if present
            if '<html>' in original_content.lower() or '<body>' in original_content.lower():
                cleaned_content = self._clean_html_content(original_content)
            else:
                cleaned_content = original_content
            
            # Extract technical terms
            technical_terms = self.term_extractor.extract_terms(cleaned_content)
            
            # Extract code blocks
            code_blocks = self.code_extractor.extract_code_blocks(cleaned_content)
            
            # Detect diagrams
            diagrams = self.diagram_detector.detect_diagrams(cleaned_content)
            
            # Clean and enhance content
            enhanced_content = self._enhance_content(cleaned_content)
            
            # Remove noise
            clean_content = self._remove_noise(enhanced_content)
            
            # Update metrics
            self.metrics.total_chars_extracted += len(clean_content)
            self.metrics.technical_terms_extracted += sum(len(terms) for terms in technical_terms.values())
            self.metrics.code_blocks_found += len(code_blocks)
            self.metrics.diagrams_detected += len(diagrams)
            
            # Enhance metadata
            enhanced_metadata = self._enhance_metadata(
                document.metadata, technical_terms, code_blocks, diagrams
            )
            
            return Document(
                page_content=clean_content,
                metadata=enhanced_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            raise
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content while preserving structure"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Remove navigation and footer elements
            for tag in soup.find_all(['nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # Extract text while preserving some structure
            text = soup.get_text(separator='\n', strip=True)
            
            return text
            
        except Exception as e:
            logger.warning(f"HTML cleaning failed: {e}")
            return html_content
    
    def _enhance_content(self, content: str) -> str:
        """Enhance content with better structure and formatting"""
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Enhance headings
            if self._is_heading(line):
                enhanced_lines.append(f"\n{line}\n")
            # Enhance list items
            elif line.startswith(('-', '*', '•')) or re.match(r'^\d+\.', line):
                enhanced_lines.append(line)
            # Regular content
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _is_heading(self, line: str) -> bool:
        """Determine if a line is a heading"""
        # Check for markdown-style headings
        if line.startswith('#'):
            return True
        
        # Check for common heading patterns
        heading_patterns = [
            r'^[A-Z][A-Za-z\s]+:$',  # Title Case with colon
            r'^[A-Z\s]+$',  # ALL CAPS
            r'^\d+\.[\d\.]*\s+[A-Z]',  # Numbered sections
        ]
        
        return any(re.match(pattern, line) for pattern in heading_patterns)
    
    def _remove_noise(self, content: str) -> str:
        """Remove noise patterns from content"""
        for pattern in self.compiled_noise_patterns:
            content = pattern.sub('', content)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _enhance_metadata(self, original_metadata: Dict[str, Any], 
                         technical_terms: Dict[str, List[str]], 
                         code_blocks: List[Dict[str, Any]], 
                         diagrams: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance document metadata with extracted information"""
        enhanced_metadata = original_metadata.copy()
        
        # Add technical term analysis
        enhanced_metadata.update({
            'technical_terms': technical_terms,
            'oran_terms_count': len(technical_terms.get('oran', [])),
            'nephio_terms_count': len(technical_terms.get('nephio', [])),
            'k8s_terms_count': len(technical_terms.get('k8s', [])),
            'telecom_terms_count': len(technical_terms.get('telecom', [])),
            'total_technical_terms': sum(len(terms) for terms in technical_terms.values())
        })
        
        # Add code analysis
        enhanced_metadata.update({
            'code_blocks_count': len(code_blocks),
            'code_types': list(set(block['type'] for block in code_blocks)),
            'has_kubernetes_yaml': any(block['type'] == 'kubernetes_yaml' for block in code_blocks),
            'has_kubectl_commands': any(block['type'] == 'kubectl_command' for block in code_blocks)
        })
        
        # Add diagram analysis
        enhanced_metadata.update({
            'diagrams_count': len(diagrams),
            'diagram_types': list(set(diag['type'] for diag in diagrams))
        })
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(technical_terms, code_blocks, diagrams)
        enhanced_metadata['relevance_score'] = relevance_score
        
        # Add processing timestamp
        enhanced_metadata['preprocessing_timestamp'] = datetime.now().isoformat()
        
        return enhanced_metadata
    
    def _calculate_relevance_score(self, technical_terms: Dict[str, List[str]], 
                                  code_blocks: List[Dict[str, Any]], 
                                  diagrams: List[Dict[str, Any]]) -> float:
        """Calculate document relevance score for O-RAN/Nephio context"""
        score = 0.0
        
        # Technical terms scoring
        score += len(technical_terms.get('oran', [])) * 3.0  # O-RAN terms are most valuable
        score += len(technical_terms.get('nephio', [])) * 3.0  # Nephio terms equally valuable
        score += len(technical_terms.get('k8s', [])) * 2.0  # Kubernetes terms valuable
        score += len(technical_terms.get('telecom', [])) * 1.0  # General telecom terms
        
        # Code blocks scoring
        for block in code_blocks:
            if block['type'] == 'kubernetes_yaml':
                score += 5.0
            elif block['type'] in ['kubectl_command', 'helm_command']:
                score += 3.0
            else:
                score += 1.0
        
        # Diagrams scoring
        score += len(diagrams) * 2.0
        
        # Normalize score (0-100)
        return min(score, 100.0)
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            'total_documents': self.metrics.total_documents,
            'processed_documents': self.metrics.processed_documents,
            'failed_documents': self.metrics.failed_documents,
            'success_rate': (self.metrics.processed_documents / max(self.metrics.total_documents, 1)) * 100,
            'total_chars_processed': self.metrics.total_chars_processed,
            'total_chars_extracted': self.metrics.total_chars_extracted,
            'compression_ratio': self.metrics.total_chars_extracted / max(self.metrics.total_chars_processed, 1),
            'processing_time': self.metrics.processing_time,
            'docs_per_second': self.metrics.processed_documents / max(self.metrics.processing_time, 0.1),
            'technical_terms_extracted': self.metrics.technical_terms_extracted,
            'code_blocks_found': self.metrics.code_blocks_found,
            'diagrams_detected': self.metrics.diagrams_detected
        }


# Factory function
def create_enhanced_preprocessor(config: Optional[Config] = None) -> EnhancedDocumentPreprocessor:
    """Create enhanced document preprocessor"""
    return EnhancedDocumentPreprocessor(config)
