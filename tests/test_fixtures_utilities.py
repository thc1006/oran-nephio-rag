"""
TDD test fixtures and utilities
Comprehensive test utilities, factories, builders, and helper functions
"""

import os
import pytest
import tempfile
import shutil
import time
import json
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import contextmanager

from langchain.docstore.document import Document


@dataclass
class TestDataBuilder:
    """Builder pattern for test data creation"""
    _data: Dict[str, Any] = field(default_factory=dict)

    def with_field(self, key: str, value: Any) -> 'TestDataBuilder':
        """Add a field to the test data"""
        self._data[key] = value
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> 'TestDataBuilder':
        """Add metadata to the test data"""
        self._data.setdefault('metadata', {}).update(metadata)
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the test data"""
        return self._data.copy()


class DocumentFactory:
    """Factory for creating test documents"""

    @staticmethod
    def create_nephio_document(
        content: Optional[str] = None,
        source: Optional[str] = None,
        doc_type: str = "nephio",
        **metadata_overrides
    ) -> Document:
        """Create a Nephio-related test document"""
        default_content = """
        Nephio Network Function Management

        Nephio is a Kubernetes-based cloud native intent automation platform designed
        for telecom network management. The platform provides comprehensive automation
        capabilities for network function deployment, scaling, and lifecycle management.

        Key features include:
        - Intent-driven automation
        - Multi-cluster orchestration
        - GitOps workflows
        - Network function scaling
        - O-RAN integration support

        The platform enables service providers to manage complex network deployments
        at scale while maintaining operational efficiency and service reliability.
        """

        metadata = {
            "source": source or "https://docs.nephio.org/test-document",
            "source_type": doc_type,
            "title": "Test Nephio Document",
            "description": "Test document for Nephio functionality",
            "content_type": "technical_documentation",
            "last_updated": datetime.now().isoformat(),
            "priority": 1,
            "keywords": ["nephio", "kubernetes", "automation", "network"],
            "content_length": len(content or default_content),
            "test_document": True
        }
        metadata.update(metadata_overrides)

        return Document(
            page_content=content or default_content,
            metadata=metadata
        )

    @staticmethod
    def create_oran_document(
        content: Optional[str] = None,
        source: Optional[str] = None,
        **metadata_overrides
    ) -> Document:
        """Create an O-RAN-related test document"""
        default_content = """
        O-RAN Network Architecture and Integration

        O-RAN (Open Radio Access Network) provides open interfaces and architecture
        for RAN disaggregation, enabling multi-vendor interoperability and innovation
        in 5G networks.

        Core O-RAN components:
        - O-CU (O-RAN Central Unit): Centralized baseband processing
        - O-DU (O-RAN Distributed Unit): Distributed unit processing
        - O-RU (O-RAN Radio Unit): Radio frequency processing
        - O-Cloud: Cloud infrastructure for O-RAN functions

        Integration with Nephio enables automated deployment and scaling of O-RAN
        network functions through intent-driven orchestration and GitOps workflows.
        """

        metadata = {
            "source": source or "https://docs.nephio.org/o-ran-test",
            "source_type": "nephio",
            "title": "Test O-RAN Document",
            "description": "Test document for O-RAN integration",
            "content_type": "integration_guide",
            "last_updated": datetime.now().isoformat(),
            "priority": 2,
            "keywords": ["o-ran", "o-cu", "o-du", "o-ru", "integration"],
            "content_length": len(content or default_content),
            "test_document": True
        }
        metadata.update(metadata_overrides)

        return Document(
            page_content=content or default_content,
            metadata=metadata
        )

    @staticmethod
    def create_scaling_document(
        content: Optional[str] = None,
        source: Optional[str] = None,
        **metadata_overrides
    ) -> Document:
        """Create a scaling-related test document"""
        default_content = """
        Network Function Scaling Strategies

        Nephio supports comprehensive scaling strategies for network functions:

        Horizontal Scaling (Scale-out):
        - Increase the number of NF instances
        - Distribute load across multiple instances
        - Use ProvisioningRequest CRDs for automation
        - Geographic distribution across edge clusters

        Vertical Scaling (Scale-up):
        - Increase resources per instance
        - CPU, memory, and storage adjustments
        - Suitable for resource-intensive workloads

        Advanced Features:
        - Predictive scaling based on traffic patterns
        - Policy-based scaling with custom metrics
        - Multi-cluster coordination for disaster recovery
        - Integration with Kubernetes HPA

        Implementation involves creating appropriate CRDs, configuring scaling policies,
        and monitoring performance metrics for automated decision making.
        """

        metadata = {
            "source": source or "https://docs.nephio.org/scaling-test",
            "source_type": "nephio",
            "title": "Test Scaling Document",
            "description": "Test document for scaling procedures",
            "content_type": "operational_guide",
            "last_updated": datetime.now().isoformat(),
            "priority": 2,
            "keywords": ["scaling", "horizontal", "vertical", "provisioningrequest"],
            "content_length": len(content or default_content),
            "test_document": True
        }
        metadata.update(metadata_overrides)

        return Document(
            page_content=content or default_content,
            metadata=metadata
        )

    @staticmethod
    def create_document_batch(
        count: int = 5,
        doc_types: Optional[List[str]] = None
    ) -> List[Document]:
        """Create a batch of test documents"""
        if not doc_types:
            doc_types = ["nephio", "oran", "scaling"]

        documents = []
        for i in range(count):
            doc_type = doc_types[i % len(doc_types)]

            if doc_type == "nephio":
                doc = DocumentFactory.create_nephio_document(
                    source=f"https://docs.nephio.org/test-{i}",
                    title=f"Test Nephio Document {i}"
                )
            elif doc_type == "oran":
                doc = DocumentFactory.create_oran_document(
                    source=f"https://docs.nephio.org/oran-test-{i}",
                    title=f"Test O-RAN Document {i}"
                )
            else:  # scaling
                doc = DocumentFactory.create_scaling_document(
                    source=f"https://docs.nephio.org/scaling-test-{i}",
                    title=f"Test Scaling Document {i}"
                )

            documents.append(doc)

        return documents


class MockRAGSystemBuilder:
    """Builder for creating mock RAG systems with specific behaviors"""

    def __init__(self):
        self.mock_system = MagicMock()
        self.mock_system.is_ready = True
        self._query_responses = {}
        self._default_response = None

    def with_query_response(self, query_pattern: str, response: Dict[str, Any]) -> 'MockRAGSystemBuilder':
        """Add a specific response for queries matching a pattern"""
        self._query_responses[query_pattern.lower()] = response
        return self

    def with_default_response(self, response: Dict[str, Any]) -> 'MockRAGSystemBuilder':
        """Set default response for unmatched queries"""
        self._default_response = response
        return self

    def with_ready_state(self, is_ready: bool) -> 'MockRAGSystemBuilder':
        """Set the ready state of the mock system"""
        self.mock_system.is_ready = is_ready
        return self

    def with_system_status(self, status: Dict[str, Any]) -> 'MockRAGSystemBuilder':
        """Set the system status response"""
        self.mock_system.get_system_status.return_value = status
        return self

    def build(self) -> MagicMock:
        """Build and return the mock RAG system"""
        def query_side_effect(question, **kwargs):
            question_lower = question.lower()

            # Check for pattern matches
            for pattern, response in self._query_responses.items():
                if pattern in question_lower:
                    return response

            # Return default response or generate one
            if self._default_response:
                return self._default_response
            else:
                return {
                    "success": True,
                    "answer": f"Mock response for: {question}",
                    "sources": [
                        {
                            "content": "Mock source content",
                            "metadata": {"source": "mock", "type": "test"},
                            "similarity_score": 0.85
                        }
                    ],
                    "query_time": 1.0,
                    "context_used": 1
                }

        self.mock_system.query.side_effect = query_side_effect
        return self.mock_system


class TestEnvironmentManager:
    """Manager for creating and cleaning up test environments"""

    def __init__(self):
        self.temp_dirs = []
        self.created_files = []
        self.patches = []

    def create_temp_directory(self, prefix: str = "rag_test_") -> str:
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def create_test_file(self, directory: str, filename: str, content: str = "") -> str:
        """Create a test file"""
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.created_files.append(filepath)
        return filepath

    def add_patch(self, patch_object) -> None:
        """Add a patch to be managed"""
        self.patches.append(patch_object)

    def cleanup(self) -> None:
        """Clean up all created resources"""
        # Stop patches
        for patch_obj in self.patches:
            try:
                patch_obj.stop()
            except RuntimeError:
                pass  # Already stopped

        # Remove files
        for filepath in self.created_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass

        # Remove directories
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

        # Clear lists
        self.temp_dirs.clear()
        self.created_files.clear()
        self.patches.clear()


@contextmanager
def test_environment(prefix: str = "rag_test_"):
    """Context manager for test environment setup and cleanup"""
    env_manager = TestEnvironmentManager()
    try:
        yield env_manager
    finally:
        env_manager.cleanup()


class PerformanceTimer:
    """Utility for timing operations in tests"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def start(self) -> None:
        """Start timing"""
        self.start_time = time.time()

    def stop(self) -> float:
        """Stop timing and return elapsed time"""
        self.end_time = time.time()
        if self.start_time is not None:
            self.elapsed_time = self.end_time - self.start_time
        return self.elapsed_time or 0.0

    @contextmanager
    def measure(self):
        """Context manager for measuring execution time"""
        self.start()
        try:
            yield self
        finally:
            self.stop()

    def assert_under(self, max_seconds: float, message: str = "") -> None:
        """Assert that elapsed time is under threshold"""
        if self.elapsed_time is None:
            raise ValueError("Timer not stopped")

        assert self.elapsed_time < max_seconds, \
            f"{message} Elapsed time {self.elapsed_time:.3f}s exceeds {max_seconds}s"


