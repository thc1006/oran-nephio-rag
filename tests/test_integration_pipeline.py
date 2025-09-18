"""
Integration tests for document processing pipeline
Testing end-to-end document loading, processing, and vector database creation
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
from typing import List, Dict, Any

import responses
from langchain.docstore.document import Document


class TestDocumentProcessingPipeline:
    """Integration tests for complete document processing pipeline"""

    @pytest.fixture
    def temp_test_dir(self):
        """Create temporary directory for integration tests"""
        temp_dir = tempfile.mkdtemp(prefix="rag_integration_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def integration_config(self, temp_test_dir):
        """Configuration for integration testing"""
        from src.config import Config

        # Override paths for testing
        config = Config()
        config.VECTOR_DB_PATH = os.path.join(temp_test_dir, "vectordb")
        config.EMBEDDINGS_CACHE_PATH = os.path.join(temp_test_dir, "embeddings")
        config.LOG_FILE = os.path.join(temp_test_dir, "test.log")
        config.CHUNK_SIZE = 256  # Smaller chunks for testing
        config.CHUNK_OVERLAP = 50
        config.MIN_CONTENT_LENGTH = 50  # Lower threshold for testing
        config.MIN_EXTRACTED_CONTENT_LENGTH = 25
        config.REQUEST_TIMEOUT = 5
        config.MAX_RETRIES = 2

        return config

    @pytest.fixture
    def mock_document_sources(self):
        """Mock document sources for testing"""
        from src.config import DocumentSource

        return [
            DocumentSource(
                url="https://docs.nephio.org/architecture",
                source_type="nephio",
                description="Nephio Architecture Guide",
                priority=1,
                enabled=True
            ),
            DocumentSource(
                url="https://docs.nephio.org/o-ran-integration",
                source_type="nephio",
                description="O-RAN Integration Guide",
                priority=2,
                enabled=True
            ),
            DocumentSource(
                url="https://docs.nephio.org/scaling",
                source_type="nephio",
                description="Network Function Scaling Guide",
                priority=2,
                enabled=True
            )
        ]

    @pytest.fixture
    def mock_html_responses(self):
        """Mock HTML responses for document sources"""
        return {
            "https://docs.nephio.org/architecture": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nephio Architecture Overview</title>
                <meta name="description" content="Comprehensive Nephio architecture guide">
            </head>
            <body>
                <main class="content">
                    <h1>Nephio Architecture</h1>
                    <p>Nephio is a Kubernetes-based cloud native intent automation platform designed for telecom network management and orchestration.</p>

                    <h2>Core Components</h2>
                    <p>The Nephio architecture consists of several key components that work together to provide intent-driven automation:</p>
                    <ul>
                        <li>Porch (Package Orchestration) - Manages configuration packages and GitOps workflows</li>
                        <li>Nephio Controllers - Automation controllers for network function lifecycle management</li>
                        <li>Resource Backend - Inventory and topology management system</li>
                        <li>WebUI - User interface for system management and monitoring</li>
                    </ul>

                    <h2>Scaling Architecture</h2>
                    <p>Nephio supports both horizontal and vertical scaling of network functions across multiple clusters and edge locations.</p>
                    <p>The platform uses Kubernetes operators and custom resource definitions (CRDs) to manage the lifecycle of network functions.</p>
                </main>
            </body>
            </html>
            """,
            "https://docs.nephio.org/o-ran-integration": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>O-RAN Integration with Nephio</title>
            </head>
            <body>
                <article>
                    <h1>O-RAN Network Function Integration</h1>
                    <p>This comprehensive guide covers the integration of O-RAN network functions with Nephio for automated deployment, scaling, and lifecycle management.</p>

                    <section>
                        <h2>O-RAN Components</h2>
                        <p>The O-RAN architecture includes several disaggregated components:</p>
                        <ul>
                            <li>O-CU (O-RAN Central Unit) - Centralized baseband processing functions</li>
                            <li>O-DU (O-RAN Distributed Unit) - Distributed unit processing with real-time requirements</li>
                            <li>O-RU (O-RAN Radio Unit) - Radio frequency processing and antenna interface</li>
                            <li>O-Cloud - Cloud infrastructure for hosting O-RAN functions</li>
                        </ul>
                    </section>

                    <section>
                        <h2>Scale-out Procedures</h2>
                        <p>To scale out O-RAN network functions using Nephio:</p>
                        <ol>
                            <li>Create a ProvisioningRequest CRD with the desired replica count and geographic distribution</li>
                            <li>Specify target cluster locations and resource requirements for each O-RAN component</li>
                            <li>Apply scaling policies based on traffic patterns and performance metrics</li>
                            <li>Monitor deployment status and validate network function connectivity</li>
                        </ol>
                        <p>Example configuration:</p>
                        <code>kubectl apply -f o-ran-scaling-config.yaml</code>
                    </section>

                    <section>
                        <h2>Integration with SMO</h2>
                        <p>Nephio integrates with the Service Management and Orchestration (SMO) framework to provide end-to-end management of O-RAN networks.</p>
                        <p>This integration enables automated policy enforcement, performance monitoring, and dynamic scaling based on network conditions.</p>
                    </section>
                </article>
            </body>
            </html>
            """,
            "https://docs.nephio.org/scaling": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Network Function Scaling with Nephio</title>
            </head>
            <body>
                <div class="main-content">
                    <h1>Network Function Scaling Guide</h1>
                    <p>Nephio provides comprehensive scaling capabilities for network functions, supporting both horizontal and vertical scaling strategies optimized for telecom workloads.</p>

                    <h2>Horizontal Scaling (Scale-out)</h2>
                    <p>Horizontal scaling increases the number of network function instances across multiple clusters:</p>
                    <ul>
                        <li>Replica-based scaling: Increase NF instances across edge clusters</li>
                        <li>Geographic distribution: Deploy instances closer to users for reduced latency</li>
                        <li>Load balancing: Distribute traffic across multiple NF instances</li>
                        <li>Stateless NF optimization: Design network functions for horizontal scaling</li>
                    </ul>

                    <h2>Vertical Scaling (Scale-up)</h2>
                    <p>Vertical scaling adjusts resources for existing network function instances:</p>
                    <ul>
                        <li>CPU and memory adjustment: Increase processing power for individual instances</li>
                        <li>Storage scaling: Expand storage capacity for stateful network functions</li>
                        <li>Performance optimization: Fine-tune resources based on workload characteristics</li>
                        <li>Cost optimization: Right-size resources to balance performance and cost</li>
                    </ul>

                    <h2>Advanced Scaling Features</h2>
                    <p>Nephio supports advanced scaling capabilities:</p>
                    <ol>
                        <li>Predictive Scaling - ML-based traffic prediction for proactive resource provisioning</li>
                        <li>Policy-based Scaling - Rule-based scaling triggers with custom metrics support</li>
                        <li>Multi-cluster Scaling - Cross-cluster load balancing and disaster recovery</li>
                        <li>Intent-driven Automation - Declarative scaling policies with automated execution</li>
                    </ol>

                    <h2>Best Practices</h2>
                    <p>Follow these best practices for effective network function scaling:</p>
                    <ul>
                        <li>Monitor key performance indicators (KPIs) and quality of service (QoS) metrics</li>
                        <li>Test scaling scenarios regularly in non-production environments</li>
                        <li>Implement proper resource limits and quotas to prevent resource exhaustion</li>
                        <li>Use automation for scaling decisions to reduce operational overhead</li>
                        <li>Consider geographic and latency requirements when scaling across regions</li>
                    </ul>
                </div>
            </body>
            </html>
            """
        }

    @responses.activate
    def test_complete_document_loading_pipeline(self, integration_config, mock_document_sources, mock_html_responses):
        """Test complete document loading pipeline with real HTTP responses"""
        from src.document_loader import DocumentLoader

        # Setup HTTP responses
        for url, html_content in mock_html_responses.items():
            responses.add(
                responses.GET,
                url,
                body=html_content,
                status=200,
                content_type="text/html; charset=utf-8"
            )

        # Create document loader
        loader = DocumentLoader(integration_config)

        # Load documents
        documents = loader.load_all_documents(mock_document_sources)

        # Assertions
        assert len(documents) == 3

        # Verify each document
        for doc in documents:
            assert isinstance(doc, Document)
            assert len(doc.page_content) > integration_config.MIN_EXTRACTED_CONTENT_LENGTH
            assert "source_url" in doc.metadata
            assert "source_type" in doc.metadata
            assert "content_length" in doc.metadata
            assert "title" in doc.metadata

        # Verify content extraction quality
        architecture_doc = next(d for d in documents if "architecture" in d.metadata["source_url"])
        assert "nephio" in architecture_doc.page_content.lower()
        assert "kubernetes" in architecture_doc.page_content.lower()
        assert "automation" in architecture_doc.page_content.lower()

        oran_doc = next(d for d in documents if "o-ran-integration" in d.metadata["source_url"])
        assert "o-ran" in oran_doc.page_content.lower()
        assert "scale-out" in oran_doc.page_content.lower()
        assert "provisioningrequest" in oran_doc.page_content.lower()

        scaling_doc = next(d for d in documents if "scaling" in d.metadata["source_url"])
        assert "scaling" in scaling_doc.page_content.lower()
        assert "horizontal" in scaling_doc.page_content.lower()
        assert "vertical" in scaling_doc.page_content.lower()

        # Verify load statistics
        stats = loader.get_load_statistics()
        assert stats["successful_loads"] == 3
        assert stats["failed_loads"] == 0
        assert stats["success_rate"] == 100.0

    @patch('src.oran_nephio_rag.HUGGINGFACE_EMBEDDINGS_AVAILABLE', False)
    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', True)
    @responses.activate
    def test_vector_database_creation_pipeline(self, integration_config, mock_document_sources, mock_html_responses):
        """Test complete vector database creation pipeline with TF-IDF embeddings"""
        from src.document_loader import DocumentLoader
        from src.oran_nephio_rag import VectorDatabaseManager

        # Setup HTTP responses
        for url, html_content in mock_html_responses.items():
            responses.add(responses.GET, url, body=html_content, status=200, content_type="text/html")

        # Load documents
        loader = DocumentLoader(integration_config)
        documents = loader.load_all_documents(mock_document_sources)

        # Create vector database manager with TF-IDF embeddings
        with patch('chromadb.Client') as mock_client, \
             patch('src.oran_nephio_rag.Chroma') as mock_chroma:

            # Setup mock vector database
            mock_vectordb = MagicMock()
            mock_chroma.from_documents.return_value = mock_vectordb

            vector_manager = VectorDatabaseManager(integration_config)

            # Build vector database
            result = vector_manager.build_vector_database(documents)

            # Assertions
            assert result is True
            assert vector_manager.vectordb == mock_vectordb
            assert vector_manager.last_update is not None

            # Verify text splitting and embedding calls
            mock_chroma.from_documents.assert_called_once()
            call_args = mock_chroma.from_documents.call_args

            # Verify documents were split into chunks
            split_documents = call_args[1]["documents"]
            assert len(split_documents) > len(documents)  # Should be split into chunks

            # Verify embedding function is set
            assert call_args[1]["embedding"] == vector_manager.embeddings
            assert call_args[1]["collection_name"] == integration_config.COLLECTION_NAME
            assert call_args[1]["persist_directory"] == integration_config.VECTOR_DB_PATH

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    @patch('src.oran_nephio_rag.HUGGINGFACE_EMBEDDINGS_AVAILABLE', False)
    @responses.activate
    def test_end_to_end_query_pipeline(self, mock_create_manager, integration_config, mock_document_sources, mock_html_responses):
        """Test complete end-to-end query processing pipeline"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup HTTP responses
        for url, html_content in mock_html_responses.items():
            responses.add(responses.GET, url, body=html_content, status=200, content_type="text/html")

        # Setup Puter.js RAG manager mock
        mock_rag_manager = MagicMock()
        mock_rag_manager.query.return_value = {
            "success": True,
            "answer": "Based on the Nephio documentation, you can scale O-RAN network functions by creating a ProvisioningRequest CRD with the desired replica count and geographic distribution. This enables horizontal scaling across multiple edge clusters while maintaining performance and connectivity requirements."
        }
        mock_create_manager.return_value = mock_rag_manager

        # Mock vector database components
        with patch('chromadb.Client') as mock_client, \
             patch('src.oran_nephio_rag.Chroma') as mock_chroma:

            # Setup mock vector database with realistic search results
            mock_vectordb = MagicMock()
            mock_vectordb._collection.count.return_value = 15

            # Mock similarity search results
            mock_doc1 = Document(
                page_content="To scale out O-RAN network functions using Nephio: Create a ProvisioningRequest CRD with the desired replica count and geographic distribution",
                metadata={"source": "https://docs.nephio.org/o-ran-integration", "type": "nephio"}
            )
            mock_doc2 = Document(
                page_content="Nephio supports both horizontal and vertical scaling of network functions across multiple clusters and edge locations",
                metadata={"source": "https://docs.nephio.org/architecture", "type": "nephio"}
            )
            mock_doc3 = Document(
                page_content="Horizontal scaling increases the number of network function instances across edge clusters with geographic distribution",
                metadata={"source": "https://docs.nephio.org/scaling", "type": "nephio"}
            )

            mock_vectordb.similarity_search_with_score.return_value = [
                (mock_doc1, 0.95),
                (mock_doc2, 0.88),
                (mock_doc3, 0.82)
            ]

            mock_chroma.from_documents.return_value = mock_vectordb
            mock_chroma.return_value = mock_vectordb

            # Override config sources for testing
            integration_config.OFFICIAL_SOURCES = mock_document_sources

            # Create and initialize RAG system
            rag_system = ORANNephioRAG(integration_config)

            # Initialize system (this will load documents and build vector DB)
            init_result = rag_system.initialize_system()
            assert init_result is True
            assert rag_system.is_ready is True

            # Test query processing
            query = "How do I scale O-RAN network functions using Nephio?"
            result = rag_system.query(query)

            # Assertions
            assert result["success"] is True
            assert "answer" in result
            assert "sources" in result
            assert "query_time" in result
            assert result["constraint_compliant"] is True

            # Verify answer quality
            answer = result["answer"].lower()
            assert "nephio" in answer or "provisioningrequest" in answer or "scaling" in answer

            # Verify sources
            assert len(result["sources"]) == 3
            for source in result["sources"]:
                assert "content" in source
                assert "metadata" in source
                assert "similarity_score" in source
                assert source["similarity_score"] > 0.8

            # Verify retrieval scores
            assert "retrieval_scores" in result
            assert len(result["retrieval_scores"]) == 3
            assert all(score > 0.8 for score in result["retrieval_scores"])

    @responses.activate
    def test_pipeline_with_failed_document_sources(self, integration_config, mock_html_responses):
        """Test pipeline resilience with some failed document sources"""
        from src.document_loader import DocumentLoader
        from src.config import DocumentSource

        # Setup mixed success/failure sources
        mixed_sources = [
            DocumentSource(
                url="https://docs.nephio.org/architecture",
                source_type="nephio",
                description="Working Architecture Guide",
                priority=1,
                enabled=True
            ),
            DocumentSource(
                url="https://docs.nephio.org/nonexistent",
                source_type="nephio",
                description="Non-existent Guide",
                priority=2,
                enabled=True
            ),
            DocumentSource(
                url="https://docs.nephio.org/scaling",
                source_type="nephio",
                description="Working Scaling Guide",
                priority=2,
                enabled=True
            )
        ]

        # Setup responses (missing nonexistent URL)
        responses.add(
            responses.GET,
            "https://docs.nephio.org/architecture",
            body=mock_html_responses["https://docs.nephio.org/architecture"],
            status=200
        )
        responses.add(
            responses.GET,
            "https://docs.nephio.org/scaling",
            body=mock_html_responses["https://docs.nephio.org/scaling"],
            status=200
        )
        responses.add(
            responses.GET,
            "https://docs.nephio.org/nonexistent",
            status=404
        )

        # Test document loading
        loader = DocumentLoader(integration_config)
        documents = loader.load_all_documents(mixed_sources)

        # Should load 2 successful documents plus fallback for failed one
        assert len(documents) >= 2

        # Verify load statistics reflect partial failure
        stats = loader.get_load_statistics()
        assert stats["total_attempts"] == 3
        assert stats["successful_loads"] >= 2
        assert stats["failed_loads"] <= 1

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    @responses.activate
    def test_pipeline_with_puter_failure_fallback(self, mock_create_manager, integration_config, mock_document_sources, mock_html_responses):
        """Test pipeline behavior when Puter.js fails and fallback is used"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Setup HTTP responses
        for url, html_content in mock_html_responses.items():
            responses.add(responses.GET, url, body=html_content, status=200)

        # Setup Puter.js failure
        mock_rag_manager = MagicMock()
        mock_rag_manager.query.return_value = {
            "success": False,
            "error": "Browser session initialization failed"
        }
        mock_create_manager.return_value = mock_rag_manager

        # Mock vector database
        with patch('chromadb.Client'), patch('src.oran_nephio_rag.Chroma') as mock_chroma:
            mock_vectordb = MagicMock()
            mock_vectordb._collection.count.return_value = 10

            # Setup search results for fallback
            mock_doc = Document(
                page_content="Nephio supports scaling of network functions. O-RAN components can be scaled horizontally across clusters.",
                metadata={"source": "test", "type": "nephio"}
            )
            mock_vectordb.similarity_search_with_score.return_value = [(mock_doc, 0.9)]

            mock_chroma.from_documents.return_value = mock_vectordb
            mock_chroma.return_value = mock_vectordb

            integration_config.OFFICIAL_SOURCES = mock_document_sources

            # Test system initialization and query
            rag_system = ORANNephioRAG(integration_config)
            init_result = rag_system.initialize_system()
            assert init_result is True

            # Query should use fallback method
            result = rag_system.query("How to scale Nephio?")

            # Should still get a response via fallback
            assert "answer" in result
            assert "sources" in result
            # Fallback may not be marked as successful in the same way
            assert len(result["sources"]) > 0

    def test_system_status_integration(self, integration_config):
        """Test system status reporting across all components"""
        from src.oran_nephio_rag import ORANNephioRAG

        # Mock all external dependencies
        with patch('src.document_loader.requests.Session'), \
             patch('chromadb.Client'), \
             patch('src.oran_nephio_rag.Chroma') as mock_chroma, \
             patch('src.oran_nephio_rag.create_puter_rag_manager'):

            # Setup vector database mock
            mock_vectordb = MagicMock()
            mock_vectordb._collection.count.return_value = 50
            mock_chroma.return_value = mock_vectordb

            rag_system = ORANNephioRAG(integration_config)
            rag_system.is_ready = True
            rag_system.last_build_time = datetime(2024, 1, 15, 10, 30, 0)

            # Mock components
            rag_system.vector_manager.vectordb = mock_vectordb
            rag_system.query_processor = MagicMock()

            # Mock document loader statistics
            rag_system.document_loader.get_load_statistics = MagicMock(return_value={
                "total_sources": 10,
                "enabled_sources": 8,
                "successful_loads": 7,
                "failed_loads": 1,
                "success_rate": 87.5
            })

            # Get system status
            status = rag_system.get_system_status()

            # Verify comprehensive status reporting
            required_fields = [
                "system_ready", "last_build_time", "config_valid",
                "vectordb_ready", "vectordb_info", "qa_chain_ready",
                "total_sources", "enabled_sources", "load_statistics",
                "constraint_compliant", "integration_method"
            ]

            for field in required_fields:
                assert field in status

            assert status["system_ready"] is True
            assert status["config_valid"] is True
            assert status["qa_chain_ready"] is True
            assert status["constraint_compliant"] is True
            assert status["integration_method"] == "browser_automation"
            assert status["last_build_time"] == "2024-01-15T10:30:00"


