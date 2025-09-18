"""
Enhanced LLM Integration for O-RAN × Nephio RAG
Advanced answer generation with context optimization and prompt engineering
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

from langchain.docstore.document import Document

# Import configuration and components
try:
    from .config import Config
    from .puter_integration import PuterRAGManager, create_puter_rag_manager
    from .retrieval_engine import RetrievalResult, QueryType
except ImportError:
    from config import Config
    from puter_integration import PuterRAGManager, create_puter_rag_manager
    from retrieval_engine import RetrievalResult, QueryType

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses for different query contexts"""
    TECHNICAL_EXPLANATION = "technical_explanation"
    CODE_EXAMPLE = "code_example"
    STEP_BY_STEP = "step_by_step"
    ARCHITECTURE_OVERVIEW = "architecture_overview"
    TROUBLESHOOTING = "troubleshooting"
    COMPARISON = "comparison"
    QUICK_ANSWER = "quick_answer"


@dataclass
class LLMMetrics:
    """Metrics for LLM operations"""
    total_queries: int = 0
    total_generation_time: float = 0.0
    average_generation_time: float = 0.0
    total_tokens_generated: int = 0
    average_tokens_per_response: float = 0.0
    context_optimization_time: float = 0.0
    prompt_template_usage: Dict[str, int] = None
    response_type_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.prompt_template_usage is None:
            self.prompt_template_usage = {}
        if self.response_type_distribution is None:
            self.response_type_distribution = {}


class PromptTemplateManager:
    """Manages prompt templates for different query types and contexts"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.usage_stats = {template: 0 for template in self.templates.keys()}
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize prompt templates for different scenarios"""
        return {
            'technical_explanation': """
You are an expert in O-RAN and Nephio technologies. Based on the provided context, please provide a comprehensive technical explanation.

Context Information:
{context}

User Question: {question}

Please provide a detailed technical explanation that:
1. Directly addresses the user's question
2. Uses the provided context as the primary source
3. Explains technical concepts clearly
4. Includes relevant technical details and specifications
5. Mentions specific O-RAN or Nephio components when applicable

Response:""",
            
            'code_example': """
You are an expert in O-RAN and Nephio development. Based on the provided context, please provide practical code examples and implementation guidance.

Context Information:
{context}

User Question: {question}

Please provide a response that:
1. Includes relevant code examples from the context
2. Explains how to implement or use the code
3. Provides step-by-step instructions if applicable
4. Mentions configuration requirements
5. Includes best practices and common pitfalls to avoid

Response:""",
            
            'step_by_step': """
You are an expert guide for O-RAN and Nephio implementations. Based on the provided context, please provide clear step-by-step instructions.

Context Information:
{context}

User Question: {question}

Please provide a structured response with:
1. Clear, numbered steps
2. Prerequisites and requirements
3. Commands or configurations needed
4. Expected outcomes for each step
5. Troubleshooting tips for common issues

Response:""",
            
            'architecture_overview': """
You are an expert architect specializing in O-RAN and Nephio systems. Based on the provided context, please provide a comprehensive architectural overview.

Context Information:
{context}

User Question: {question}

Please provide an architectural response that:
1. Describes the high-level architecture and components
2. Explains how components interact
3. Discusses design patterns and principles
4. Covers scalability and deployment considerations
5. References relevant diagrams or specifications from the context

Response:""",
            
            'troubleshooting': """
You are an expert troubleshooter for O-RAN and Nephio systems. Based on the provided context, please help diagnose and resolve the issue.

Context Information:
{context}

User Question: {question}

Please provide a troubleshooting response that:
1. Identifies possible root causes
2. Provides diagnostic steps to isolate the issue
3. Offers specific solutions with commands/configurations
4. Explains how to verify the fix
5. Suggests preventive measures

Response:""",
            
            'comparison': """
You are an expert analyst of O-RAN and Nephio technologies. Based on the provided context, please provide a detailed comparison.

Context Information:
{context}

User Question: {question}

Please provide a comparative analysis that:
1. Clearly outlines the differences and similarities
2. Discusses advantages and disadvantages of each option
3. Provides use case scenarios for each approach
4. Includes performance and operational considerations
5. Offers recommendations based on specific requirements

Response:""",
            
            'quick_answer': """
You are an expert in O-RAN and Nephio technologies. Based on the provided context, please provide a concise but complete answer.

Context Information:
{context}

User Question: {question}

Please provide a brief but comprehensive answer that:
1. Directly answers the question
2. Uses information from the context
3. Is clear and to the point
4. Includes key technical details
5. Suggests where to find more detailed information if needed

Response:"""
        }
    
    def get_template(self, response_type: ResponseType, 
                    query_type: QueryType = None) -> str:
        """Get appropriate template based on response and query types"""
        # Map response types to templates
        template_mapping = {
            ResponseType.TECHNICAL_EXPLANATION: 'technical_explanation',
            ResponseType.CODE_EXAMPLE: 'code_example',
            ResponseType.STEP_BY_STEP: 'step_by_step',
            ResponseType.ARCHITECTURE_OVERVIEW: 'architecture_overview',
            ResponseType.TROUBLESHOOTING: 'troubleshooting',
            ResponseType.COMPARISON: 'comparison',
            ResponseType.QUICK_ANSWER: 'quick_answer'
        }
        
        template_name = template_mapping.get(response_type, 'technical_explanation')
        
        # Update usage stats
        self.usage_stats[template_name] += 1
        
        return self.templates[template_name]
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get template usage statistics"""
        return self.usage_stats.copy()


class ContextOptimizer:
    """Optimizes context for LLM input to maximize relevance and fit within token limits"""
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
    
    def optimize_context(self, documents: List[Document], 
                        scores: List[float],
                        query: str,
                        query_analysis: Dict[str, Any]) -> str:
        """Optimize context from retrieved documents"""
        if not documents:
            return ""
        
        # Sort documents by relevance score
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Extract and optimize content
        optimized_sections = []
        current_length = 0
        
        for doc, score in doc_score_pairs:
            # Extract key information from document
            section = self._extract_key_section(doc, query, query_analysis)
            section_length = len(section)
            
            # Check if we can fit this section
            if current_length + section_length <= self.max_context_length:
                optimized_sections.append({
                    'content': section,
                    'score': score,
                    'source': doc.metadata.get('source_url', 'unknown'),
                    'title': doc.metadata.get('title', 'Untitled')
                })
                current_length += section_length
            else:
                # Try to fit a truncated version
                remaining_space = self.max_context_length - current_length
                if remaining_space > 200:  # Only if we have reasonable space
                    truncated = section[:remaining_space-50] + "..."
                    optimized_sections.append({
                        'content': truncated,
                        'score': score,
                        'source': doc.metadata.get('source_url', 'unknown'),
                        'title': doc.metadata.get('title', 'Untitled')
                    })
                break
        
        # Format optimized context
        context_parts = []
        for i, section in enumerate(optimized_sections, 1):
            title = section['title']
            content = section['content']
            source = section['source']
            
            context_parts.append(f"""Document {i}: {title}