class ResponseValidator:
    """Utility for validating RAG system responses"""

    @staticmethod
    def validate_basic_response(response: Dict[str, Any]) -> None:
        """Validate basic response structure"""
        required_fields = ["success", "answer"]
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"

        assert isinstance(response["success"], bool), "Success field must be boolean"
        assert isinstance(response["answer"], str), "Answer field must be string"

    @staticmethod
    def validate_successful_response(response: Dict[str, Any]) -> None:
        """Validate successful response structure"""
        ResponseValidator.validate_basic_response(response)

        assert response["success"] is True, "Response should be successful"
        assert len(response["answer"]) > 0, "Answer should not be empty"

        if "sources" in response:
            assert isinstance(response["sources"], list), "Sources must be a list"

        if "query_time" in response:
            assert isinstance(response["query_time"], (int, float)), "Query time must be numeric"
            assert response["query_time"] >= 0, "Query time must be non-negative"

    @staticmethod
    def validate_error_response(response: Dict[str, Any]) -> None:
        """Validate error response structure"""
        ResponseValidator.validate_basic_response(response)

        assert response["success"] is False, "Response should indicate failure"
        assert "error" in response, "Error response should include error field"

    @staticmethod
    def validate_sources(sources: List[Dict[str, Any]]) -> None:
        """Validate source structure"""
        for source in sources:
            required_fields = ["content", "metadata"]
            for field in required_fields:
                assert field in source, f"Source missing required field: {field}"

            assert isinstance(source["content"], str), "Source content must be string"
            assert isinstance(source["metadata"], dict), "Source metadata must be dict"

            if "similarity_score" in source:
                score = source["similarity_score"]
                assert isinstance(score, (int, float)), "Similarity score must be numeric"
                assert 0.0 <= score <= 1.0, "Similarity score must be between 0 and 1"


