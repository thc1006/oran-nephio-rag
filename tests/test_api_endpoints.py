"""
API endpoint testing with various query types
Testing: FastAPI endpoints, query processing, response validation, error handling
"""

import os
import pytest
import json
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any, List
from datetime import datetime

# FastAPI testing imports
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Test data models
class QueryRequest(BaseModel):
    """Request model for API queries"""
    question: str
    k: int = 5
    stream: bool = False
    include_sources: bool = True
    model: str = "claude-sonnet-4"

class QueryResponse(BaseModel):
    """Response model for API queries"""
    success: bool
    answer: str
    sources: List[Dict[str, Any]] = []
    query_time: float
    metadata: Dict[str, Any] = {}


class TestAPIEndpoints:
    """Test API endpoints and HTTP interface"""

    @pytest.fixture
    def mock_rag_system(self):
        """Mock RAG system for API testing"""
        rag_system = MagicMock()
        rag_system.is_ready = True
        rag_system.query.return_value = {
            "success": True,
            "answer": "Nephio is a Kubernetes-based cloud native intent automation platform designed for telecom networks.",
            "sources": [
                {
                    "content": "Nephio provides intent-driven automation...",
                    "metadata": {
                        "source": "https://docs.nephio.org/architecture",
                        "type": "nephio",
                        "title": "Architecture Guide"
                    },
                    "similarity_score": 0.95
                }
            ],
            "query_time": 2.1,
            "context_used": 3,
            "retrieval_scores": [0.95, 0.88, 0.82],
            "constraint_compliant": True,
            "generation_method": "puter_js_browser"
        }
        rag_system.get_system_status.return_value = {
            "system_ready": True,
            "vectordb_ready": True,
            "qa_chain_ready": True,
            "total_sources": 10,
            "enabled_sources": 8,
            "last_update": "2024-01-15T10:30:00",
            "constraint_compliant": True
        }
        return rag_system

    @pytest.fixture
    def api_app(self, mock_rag_system):
        """Create FastAPI app for testing"""
        app = FastAPI(title="O-RAN × Nephio RAG API", version="1.0.0")

        # Store RAG system in app state
        app.state.rag_system = mock_rag_system

        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "oran-nephio-rag-api"
            }

        @app.get("/status")
        async def system_status():
            """Get system status"""
            if not hasattr(app.state, 'rag_system'):
                raise HTTPException(status_code=503, detail="RAG system not initialized")

            try:
                status = app.state.rag_system.get_system_status()
                return {
                    "status": "ok" if status.get("system_ready") else "degraded",
                    "rag_system": status,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

        @app.post("/query")
        async def process_query(request: QueryRequest):
            """Process RAG query"""
            if not hasattr(app.state, 'rag_system'):
                raise HTTPException(status_code=503, detail="RAG system not initialized")

            if not app.state.rag_system.is_ready:
                raise HTTPException(status_code=503, detail="RAG system not ready")

            try:
                # Process query with RAG system
                result = app.state.rag_system.query(
                    request.question,
                    k=request.k,
                    stream=request.stream,
                    model=request.model
                )

                # Format response
                response_data = {
                    "success": result.get("success", True),
                    "answer": result.get("answer", ""),
                    "query_time": result.get("query_time", 0.0),
                    "metadata": {
                        "context_used": result.get("context_used", 0),
                        "generation_method": result.get("generation_method", "unknown"),
                        "constraint_compliant": result.get("constraint_compliant", True),
                        "model": request.model,
                        "retrieval_k": request.k
                    }
                }

                if request.include_sources:
                    response_data["sources"] = result.get("sources", [])

                if not result.get("success", True):
                    response_data["error"] = result.get("error", "Unknown error")

                return response_data

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

        @app.post("/batch-query")
        async def process_batch_queries(requests: List[QueryRequest]):
            """Process multiple queries in batch"""
            if not hasattr(app.state, 'rag_system'):
                raise HTTPException(status_code=503, detail="RAG system not initialized")

            if len(requests) > 10:
                raise HTTPException(status_code=400, detail="Maximum 10 queries per batch")

            results = []
            for req in requests:
                try:
                    result = app.state.rag_system.query(
                        req.question,
                        k=req.k,
                        stream=req.stream,
                        model=req.model
                    )

                    response_data = {
                        "question": req.question,
                        "success": result.get("success", True),
                        "answer": result.get("answer", ""),
                        "query_time": result.get("query_time", 0.0)
                    }

                    if req.include_sources:
                        response_data["sources"] = result.get("sources", [])

                    results.append(response_data)

                except Exception as e:
                    results.append({
                        "question": req.question,
                        "success": False,
                        "error": str(e),
                        "query_time": 0.0
                    })

            return {
                "batch_results": results,
                "total_queries": len(requests),
                "successful_queries": sum(1 for r in results if r.get("success", False)),
                "timestamp": datetime.utcnow().isoformat()
            }

        return app

    @pytest.fixture
    def client(self, api_app):
        """Create test client"""
        return TestClient(api_app)

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "oran-nephio-rag-api"

    def test_system_status_endpoint(self, client):
        """Test system status endpoint"""
        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "rag_system" in data
        assert "timestamp" in data

        rag_status = data["rag_system"]
        assert rag_status["system_ready"] is True
        assert rag_status["vectordb_ready"] is True
        assert rag_status["qa_chain_ready"] is True

    def test_query_endpoint_basic(self, client):
        """Test basic query endpoint functionality"""
        query_data = {
            "question": "What is Nephio?",
            "k": 5,
            "include_sources": True
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "answer" in data
        assert "query_time" in data
        assert "metadata" in data
        assert "sources" in data

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["constraint_compliant"] is True
        assert metadata["retrieval_k"] == 5
        assert "generation_method" in metadata

    def test_query_endpoint_without_sources(self, client):
        """Test query endpoint without sources"""
        query_data = {
            "question": "How to scale O-RAN functions?",
            "include_sources": False
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "sources" not in data or data["sources"] == []

    def test_query_endpoint_with_custom_parameters(self, client):
        """Test query endpoint with custom parameters"""
        query_data = {
            "question": "Explain Nephio architecture",
            "k": 8,
            "stream": False,
            "model": "claude-opus-4",
            "include_sources": True
        }

        response = client.post("/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        metadata = data["metadata"]
        assert metadata["model"] == "claude-opus-4"
        assert metadata["retrieval_k"] == 8

    def test_query_endpoint_validation_errors(self, client):
        """Test query endpoint input validation"""
        # Empty question
        response = client.post("/query", json={"question": ""})
        assert response.status_code == 422  # Validation error

        # Missing question
        response = client.post("/query", json={"k": 5})
        assert response.status_code == 422

        # Invalid k value
        response = client.post("/query", json={"question": "test", "k": -1})
        assert response.status_code == 422

    def test_query_endpoint_error_handling(self, client, mock_rag_system):
        """Test query endpoint error handling"""
        # Mock RAG system failure
        mock_rag_system.query.side_effect = Exception("RAG system error")

        query_data = {"question": "Test question"}
        response = client.post("/query", json=query_data)

        assert response.status_code == 500
        assert "Query processing failed" in response.json()["detail"]

    def test_query_endpoint_system_not_ready(self, client, mock_rag_system):
        """Test query endpoint when system not ready"""
        mock_rag_system.is_ready = False

        query_data = {"question": "Test question"}
        response = client.post("/query", json=query_data)

        assert response.status_code == 503
        assert "not ready" in response.json()["detail"]

    def test_batch_query_endpoint(self, client):
        """Test batch query endpoint"""
        batch_data = [
            {"question": "What is Nephio?", "k": 3},
            {"question": "How to scale O-RAN?", "k": 5},
            {"question": "Network function deployment?", "k": 4}
        ]

        response = client.post("/batch-query", json=batch_data)

        assert response.status_code == 200
        data = response.json()

        assert "batch_results" in data
        assert data["total_queries"] == 3
        assert data["successful_queries"] == 3
        assert len(data["batch_results"]) == 3

        # Verify each result
        for i, result in enumerate(data["batch_results"]):
            assert result["question"] == batch_data[i]["question"]
            assert result["success"] is True
            assert "answer" in result

    def test_batch_query_size_limit(self, client):
        """Test batch query size limit"""
        # Too many queries
        large_batch = [{"question": f"Question {i}"} for i in range(15)]

        response = client.post("/batch-query", json=large_batch)
        assert response.status_code == 400
        assert "Maximum 10 queries" in response.json()["detail"]

    def test_batch_query_partial_failure(self, client, mock_rag_system):
        """Test batch query with partial failures"""
        # Mock alternating success/failure
        def mock_query_side_effect(question, **kwargs):
            if "fail" in question.lower():
                raise Exception("Simulated failure")
            return {
                "success": True,
                "answer": f"Answer for: {question}",
                "sources": [],
                "query_time": 1.0
            }

        mock_rag_system.query.side_effect = mock_query_side_effect

        batch_data = [
            {"question": "Success question 1"},
            {"question": "This should fail"},
            {"question": "Success question 2"}
        ]

        response = client.post("/batch-query", json=batch_data)

        assert response.status_code == 200
        data = response.json()

        assert data["total_queries"] == 3
        assert data["successful_queries"] == 2

        results = data["batch_results"]
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[2]["success"] is True
        assert "error" in results[1]


class TestQueryTypes:
    """Test different types of queries and their responses"""

    @pytest.fixture
    def query_client(self, api_app):
        """Test client for query testing"""
        return TestClient(api_app)

    def test_architecture_queries(self, query_client, mock_rag_system):
        """Test architecture-related queries"""
        # Mock specific response for architecture queries
        mock_rag_system.query.return_value = {
            "success": True,
            "answer": "Nephio architecture consists of Porch for package orchestration, Nephio Controllers for automation, Resource Backend for inventory management, and WebUI for system management.",
            "sources": [
                {
                    "content": "Nephio architecture overview...",
                    "metadata": {"source": "https://docs.nephio.org/architecture", "type": "nephio"},
                    "similarity_score": 0.92
                }
            ],
            "query_time": 1.8,
            "generation_method": "puter_js_browser"
        }

        architecture_queries = [
            "What is Nephio architecture?",
            "Explain Nephio core components",
            "How is Nephio designed?",
            "Nephio system architecture overview"
        ]

        for query in architecture_queries:
            response = query_client.post("/query", json={"question": query})
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert "nephio" in data["answer"].lower()
            assert "architecture" in data["answer"].lower() or "component" in data["answer"].lower()

    def test_scaling_queries(self, query_client, mock_rag_system):
        """Test scaling-related queries"""
        mock_rag_system.query.return_value = {
            "success": True,
            "answer": "O-RAN network functions can be scaled using Nephio by creating ProvisioningRequest CRDs with desired replica counts and geographic distribution. Both horizontal scale-out and vertical scale-up strategies are supported.",
            "sources": [
                {
                    "content": "O-RAN scaling procedures...",
                    "metadata": {"source": "https://docs.nephio.org/scaling", "type": "nephio"},
                    "similarity_score": 0.94
                }
            ],
            "query_time": 2.2,
            "generation_method": "puter_js_browser"
        }

        scaling_queries = [
            "How to scale O-RAN network functions?",
            "Nephio scaling strategies",
            "Network function scale-out procedures",
            "Horizontal and vertical scaling in Nephio"
        ]

        for query in scaling_queries:
            response = query_client.post("/query", json={"question": query})
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            answer_lower = data["answer"].lower()
            assert any(term in answer_lower for term in ["scale", "scaling", "replica", "horizontal", "vertical"])

    def test_oran_specific_queries(self, query_client, mock_rag_system):
        """Test O-RAN specific queries"""
        mock_rag_system.query.return_value = {
            "success": True,
            "answer": "O-RAN provides open interfaces and architecture for RAN disaggregation with components including O-CU (Central Unit), O-DU (Distributed Unit), O-RU (Radio Unit), and integration with SMO for orchestration.",
            "sources": [
                {
                    "content": "O-RAN integration details...",
                    "metadata": {"source": "https://docs.nephio.org/o-ran", "type": "nephio"},
                    "similarity_score": 0.96
                }
            ],
            "query_time": 2.0,
            "generation_method": "puter_js_browser"
        }

        oran_queries = [
            "What is O-RAN?",
            "O-RAN components and architecture",
            "O-CU, O-DU, O-RU explanation",
            "O-RAN integration with Nephio"
        ]

        for query in oran_queries:
            response = query_client.post("/query", json={"question": query})
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            answer_lower = data["answer"].lower()
            assert "o-ran" in answer_lower or "oran" in answer_lower

    def test_deployment_queries(self, query_client, mock_rag_system):
        """Test deployment-related queries"""
        mock_rag_system.query.return_value = {
            "success": True,
            "answer": "Network function deployment in Nephio involves creating package configurations, applying intent-driven automation, and using GitOps workflows for multi-cluster orchestration.",
            "sources": [
                {
                    "content": "NF deployment procedures...",
                    "metadata": {"source": "https://docs.nephio.org/deployment", "type": "nephio"},
                    "similarity_score": 0.89
                }
            ],
            "query_time": 1.9,
            "generation_method": "puter_js_browser"
        }

        deployment_queries = [
            "How to deploy network functions?",
            "NF deployment guide",
            "Network function lifecycle management",
            "Deployment automation in Nephio"
        ]

        for query in deployment_queries:
            response = query_client.post("/query", json={"question": query})
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            answer_lower = data["answer"].lower()
            assert any(term in answer_lower for term in ["deploy", "deployment", "lifecycle", "automation"])

    def test_complex_queries(self, query_client, mock_rag_system):
        """Test complex multi-part queries"""
        mock_rag_system.query.return_value = {
            "success": True,
            "answer": "To implement O-RAN scale-out with Nephio: 1) Create ProvisioningRequest CRDs specifying O-RAN component requirements, 2) Define geographic distribution across edge sites, 3) Configure resource constraints and scaling policies, 4) Apply intent-driven automation for deployment, 5) Monitor performance and adjust scaling parameters as needed.",
            "sources": [
                {
                    "content": "Complex O-RAN scaling implementation...",
                    "metadata": {"source": "https://docs.nephio.org/advanced", "type": "nephio"},
                    "similarity_score": 0.91
                }
            ],
            "query_time": 3.1,
            "generation_method": "puter_js_browser"
        }

        complex_queries = [
            "How to implement O-RAN scale-out with Nephio across multiple edge locations?",
            "What are the steps for automated O-RAN deployment using Nephio controllers?",
            "Explain the integration between Nephio, O-RAN, and SMO for network automation",
            "How does Nephio handle multi-cluster O-RAN network function lifecycle management?"
        ]

        for query in complex_queries:
            response = query_client.post("/query", json={"question": query, "k": 8})
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert len(data["answer"]) > 100  # Complex queries should have detailed answers
            assert data["metadata"]["retrieval_k"] == 8

    def test_edge_case_queries(self, query_client, mock_rag_system):
        """Test edge case queries"""
        # Mock response for edge cases
        def mock_edge_case_response(question, **kwargs):
            if len(question.strip()) < 3:
                return {
                    "success": False,
                    "answer": "Query too short to process effectively.",
                    "error": "insufficient_query_length"
                }
            elif "unrelated" in question.lower():
                return {
                    "success": False,
                    "answer": "No relevant information found for this query.",
                    "error": "no_relevant_docs"
                }
            else:
                return {
                    "success": True,
                    "answer": "Standard response for edge case query.",
                    "sources": []
                }

        mock_rag_system.query.side_effect = mock_edge_case_response

        edge_cases = [
            {"query": "?", "should_succeed": False},
            {"query": "ab", "should_succeed": False},
            {"query": "completely unrelated topic", "should_succeed": False},
            {"query": "very long query " * 20, "should_succeed": True},
            {"query": "Query with symbols !@#$%^&*()", "should_succeed": True}
        ]

        for case in edge_cases:
            response = query_client.post("/query", json={"question": case["query"]})
            assert response.status_code == 200

            data = response.json()
            if case["should_succeed"]:
                assert data["success"] is True
            else:
                assert data["success"] is False
                assert "error" in data or not data["success"]


class TestAPIPerformance:
    """Test API performance characteristics"""

    @pytest.fixture
    def performance_client(self, api_app):
        """Client for performance testing"""
        return TestClient(api_app)

    def test_concurrent_query_handling(self, performance_client, mock_rag_system):
        """Test handling of concurrent queries"""
        import threading
        import time

        results = []

        def make_query(query_id):
            start_time = time.time()
            response = performance_client.post(
                "/query",
                json={"question": f"Performance test query {query_id}"}
            )
            end_time = time.time()

            results.append({
                "query_id": query_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.json().get("success", False) if response.status_code == 200 else False
            })

        # Create multiple threads for concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_query, args=(i,))
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # Verify results
        assert len(results) == 5
        assert all(r["status_code"] == 200 for r in results)
        assert all(r["success"] for r in results)
        assert total_time < 10.0  # Should complete within reasonable time

        # Check individual response times
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        assert avg_response_time < 5.0  # Average response time should be reasonable

    def test_batch_query_performance(self, performance_client, mock_rag_system):
        """Test batch query performance"""
        import time

        # Create batch of queries
        batch_queries = [
            {"question": f"Performance batch query {i}", "k": 3}
            for i in range(8)
        ]

        start_time = time.time()
        response = performance_client.post("/batch-query", json=batch_queries)
        end_time = time.time()

        processing_time = end_time - start_time

        assert response.status_code == 200
        data = response.json()

        assert data["total_queries"] == 8
        assert data["successful_queries"] == 8
        assert processing_time < 15.0  # Batch should complete reasonably quickly

    def test_large_query_handling(self, performance_client, mock_rag_system):
        """Test handling of large queries"""
        # Create large query
        large_query = "How does Nephio handle " + "network function scaling and deployment across multiple edge clusters with geographic distribution and resource optimization considering performance requirements and quality of service metrics while maintaining security compliance and operational efficiency in cloud native environments with Kubernetes orchestration and intent-driven automation workflows " * 10

        response = performance_client.post(
            "/query",
            json={"question": large_query, "k": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "answer" in data


class TestAPIErrorHandling:
    """Test API error handling and resilience"""

    @pytest.fixture
    def error_client(self, api_app):
        """Client for error testing"""
        return TestClient(api_app)

    def test_rag_system_not_initialized(self, error_client):
        """Test behavior when RAG system not initialized"""
        # Remove RAG system from app state
        error_client.app.state.__dict__.pop('rag_system', None)

        response = error_client.post("/query", json={"question": "test"})
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"]

        response = error_client.get("/status")
        assert response.status_code == 503

    def test_invalid_json_request(self, error_client):
        """Test invalid JSON in request"""
        response = error_client.post(
            "/query",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_content_type(self, error_client):
        """Test missing content type header"""
        response = error_client.post("/query", data='{"question": "test"}')
        # FastAPI should handle this gracefully
        assert response.status_code in [200, 422]

    def test_status_endpoint_errors(self, error_client, mock_rag_system):
        """Test status endpoint error handling"""
        # Mock status method to raise exception
        mock_rag_system.get_system_status.side_effect = Exception("Status error")

        response = error_client.get("/status")
        assert response.status_code == 500
        assert "Failed to get system status" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])