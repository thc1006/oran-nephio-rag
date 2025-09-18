"""
Smart Text Chunking System for O-RAN × Nephio RAG
Advanced semantic-aware chunking with domain-specific optimization
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import math

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import sentence transformers if available for semantic chunking
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Import configuration
try:
    from .config import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for individual chunks"""
    chunk_id: str
    chunk_index: int
    chunk_type: str  # 'content', 'code', 'heading', 'list'
    parent_document_id: str
    semantic_density: float
    technical_term_count: int
    code_block_count: int
    heading_level: int
    relevance_score: float
    neighbor_chunks: List[str]
    split_method: str


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies"""
    
    @abstractmethod
    def chunk_document(self, document: Document) -> List[Document]:
        """Chunk a document into smaller pieces"""
        pass


class SemanticChunker(ChunkingStrategy):
    """Semantic-aware chunking using sentence embeddings"""
    
    def __init__(self, config: Config, similarity_threshold: float = 0.7):
        self.config = config
        self.similarity_threshold = similarity_threshold
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Semantic chunker initialized with sentence transformers")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer model: {e}")
                self.model = None
        else:
            logger.warning("Sentence transformers not available, using fallback chunking")
            self.model = None
    
    def chunk_document(self, document: Document) -> List[Document]:
        """Chunk document using semantic similarity"""
        if self.model is None:
            # Fallback to basic chunking
            return self._fallback_chunk(document)
        
        try:
            # Split into sentences
            sentences = self._split_into_sentences(document.page_content)
            
            if len(sentences) <= 3:
                return [document]  # Too few sentences to chunk effectively
            
            # Get sentence embeddings
            embeddings = self.model.encode(sentences)
            
            # Find semantic boundaries
            boundaries = self._find_semantic_boundaries(embeddings)
            
            # Create chunks based on boundaries
            chunks = self._create_chunks_from_boundaries(document, sentences, boundaries)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Semantic chunking failed: {e}")
            return self._fallback_chunk(document)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Enhanced sentence splitting for technical documentation
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and not sentence.isdigit():  # Filter out very short or numeric-only sentences
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _find_semantic_boundaries(self, embeddings: np.ndarray) -> List[int]:
        """Find semantic boundaries in the embedding sequence"""
        boundaries = [0]  # Always start with first sentence
        
        for i in range(1, len(embeddings) - 1):
            # Calculate similarity with previous and next sentences
            prev_sim = cosine_similarity([embeddings[i]], [embeddings[i-1]])[0][0]
            next_sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
            
            # If similarity drops significantly, it's a boundary
            if prev_sim < self.similarity_threshold and next_sim < self.similarity_threshold:
                boundaries.append(i)
        
        boundaries.append(len(embeddings))  # Always end with last sentence
        return boundaries
    
    def _create_chunks_from_boundaries(self, document: Document, 
                                     sentences: List[str], 
                                     boundaries: List[int]) -> List[Document]:
        """Create document chunks from semantic boundaries"""
        chunks = []
        
        for i in range(len(boundaries) - 1):
            start_idx = boundaries[i]
            end_idx = boundaries[i + 1]
            
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_content = ' '.join(chunk_sentences)
            
            # Skip very small chunks
            if len(chunk_content) < 50:
                continue
            
            # Create chunk metadata
            chunk_metadata = document.metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'chunk_type': 'semantic',
                'chunk_method': 'semantic_similarity',
                'sentence_count': len(chunk_sentences),
                'chunk_boundaries': f"{start_idx}-{end_idx}"
            })
            
            chunks.append(Document(
                page_content=chunk_content,
                metadata=chunk_metadata
            ))
        
        return chunks
    
    def _fallback_chunk(self, document: Document) -> List[Document]:
        """Fallback chunking method"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len
        )
        
        chunks = splitter.split_documents([document])
        
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                'chunk_index': i,
                'chunk_type': 'fallback',
                'chunk_method': 'recursive_text_splitter'
            })
        
        return chunks