class TestAssertions:
    """Custom assertions for RAG system testing"""

    @staticmethod
    def assert_contains_keywords(text: str, keywords: List[str], min_count: int = 1) -> None:
        """Assert that text contains specified keywords"""
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in text_lower]

        assert len(found_keywords) >= min_count, \
            f"Expected at least {min_count} keywords from {keywords}, found: {found_keywords}"

    @staticmethod
    def assert_response_quality(response: Dict[str, Any], min_length: int = 50) -> None:
        """Assert response meets quality criteria"""
        ResponseValidator.validate_successful_response(response)

        answer = response["answer"]
        assert len(answer) >= min_length, f"Response too short: {len(answer)} < {min_length}"

        # Check for coherent sentences
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        assert len(sentences) >= 2, "Response should contain multiple sentences"

    @staticmethod
    def assert_performance_within_bounds(
        elapsed_time: float,
        max_time: float,
        operation: str = "operation"
    ) -> None:
        """Assert operation completed within time bounds"""
        assert elapsed_time <= max_time, \
            f"{operation} took {elapsed_time:.3f}s, exceeding limit of {max_time}s"

    @staticmethod
    def assert_memory_usage_reasonable(
        initial_memory: float,
        final_memory: float,
        max_increase_mb: float = 100
    ) -> None:
        """Assert memory usage increase is reasonable"""
        memory_increase = final_memory - initial_memory
        assert memory_increase <= max_increase_mb, \
            f"Memory increase {memory_increase:.1f}MB exceeds limit of {max_increase_mb}MB"


class TestFixtures:
    """Collection of reusable test fixtures"""

    @staticmethod
    @pytest.fixture
    def test_documents():
        """Fixture providing test documents"""
        return DocumentFactory.create_document_batch(count=10)

    @staticmethod
    @pytest.fixture
    def mock_rag_system():
        """Fixture providing a mock RAG system"""
        return (MockRAGSystemBuilder()
                .with_default_response({
                    "success": True,
                    "answer": "Test response from mock RAG system",
                    "sources": [],
                    "query_time": 1.0
                })
                .build())

    @staticmethod
    @pytest.fixture
    def performance_timer():
        """Fixture providing a performance timer"""
        return PerformanceTimer()

    @staticmethod
    @pytest.fixture
    def test_env():
        """Fixture providing a test environment manager"""
        with test_environment() as env:
            yield env