class TestPipelinePerformance:
    """Integration tests for pipeline performance characteristics"""

    @pytest.fixture
    def performance_config(self, temp_test_dir):
        """Configuration optimized for performance testing"""
        from src.config import Config

        config = Config()
        config.VECTOR_DB_PATH = os.path.join(temp_test_dir, "perf_vectordb")
        config.CHUNK_SIZE = 512
        config.CHUNK_OVERLAP = 100
        config.REQUEST_TIMEOUT = 10
        config.MAX_RETRIES = 1  # Faster testing
        config.REQUEST_DELAY = 0.1  # Minimal delay

        return config

    @pytest.fixture
    def large_document_set(self):
        """Generate larger document set for performance testing"""
        documents = []

        for i in range(10):
            content = f"""
            Document {i}: Nephio Network Function Management

            This document covers advanced topics in Nephio network function management including:
            - Kubernetes-based orchestration and automation platform capabilities
            - O-RAN network function deployment and scaling strategies
            - Intent-driven automation for telecom network operations
            - Multi-cluster management and edge deployment scenarios
            - GitOps workflows and configuration management practices
            - Performance monitoring and observability features
            - Security and compliance considerations for telecom workloads
            - Integration with cloud native ecosystem and CNCF projects

            Scaling Procedures for Document {i}:
            1. Create ProvisioningRequest custom resource definitions
            2. Specify geographic distribution and resource requirements
            3. Apply intent-driven policies for automated scaling
            4. Monitor performance metrics and quality of service indicators
            5. Validate network function connectivity and service continuity

            Additional technical details and implementation guidance...
            """

            documents.append(Document(
                page_content=content,
                metadata={
                    "source": f"https://docs.nephio.org/perf-test-{i}",
                    "type": "nephio",
                    "doc_id": i,
                    "content_length": len(content)
                }
            ))

        return documents

    @patch('src.oran_nephio_rag.HUGGINGFACE_EMBEDDINGS_AVAILABLE', False)
    def test_large_document_processing_performance(self, performance_config, large_document_set):
        """Test performance with larger document set"""
        from src.oran_nephio_rag import VectorDatabaseManager
        import time

        with patch('chromadb.Client'), patch('src.oran_nephio_rag.Chroma') as mock_chroma:
            mock_vectordb = MagicMock()
            mock_chroma.from_documents.return_value = mock_vectordb

            vector_manager = VectorDatabaseManager(performance_config)

            # Measure processing time
            start_time = time.time()
            result = vector_manager.build_vector_database(large_document_set)
            end_time = time.time()

            processing_time = end_time - start_time

            # Assertions
            assert result is True
            assert processing_time < 10.0  # Should complete within 10 seconds

            # Verify text splitting performance
            call_args = mock_chroma.from_documents.call_args
            split_documents = call_args[1]["documents"]

            # Should efficiently split documents
            assert len(split_documents) > len(large_document_set)
            # Reasonable split ratio
            assert len(split_documents) < len(large_document_set) * 10

    @patch('src.oran_nephio_rag.create_puter_rag_manager')
    def test_query_response_time_performance(self, mock_create_manager, performance_config):
        """Test query response time performance"""
        from src.oran_nephio_rag import ORANNephioRAG
        import time

        # Setup fast Puter.js mock
        mock_rag_manager = MagicMock()
        mock_rag_manager.query.return_value = {
            "success": True,
            "answer": "Fast mock response for performance testing"
        }
        mock_create_manager.return_value = mock_rag_manager

        with patch('chromadb.Client'), patch('src.oran_nephio_rag.Chroma') as mock_chroma:
            # Setup fast vector search
            mock_vectordb = MagicMock()
            mock_vectordb._collection.count.return_value = 100

            fast_doc = Document(
                page_content="Quick response content for performance testing",
                metadata={"source": "test", "type": "nephio"}
            )
            mock_vectordb.similarity_search_with_score.return_value = [
                (fast_doc, 0.9)
            ]

            mock_chroma.return_value = mock_vectordb

            # Initialize system
            rag_system = ORANNephioRAG(performance_config)
            rag_system.is_ready = True
            rag_system.vector_manager.vectordb = mock_vectordb

            # Mock query processor for speed
            from src.oran_nephio_rag import QueryProcessor
            rag_system.query_processor = QueryProcessor(performance_config, rag_system.vector_manager)

            # Measure query response time
            queries = [
                "What is Nephio?",
                "How to scale O-RAN functions?",
                "Network function deployment guide",
                "Kubernetes automation platform",
                "Intent-driven scaling procedures"
            ]

            total_start = time.time()

            for query in queries:
                query_start = time.time()
                result = rag_system.query(query)
                query_end = time.time()

                query_time = query_end - query_start

                # Each query should complete quickly
                assert query_time < 5.0
                assert "answer" in result
                assert "query_time" in result

            total_end = time.time()
            total_time = total_end - total_start

            # All queries should complete within reasonable time
            assert total_time < 15.0
            average_time = total_time / len(queries)
            assert average_time < 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])