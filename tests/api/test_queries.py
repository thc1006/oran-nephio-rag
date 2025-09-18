"""
Tests for query endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


@pytest.fixture
def client():
    """Create test client with mocked RAG system"""
    from src.api.main import create_app

    app = create_app()

    # Mock the RAG system
    mock_rag = Mock()
    mock_rag.is_ready = True
    mock_rag.query.return_value = {
        "success": True,
        "answer": "Test answer",
        "sources": [
            {
                "content": "Test content",
                "metadata": {"source_type": "nephio", "url": "https://example.com"},
                "similarity_score": 0.9,
            }
        ],
        "context_used": 1,
        "retrieval_scores": [0.9],
        "generation_method": "test",
        "constraint_compliant": True,
    }
    mock_rag.vector_manager.search_similar.return_value = [
        (Mock(page_content="Test content", metadata={"source_type": "nephio"}), 0.9)
    ]

    app.state.rag_system = mock_rag
    return TestClient(app)


class TestQueryEndpoints:
    """Test query-related endpoints"""

    def test_basic_query(self, client):
        """Test basic query endpoint"""
        query_data = {"query": "What is O-RAN?"}

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "query_time" in data
        assert data["constraint_compliant"] is True

    def test_query_with_parameters(self, client):
        """Test query with additional parameters"""
        query_data = {
            "query": "What is Nephio?",
            "k": 3,
            "include_sources": True,
            "stream": False,
        }

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["sources"]) <= 3

    def test_query_without_sources(self, client):
        """Test query without including sources"""
        query_data = {"query": "Test query", "include_sources": False}

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["sources"]) == 0

    def test_empty_query(self, client):
        """Test empty query validation"""
        query_data = {"query": ""}

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 422  # Validation error

    def test_long_query(self, client):
        """Test very long query validation"""
        query_data = {"query": "x" * 1001}  # Exceeds max length

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_k_parameter(self, client):
        """Test invalid k parameter"""
        query_data = {"query": "Test", "k": 25}  # Exceeds max k

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 422  # Validation error

    def test_search_endpoint(self, client):
        """Test document search endpoint"""
        search_data = {"query": "O-RAN", "k": 5}

        response = client.post("/api/v1/query/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total_found" in data
        assert "query_time" in data

    def test_search_with_filters(self, client):
        """Test search with filters"""
        search_data = {
            "query": "Nephio",
            "k": 10,
            "source_types": ["nephio"],
            "score_threshold": 0.5,
        }

        response = client.post("/api/v1/query/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "filters_applied" in data

    def test_bulk_query(self, client):
        """Test bulk query endpoint"""
        bulk_data = {
            "queries": ["What is O-RAN?", "What is Nephio?"],
            "k": 3,
            "include_sources": False,
        }

        response = client.post("/api/v1/query/bulk", json=bulk_data)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert "total_processed" in data
        assert "average_time" in data

    def test_bulk_query_too_many(self, client):
        """Test bulk query with too many queries"""
        bulk_data = {"queries": ["query"] * 15}  # Exceeds limit

        response = client.post("/api/v1/query/bulk", json=bulk_data)
        assert response.status_code == 422  # Validation error

    @patch("src.api.routers.queries.limiter.limit")
    def test_rate_limiting(self, mock_limit, client):
        """Test rate limiting (mocked)"""
        # This would normally test actual rate limiting
        # For now, just ensure the endpoint is accessible
        query_data = {"query": "Test query"}

        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 200


class TestQueryErrors:
    """Test query error scenarios"""

    def test_rag_system_not_available(self):
        """Test behavior when RAG system is not available"""
        from src.api.main import create_app

        app = create_app()
        app.state.rag_system = None  # No RAG system
        client = TestClient(app)

        query_data = {"query": "Test query"}
        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 503  # Service unavailable

    def test_rag_system_not_ready(self):
        """Test behavior when RAG system is not ready"""
        from src.api.main import create_app

        app = create_app()

        # Mock unready RAG system
        mock_rag = Mock()
        mock_rag.is_ready = False
        mock_rag.initialize_system.return_value = False
        app.state.rag_system = mock_rag

        client = TestClient(app)

        query_data = {"query": "Test query"}
        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 503  # Service unavailable

    def test_query_processing_error(self, client):
        """Test query processing error handling"""
        # Mock RAG system to raise an exception
        client.app.state.rag_system.query.side_effect = Exception("Test error")

        query_data = {"query": "Test query"}
        response = client.post("/api/v1/query/", json=query_data)
        assert response.status_code == 500

        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_invalid_json(self, client):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/v1/query/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422  # Unprocessable entity