class TestUtilities:
    """General test utilities"""

    @staticmethod
    def generate_test_queries(count: int = 5, topic: str = "nephio") -> List[str]:
        """Generate test queries for a specific topic"""
        if topic == "nephio":
            base_queries = [
                "What is Nephio?",
                "How does Nephio work?",
                "Explain Nephio architecture",
                "What are Nephio core components?",
                "How to deploy network functions with Nephio?"
            ]
        elif topic == "oran":
            base_queries = [
                "What is O-RAN?",
                "How does O-RAN integrate with Nephio?",
                "Explain O-RAN components",
                "What is O-CU in O-RAN?",
                "How to scale O-RAN network functions?"
            ]
        elif topic == "scaling":
            base_queries = [
                "How to scale network functions?",
                "What is horizontal scaling?",
                "Explain vertical scaling procedures",
                "How to configure ProvisioningRequest?",
                "What are scaling best practices?"
            ]
        else:
            base_queries = [
                f"What is {topic}?",
                f"How does {topic} work?",
                f"Explain {topic} features",
                f"What are {topic} benefits?",
                f"How to use {topic}?"
            ]

        # Extend if more queries needed
        queries = base_queries * (count // len(base_queries) + 1)
        return queries[:count]

    @staticmethod
    def create_test_config(temp_dir: str) -> Dict[str, Any]:
        """Create test configuration"""
        return {
            "VECTOR_DB_PATH": os.path.join(temp_dir, "test_vectordb"),
            "EMBEDDINGS_CACHE_PATH": os.path.join(temp_dir, "test_embeddings"),
            "LOG_FILE": os.path.join(temp_dir, "test.log"),
            "CHUNK_SIZE": 256,
            "CHUNK_OVERLAP": 50,
            "RETRIEVER_K": 3,
            "REQUEST_TIMEOUT": 5,
            "MAX_RETRIES": 1
        }

    @staticmethod
    def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout_seconds: float = 10.0,
        check_interval: float = 0.1
    ) -> bool:
        """Wait for a condition to become true"""
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            if condition_func():
                return True
            time.sleep(check_interval)

        return False

    @staticmethod
    def capture_logs(logger_name: str = "src.oran_nephio_rag"):
        """Context manager to capture log messages"""
        import logging
        from io import StringIO

        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)

        try:
            yield log_capture
        finally:
            logger.removeHandler(handler)


class TestCaseGenerator:
    """Generator for creating test cases"""

    @staticmethod
    def generate_query_test_cases(scenarios: List[str]) -> List[Dict[str, Any]]:
        """Generate test cases for different query scenarios"""
        test_cases = []

        for scenario in scenarios:
            if scenario == "simple":
                test_cases.append({
                    "query": "What is Nephio?",
                    "expected_keywords": ["nephio", "kubernetes", "platform"],
                    "min_length": 50,
                    "complexity": "low"
                })
            elif scenario == "complex":
                test_cases.append({
                    "query": "How do I configure horizontal scaling for O-DU components across multiple edge clusters with geographic distribution?",
                    "expected_keywords": ["scaling", "o-du", "clusters", "geographic"],
                    "min_length": 150,
                    "complexity": "high"
                })
            elif scenario == "integration":
                test_cases.append({
                    "query": "Explain the integration between Nephio and O-RAN SMO",
                    "expected_keywords": ["nephio", "o-ran", "smo", "integration"],
                    "min_length": 100,
                    "complexity": "medium"
                })

        return test_cases

    @staticmethod
    def generate_performance_test_cases() -> List[Dict[str, Any]]:
        """Generate performance test cases"""
        return [
            {
                "name": "single_query_performance",
                "query": "Test performance query",
                "max_response_time": 2.0,
                "expected_success": True
            },
            {
                "name": "batch_query_performance",
                "queries": ["Query 1", "Query 2", "Query 3"],
                "max_total_time": 5.0,
                "expected_success_rate": 1.0
            },
            {
                "name": "concurrent_query_performance",
                "concurrent_queries": 5,
                "max_response_time": 3.0,
                "expected_success_rate": 0.95
            }
        ]


if __name__ == "__main__":
    # Example usage
    with test_environment() as env:
        temp_dir = env.create_temp_directory()
        print(f"Created test directory: {temp_dir}")

        # Create test documents
        docs = DocumentFactory.create_document_batch(3)
        print(f"Created {len(docs)} test documents")

        # Build mock RAG system
        mock_rag = (MockRAGSystemBuilder()
                   .with_query_response("nephio", {"success": True, "answer": "Nephio response"})
                   .build())

        # Test query
        result = mock_rag.query("What is Nephio?")
        print(f"Mock response: {result['answer']}")

    print("Test environment cleaned up automatically")