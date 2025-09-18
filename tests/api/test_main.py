"""
Tests for the main API application
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client"""
    from src.api.main import create_app

    app = create_app()
    return TestClient(app)


class TestMainAPI:
    """Test the main API endpoints"""

    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "O-RAN × Nephio RAG API" in data["message"]
        assert "version" in data["data"]
        assert "docs" in data["data"]

    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime" in data
        assert "components" in data

    def test_health_live_endpoint(self, client):
        """Test the liveness endpoint"""
        response = client.get("/health/live")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "alive" in data["data"]
        assert data["data"]["alive"] is True

    def test_health_ready_endpoint(self, client):
        """Test the readiness endpoint"""
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]  # May not be ready during tests

        data = response.json()
        assert "success" in data
        assert "ready" in data["data"]

    def test_openapi_docs(self, client):
        """Test OpenAPI documentation endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "O-RAN × Nephio RAG API"

    def test_swagger_docs(self, client):
        """Test Swagger documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_docs(self, client):
        """Test ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/")
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/")

        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers

    def test_request_id_header(self, client):
        """Test that request ID is added to responses"""
        response = client.get("/")
        assert "x-request-id" in response.headers

    def test_process_time_header(self, client):
        """Test that process time is added to responses"""
        response = client.get("/")
        assert "x-process-time" in response.headers

        # Process time should be a float
        process_time = float(response.headers["x-process-time"])
        assert process_time >= 0


class TestErrorHandling:
    """Test error handling"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "message" in data

    def test_method_not_allowed(self, client):
        """Test 405 error handling"""
        response = client.delete("/")  # DELETE not allowed on root
        assert response.status_code == 405

        data = response.json()
        assert data["success"] is False