Source: {source}
Content: {content}
""")
        
        return "\n\n".join(context_parts)
    
    def _extract_key_section(self, document: Document, 
                           query: str, 
                           query_analysis: Dict[str, Any]) -> str:
        """Extract the most relevant section from a document"""
        content = document.page_content
        
        # For shorter documents, return as-is
        if len(content) <= 500:
            return content
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if len(paragraphs) <= 3:
            return content
        
        # Score paragraphs based on query relevance
        query_terms = set(query.lower().split())
        domain_terms = set()
        for terms_list in query_analysis.get('domain_terms', {}).values():
            domain_terms.update(terms_list)
        
        scored_paragraphs = []
        for para in paragraphs:
            para_lower = para.lower()
            
            # Score based on query term matches
            query_matches = sum(1 for term in query_terms if term in para_lower)
            domain_matches = sum(1 for term in domain_terms if term in para_lower)
            
            # Prefer paragraphs with code blocks for code-related queries
            code_bonus = 0
            if query_analysis.get('query_type') == QueryType.CODE_RELATED:
                if any(marker in para for marker in ['```', 'kubectl', 'yaml', 'apiVersion']):
                    code_bonus = 5
            
            score = query_matches * 2 + domain_matches * 3 + code_bonus
            scored_paragraphs.append((para, score))
        
        # Sort by score and select top paragraphs
        scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
        
        # Select paragraphs until we reach a reasonable length
        selected_paras = []
        total_length = 0
        
        for para, score in scored_paragraphs:
            if total_length + len(para) <= 800:  # Target length per document
                selected_paras.append(para)
                total_length += len(para)
            else:
                break
        
        # If we didn't select enough content, add more
        if total_length < 300 and len(selected_paras) < len(paragraphs):
            remaining_paras = [p for p, s in scored_paragraphs if p not in selected_paras]
            for para in remaining_paras[:2]:  # Add up to 2 more paragraphs
                if total_length + len(para) <= 1000:
                    selected_paras.append(para)
                    total_length += len(para)
        
        return '\n\n'.join(selected_paras)


class ResponseTypeClassifier:
    """Classifies queries to determine the best response type"""
    
    def __init__(self):
        self.classification_rules = {
            ResponseType.CODE_EXAMPLE: [
                r'\b(example|code|implementation|snippet|script)\b',
                r'\b(kubectl|yaml|configuration|manifest)\b',
                r'\b(how to implement|show me|give me an example)\b'
            ],
            ResponseType.STEP_BY_STEP: [
                r'\b(how to|step|guide|tutorial|process|procedure)\b',
                r'\b(install|setup|configure|deploy)\b',
                r'\b(walkthrough|instructions)\b'
            ],
            ResponseType.ARCHITECTURE_OVERVIEW: [
                r'\b(architecture|design|overview|structure)\b',
                r'\b(components|modules|diagram|topology)\b',
                r'\b(high-level|system design)\b'
            ],
            ResponseType.TROUBLESHOOTING: [
                r'\b(error|issue|problem|debug|troubleshoot|fix)\b',
                r'\b(not working|broken|failed|crash)\b',
                r'\b(diagnose|resolve|solution)\b'
            ],
            ResponseType.COMPARISON: [
                r'\b(vs|versus|compare|comparison|difference)\b',
                r'\b(better|alternative|option|choice)\b',
                r'\b(pros|cons|advantage|disadvantage)\b'
            ]
        }
    
    def classify(self, query: str, query_type: QueryType = None) -> ResponseType:
        """Classify query to determine appropriate response type"""
        query_lower = query.lower()
        
        # Score each response type
        scores = {}
        for response_type, patterns in self.classification_rules.items():
            score = 0
            for pattern in patterns:
                import re
                matches = len(re.findall(pattern, query_lower))
                score += matches
            scores[response_type] = score
        
        # Get the highest scoring response type
        best_response_type = max(scores.items(), key=lambda x: x[1])
        
        # If no clear winner, use query type to determine response type
        if best_response_type[1] == 0:
            if query_type == QueryType.CODE_RELATED:
                return ResponseType.CODE_EXAMPLE
            elif query_type == QueryType.ARCHITECTURE:
                return ResponseType.ARCHITECTURE_OVERVIEW
            elif query_type == QueryType.TROUBLESHOOTING:
                return ResponseType.TROUBLESHOOTING
            elif query_type == QueryType.HOW_TO:
                return ResponseType.STEP_BY_STEP
            elif query_type == QueryType.COMPARISON:
                return ResponseType.COMPARISON
            else:
                return ResponseType.TECHNICAL_EXPLANATION
        
        # For short queries, prefer quick answers
        if len(query.split()) <= 5:
            return ResponseType.QUICK_ANSWER
        
        return best_response_type[0]


class EnhancedLLMManager:
    """Enhanced LLM manager with advanced prompt engineering and context optimization"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        # Initialize components
        self.puter_manager = create_puter_rag_manager(
            model=self.config.PUTER_MODEL,
            headless=self.config.BROWSER_HEADLESS
        )
        
        self.prompt_manager = PromptTemplateManager()
        self.context_optimizer = ContextOptimizer(
            max_context_length=int(self.config.MAX_TOKENS * 0.6)  # Reserve space for response
        )
        self.response_classifier = ResponseTypeClassifier()
        
        # Metrics
        self.metrics = LLMMetrics()
        
        logger.info("Enhanced LLM manager initialized")
    
    def generate_answer(self, query: str, 
                       retrieval_result: RetrievalResult,
                       response_type: Optional[ResponseType] = None,
                       stream: bool = False) -> Dict[str, Any]:
        """Generate enhanced answer using optimized context and prompts"""
        start_time = time.time()
        
        try:
            # Determine response type if not provided
            if response_type is None:
                response_type = self.response_classifier.classify(
                    query, retrieval_result.query_type
                )
            
            # Optimize context
            context_start = time.time()
            optimized_context = self.context_optimizer.optimize_context(
                retrieval_result.documents,
                retrieval_result.scores,
                query,
                retrieval_result.metadata.get('query_analysis', {})
            )
            context_time = time.time() - context_start
            
            # Get appropriate prompt template
            template = self.prompt_manager.get_template(
                response_type, retrieval_result.query_type
            )
            
            # Format the prompt
            formatted_prompt = template.format(
                context=optimized_context,
                question=query
            )
            
            # Generate response using Puter.js
            generation_start = time.time()
            llm_result = self.puter_manager.query(
                prompt=formatted_prompt,
                context=optimized_context,
                stream=stream
            )
            generation_time = time.time() - generation_start
            
            # Update metrics
            self._update_metrics(generation_time, context_time, response_type, llm_result)
            
            # Prepare final result
            total_time = time.time() - start_time
            
            final_result = {
                'answer': llm_result.get('answer', 'Sorry, I could not generate an answer.'),
                'success': llm_result.get('success', False),
                'response_type': response_type.value,
                'context_length': len(optimized_context),
                'documents_used': len(retrieval_result.documents),
                'generation_time': round(generation_time, 3),
                'context_optimization_time': round(context_time, 3),
                'total_time': round(total_time, 3),
                'template_used': self.prompt_manager.get_template(response_type, retrieval_result.query_type),
                'model_info': {
                    'model': self.config.PUTER_MODEL,
                    'integration_method': 'puter_js_browser',
                    'constraint_compliant': True
                },
                'metadata': {
                    'retrieval_metadata': retrieval_result.metadata,
                    'llm_metadata': llm_result
                }
            }
            
            if not llm_result.get('success'):
                final_result['error'] = llm_result.get('error', 'Unknown LLM error')
            
            return final_result
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return {
                'answer': f'Sorry, an error occurred while generating the answer: {str(e)}',
                'success': False,
                'error': str(e),
                'response_type': response_type.value if response_type else 'unknown',
                'generation_time': time.time() - start_time
            }
    
    def _update_metrics(self, generation_time: float, context_time: float, 
                       response_type: ResponseType, llm_result: Dict[str, Any]) -> None:
        """Update LLM metrics"""
        self.metrics.total_queries += 1
        self.metrics.total_generation_time += generation_time
        self.metrics.average_generation_time = (
            self.metrics.total_generation_time / self.metrics.total_queries
        )
        self.metrics.context_optimization_time += context_time
        
        # Estimate tokens (rough approximation)
        answer = llm_result.get('answer', '')
        estimated_tokens = len(answer.split()) * 1.3  # Rough token estimation
        self.metrics.total_tokens_generated += estimated_tokens
        self.metrics.average_tokens_per_response = (
            self.metrics.total_tokens_generated / self.metrics.total_queries
        )
        
        # Update response type distribution
        if response_type.value not in self.metrics.response_type_distribution:
            self.metrics.response_type_distribution[response_type.value] = 0
        self.metrics.response_type_distribution[response_type.value] += 1
    
    def get_llm_metrics(self) -> Dict[str, Any]:
        """Get LLM manager metrics"""
        return {
            'total_queries': self.metrics.total_queries,
            'total_generation_time': round(self.metrics.total_generation_time, 3),
            'average_generation_time': round(self.metrics.average_generation_time, 3),
            'total_tokens_generated': int(self.metrics.total_tokens_generated),
            'average_tokens_per_response': round(self.metrics.average_tokens_per_response, 1),
            'context_optimization_time': round(self.metrics.context_optimization_time, 3),
            'template_usage': self.prompt_manager.get_usage_stats(),
            'response_type_distribution': self.metrics.response_type_distribution.copy(),
            'model_info': {
                'model': self.config.PUTER_MODEL,
                'integration_method': 'puter_js_browser',
                'constraint_compliant': True
            }
        }
    
    def benchmark_generation(self, test_queries: List[str], 
                           mock_retrieval_results: List[RetrievalResult]) -> Dict[str, Any]:
        """Benchmark answer generation performance"""
        start_time = time.time()
        generation_times = []
        success_count = 0
        
        for query, retrieval_result in zip(test_queries, mock_retrieval_results):
            result = self.generate_answer(query, retrieval_result)
            generation_times.append(result.get('generation_time', 0))
            if result.get('success'):
                success_count += 1
        
        total_time = time.time() - start_time
        
        return {
            'total_queries': len(test_queries),
            'successful_generations': success_count,
            'success_rate': round((success_count / len(test_queries)) * 100, 2),
            'total_time': round(total_time, 3),
            'average_generation_time': round(sum(generation_times) / len(generation_times), 3),
            'fastest_generation': round(min(generation_times), 3),
            'slowest_generation': round(max(generation_times), 3),
            'generations_per_second': round(len(test_queries) / total_time, 2)
        }


# Factory function
def create_enhanced_llm_manager(config: Optional[Config] = None) -> EnhancedLLMManager:
    """Create enhanced LLM manager"""
    return EnhancedLLMManager(config)