class StructuralChunker(ChunkingStrategy):
    """Structure-aware chunking based on document structure"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Patterns for different structural elements
        self.heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headings
            r'^([A-Z][A-Za-z\s]+):$',  # Title case with colon
            r'^\d+\.\s+(.+)$',  # Numbered sections
            r'^([A-Z\s]{3,})$',  # ALL CAPS headings
        ]
        
        self.list_patterns = [
            r'^\s*[-*+]\s+(.+)$',  # Bullet lists
            r'^\s*\d+\.\s+(.+)$',  # Numbered lists
            r'^\s*[a-zA-Z]\)\s+(.+)$',  # Lettered lists
        ]
        
        self.code_patterns = [
            r'```[\w]*\n([\s\S]*?)```',  # Code blocks
            r'`([^`]+)`',  # Inline code
        ]
    
    def chunk_document(self, document: Document) -> List[Document]:
        """Chunk document based on structural elements"""
        content = document.page_content
        lines = content.split('\n')
        
        # Analyze document structure
        structure = self._analyze_structure(lines)
        
        # Create chunks based on structure
        chunks = self._create_structural_chunks(document, lines, structure)
        
        return chunks
    
    def _analyze_structure(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Analyze document structure"""
        structure = []
        
        for i, line in enumerate(lines):
            line_info = {
                'line_index': i,
                'content': line,
                'type': 'content',
                'level': 0
            }
            
            # Check for headings
            for pattern in self.heading_patterns:
                match = re.match(pattern, line)
                if match:
                    line_info['type'] = 'heading'
                    line_info['heading_text'] = match.group(1) if len(match.groups()) > 0 else line
                    line_info['level'] = self._get_heading_level(line)
                    break
            
            # Check for lists
            if line_info['type'] == 'content':
                for pattern in self.list_patterns:
                    if re.match(pattern, line):
                        line_info['type'] = 'list_item'
                        break
            
            # Check for code
            if line_info['type'] == 'content':
                for pattern in self.code_patterns:
                    if re.search(pattern, line):
                        line_info['type'] = 'code'
                        break
            
            structure.append(line_info)
        
        return structure
    
    def _get_heading_level(self, line: str) -> int:
        """Get heading level from line"""
        if line.startswith('#'):
            return len(line) - len(line.lstrip('#'))
        elif re.match(r'^\d+\.', line):
            return line.count('.') + 1
        else:
            return 1
    
    def _create_structural_chunks(self, document: Document, 
                                lines: List[str], 
                                structure: List[Dict[str, Any]]) -> List[Document]:
        """Create chunks based on structural analysis"""
        chunks = []
        current_chunk_lines = []
        current_chunk_type = 'content'
        chunk_index = 0
        
        for line_info in structure:
            line = line_info['content']
            line_type = line_info['type']
            
            # Start new chunk on major headings
            if line_type == 'heading' and line_info.get('level', 0) <= 2:
                if current_chunk_lines:
                    # Finalize current chunk
                    chunk = self._create_chunk_from_lines(
                        document, current_chunk_lines, current_chunk_type, chunk_index
                    )
                    if chunk:
                        chunks.append(chunk)
                        chunk_index += 1
                
                # Start new chunk
                current_chunk_lines = [line]
                current_chunk_type = 'heading_section'
            else:
                current_chunk_lines.append(line)
                
                # Update chunk type based on content
                if line_type == 'code' and current_chunk_type != 'heading_section':
                    current_chunk_type = 'code_section'
                elif line_type == 'list_item' and current_chunk_type == 'content':
                    current_chunk_type = 'list_section'
            
            # Check if chunk is getting too large
            chunk_content = '\n'.join(current_chunk_lines)
            if len(chunk_content) > self.config.CHUNK_SIZE * 1.5:
                # Finalize current chunk
                chunk = self._create_chunk_from_lines(
                    document, current_chunk_lines, current_chunk_type, chunk_index
                )
                if chunk:
                    chunks.append(chunk)
                    chunk_index += 1
                
                current_chunk_lines = []
                current_chunk_type = 'content'
        
        # Handle remaining content
        if current_chunk_lines:
            chunk = self._create_chunk_from_lines(
                document, current_chunk_lines, current_chunk_type, chunk_index
            )
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _create_chunk_from_lines(self, document: Document, 
                               lines: List[str], 
                               chunk_type: str, 
                               chunk_index: int) -> Optional[Document]:
        """Create a document chunk from lines"""
        content = '\n'.join(lines).strip()
        
        if len(content) < 50:  # Skip very small chunks
            return None
        
        # Create chunk metadata
        chunk_metadata = document.metadata.copy()
        chunk_metadata.update({
            'chunk_index': chunk_index,
            'chunk_type': chunk_type,
            'chunk_method': 'structural',
            'line_count': len(lines),
            'chunk_size': len(content)
        })
        
        return Document(
            page_content=content,
            metadata=chunk_metadata
        )


class HybridChunker(ChunkingStrategy):
    """Hybrid chunking combining semantic and structural approaches"""
    
    def __init__(self, config: Config):
        self.config = config
        self.semantic_chunker = SemanticChunker(config)
        self.structural_chunker = StructuralChunker(config)
        
        # Chunking preferences for different document types
        self.chunking_preferences = {
            'high_code_content': 'structural',  # Prefer structural for code-heavy docs
            'high_technical_terms': 'semantic',  # Prefer semantic for technical docs
            'balanced': 'hybrid'  # Use both approaches
        }
    
    def chunk_document(self, document: Document) -> List[Document]:
        """Chunk document using hybrid approach"""
        # Analyze document characteristics
        doc_type = self._analyze_document_type(document)
        
        if doc_type == 'high_code_content':
            return self.structural_chunker.chunk_document(document)
        elif doc_type == 'high_technical_terms' and SENTENCE_TRANSFORMERS_AVAILABLE:
            return self.semantic_chunker.chunk_document(document)
        else:
            # Use hybrid approach
            return self._hybrid_chunk(document)
    
    def _analyze_document_type(self, document: Document) -> str:
        """Analyze document to determine best chunking strategy"""
        content = document.page_content
        metadata = document.metadata
        
        # Check code content ratio
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        code_lines = len(re.findall(r'^\s*[{};]\s*$', content, re.MULTILINE))
        total_lines = len(content.split('\n'))
        
        code_ratio = (code_blocks * 10 + code_lines) / max(total_lines, 1)
        
        # Check technical terms from metadata
        tech_terms_count = metadata.get('total_technical_terms', 0)
        content_length = len(content)
        tech_density = tech_terms_count / max(content_length / 100, 1)  # terms per 100 chars
        
        if code_ratio > 0.3:
            return 'high_code_content'
        elif tech_density > 2.0:
            return 'high_technical_terms'
        else:
            return 'balanced'
    
    def _hybrid_chunk(self, document: Document) -> List[Document]:
        """Apply hybrid chunking strategy"""
        # First, use structural chunking to identify major sections
        structural_chunks = self.structural_chunker.chunk_document(document)
        
        # Then, apply semantic chunking to large sections
        final_chunks = []
        
        for chunk in structural_chunks:
            if len(chunk.page_content) > self.config.CHUNK_SIZE * 2:
                # Large chunk - apply semantic chunking
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    semantic_subchunks = self.semantic_chunker.chunk_document(chunk)
                    final_chunks.extend(semantic_subchunks)
                else:
                    # Fallback to basic splitting
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=self.config.CHUNK_SIZE,
                        chunk_overlap=self.config.CHUNK_OVERLAP
                    )
                    subchunks = splitter.split_documents([chunk])
                    final_chunks.extend(subchunks)
            else:
                final_chunks.append(chunk)
        
        # Update metadata to indicate hybrid processing
        for i, chunk in enumerate(final_chunks):
            chunk.metadata.update({
                'chunk_index': i,
                'chunk_method': 'hybrid',
                'final_processing': True
            })
        
        return final_chunks


class SmartChunkingSystem:
    """Smart chunking system with multiple strategies"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        # Initialize chunking strategies
        self.strategies = {
            'semantic': SemanticChunker(self.config),
            'structural': StructuralChunker(self.config),
            'hybrid': HybridChunker(self.config)
        }
        
        self.default_strategy = 'hybrid'
        
        # Chunking statistics
        self.stats = {
            'total_documents_chunked': 0,
            'total_chunks_created': 0,
            'strategy_usage': {strategy: 0 for strategy in self.strategies.keys()}
        }
        
        logger.info(f"Smart chunking system initialized with {len(self.strategies)} strategies")
    
    def chunk_documents(self, documents: List[Document], 
                       strategy: Optional[str] = None) -> List[Document]:
        """Chunk multiple documents using specified or auto-selected strategy"""
        if not documents:
            return []
        
        strategy = strategy or self.default_strategy
        if strategy not in self.strategies:
            logger.warning(f"Unknown strategy '{strategy}', using default '{self.default_strategy}'")
            strategy = self.default_strategy
        
        chunker = self.strategies[strategy]
        all_chunks = []
        
        logger.info(f"Chunking {len(documents)} documents using '{strategy}' strategy")
        
        for doc_idx, document in enumerate(documents):
            try:
                chunks = chunker.chunk_document(document)
                
                # Add document-level metadata to chunks
                for chunk_idx, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        'parent_document_index': doc_idx,
                        'global_chunk_index': len(all_chunks) + chunk_idx,
                        'chunking_strategy': strategy
                    })
                
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Failed to chunk document {doc_idx}: {e}")
                # Fallback: use the original document as a single chunk
                document.metadata.update({
                    'chunk_index': 0,
                    'chunk_type': 'fallback_whole_document',
                    'chunking_error': str(e)
                })
                all_chunks.append(document)
        
        # Update statistics
        self.stats['total_documents_chunked'] += len(documents)
        self.stats['total_chunks_created'] += len(all_chunks)
        self.stats['strategy_usage'][strategy] += len(documents)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        
        return all_chunks
    
    def get_optimal_strategy(self, document: Document) -> str:
        """Determine optimal chunking strategy for a document"""
        # This could be enhanced with ML-based strategy selection
        content = document.page_content
        metadata = document.metadata
        
        # Simple heuristics for now
        if metadata.get('code_blocks_count', 0) > 5:
            return 'structural'
        elif metadata.get('total_technical_terms', 0) > 20:
            return 'semantic' if SENTENCE_TRANSFORMERS_AVAILABLE else 'hybrid'
        else:
            return 'hybrid'
    
    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get chunking statistics"""
        total_docs = self.stats['total_documents_chunked']
        avg_chunks_per_doc = self.stats['total_chunks_created'] / max(total_docs, 1)
        
        return {
            'total_documents_chunked': total_docs,
            'total_chunks_created': self.stats['total_chunks_created'],
            'average_chunks_per_document': round(avg_chunks_per_doc, 2),
            'strategy_usage': self.stats['strategy_usage'].copy(),
            'available_strategies': list(self.strategies.keys()),
            'semantic_chunking_available': SENTENCE_TRANSFORMERS_AVAILABLE
        }


# Factory function
def create_smart_chunking_system(config: Optional[Config] = None) -> SmartChunkingSystem:
    """Create smart chunking system"""
    return SmartChunkingSystem(config)
