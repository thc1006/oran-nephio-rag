# O-RAN × Nephio RAG API Documentation

## Overview

The O-RAN × Nephio RAG API provides developer-friendly REST endpoints for querying the RAG (Retrieval-Augmented Generation) system. This API enables applications to access O-RAN and Nephio documentation knowledge through natural language queries.

## Features

- **🔍 Intelligent Query Processing**: Natural language questions with contextual answers
- **📚 Document Management**: Upload, manage, and organize documentation sources
- **🔐 Authentication & Security**: API key and JWT token support with rate limiting
- **📊 Health Monitoring**: Comprehensive health checks and system status
- **📝 Request Validation**: Pydantic-based request/response validation
- **🛡️ Error Handling**: Structured error responses with detailed information
- **📈 Metrics & Logging**: Prometheus metrics and comprehensive logging

## Quick Start

### 1. Installation

```bash
# Install API dependencies
pip install -r src/api/requirements.txt

# Or install with the main project
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with the required configuration:

```bash
# API Configuration
API_MODE=browser  # or "mock" for testing
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Authentication (optional)
AUTH_MODE=optional  # "required", "optional", or "disabled"
API_KEY=your-secret-api-key
JWT_SECRET_KEY=your-super-secret-jwt-key

# Rate Limiting
REDIS_URL=redis://localhost:6379  # Optional: for distributed rate limiting

# RAG System Configuration
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
VECTOR_DB_PATH=./oran_nephio_vectordb
```

### 3. Run the API Server

```bash
# Development mode
python -m src.api.main

# Or with uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access the API

- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## API Endpoints

### Core Query Endpoints

#### POST `/api/v1/query/`
Process a natural language query and return an answer with sources.

```bash
curl -X POST "http://localhost:8000/api/v1/query/" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "query": "How do I implement O-RAN DU scale-out in Nephio?",
    "k": 5,
    "include_sources": true
  }'
```

#### POST `/api/v1/query/search`
Search for documents without generating answers.

```bash
curl -X POST "http://localhost:8000/api/v1/query/search" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "O-RAN network functions",
    "k": 10,
    "source_types": ["nephio"],
    "score_threshold": 0.7
  }'
```

#### POST `/api/v1/query/bulk`
Process multiple queries in a single request.

```bash
curl -X POST "http://localhost:8000/api/v1/query/bulk" \\
  -H "Content-Type: application/json" \\
  -d '{
    "queries": [
      "What is O-RAN?",
      "How does Nephio work?",
      "O2IMS integration patterns"
    ],
    "k": 3,
    "include_sources": false
  }'
```

### Document Management

#### GET `/api/v1/documents/`
List all configured document sources.

```bash
curl "http://localhost:8000/api/v1/documents/?source_type=nephio&enabled_only=true"
```

#### POST `/api/v1/documents/`
Add a new document source.

```bash
curl -X POST "http://localhost:8000/api/v1/documents/" \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://docs.nephio.org/new-guide/",
    "source_type": "nephio",
    "description": "New Nephio Guide",
    "priority": 2,
    "enabled": true
  }'
```

#### POST `/api/v1/documents/update`
Update the vector database with latest documents.

```bash
curl -X POST "http://localhost:8000/api/v1/documents/update" \\
  -H "Content-Type: application/json" \\
  -d '{
    "force_rebuild": false
  }'
```

### System Management

#### GET `/api/v1/system/status`
Get comprehensive system status.

```bash
curl "http://localhost:8000/api/v1/system/status" \\
  -H "Authorization: Bearer your-jwt-token"
```

#### GET `/api/v1/system/config`
Get current system configuration.

```bash
curl "http://localhost:8000/api/v1/system/config"
```

#### POST `/api/v1/system/restart`
Restart the RAG system components.

```bash
curl -X POST "http://localhost:8000/api/v1/system/restart" \\
  -H "Authorization: Bearer your-jwt-token"
```

### Health Monitoring

#### GET `/health`
Basic health check for load balancers.

```bash
curl "http://localhost:8000/health"
```

#### GET `/health/ready`
Readiness check for Kubernetes deployments.

```bash
curl "http://localhost:8000/health/ready"
```

#### GET `/health/live`
Liveness check for container orchestration.

```bash
curl "http://localhost:8000/health/live"
```

## Authentication

The API supports multiple authentication methods:

### API Key Authentication

Include the API key in the request header:

```bash
curl -H "X-API-Key: your-secret-api-key" "http://localhost:8000/api/v1/query/"
```

### JWT Token Authentication

1. Obtain a JWT token (implementation depends on your auth system)
2. Include it in the Authorization header:

```bash
curl -H "Authorization: Bearer your-jwt-token" "http://localhost:8000/api/v1/system/status"
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Query endpoints**: 10 requests per minute per user/IP
- **Search endpoints**: 20 requests per minute per user/IP
- **Bulk endpoints**: 2 requests per minute per user/IP
- **Other endpoints**: 60 requests per minute per user/IP

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## Error Handling

The API returns structured error responses:

```json
{
  "success": false,
  "error": "validation_error",
  "message": "Request validation failed",
  "details": {
    "validation_errors": [
      {
        "field": "query",
        "message": "field required",
        "type": "value_error.missing"
      }
    ],
    "request_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid request data
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation failed
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - System not ready

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Query processed successfully",
  "data": {
    "answer": "...",
    "sources": [...],
    "query_time": 1.23
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Query Response
```json
{
  "answer": "Based on the O-RAN and Nephio documentation...",
  "sources": [
    {
      "content": "Excerpt from source document...",
      "metadata": {
        "source_type": "nephio",
        "url": "https://docs.nephio.org/..."
      },
      "similarity_score": 0.95
    }
  ],
  "query_time": 2.14,
  "context_used": 3,
  "retrieval_scores": [0.95, 0.87, 0.82],
  "generation_method": "browser_automation",
  "constraint_compliant": true
}
```

## Testing

Run the API test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/api/

# Run specific test file
pytest tests/api/test_queries.py

# Run with coverage
pytest tests/api/ --cov=src/api --cov-report=html
```

## Monitoring

### Metrics Endpoint

Prometheus metrics are available at `/metrics`:

```bash
curl "http://localhost:8000/metrics"
```

Key metrics include:
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request duration histogram
- `rag_queries_total`: Total RAG queries
- `rag_query_duration_seconds`: Query duration histogram

### Logging

The API provides structured logging with request IDs for tracing:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "method": "POST",
  "path": "/api/v1/query/",
  "status_code": 200,
  "process_time": 2.14
}
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-nephio-rag-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oran-nephio-rag-api
  template:
    metadata:
      labels:
        app: oran-nephio-rag-api
    spec:
      containers:
      - name: api
        image: oran-nephio-rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_MODE
          value: "browser"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
```

## Development

### Project Structure

```
src/api/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application
├── models.py            # Pydantic models
├── auth.py              # Authentication
├── middleware.py        # Custom middleware
├── error_handlers.py    # Error handling
├── requirements.txt     # API dependencies
└── routers/
    ├── __init__.py
    ├── queries.py       # Query endpoints
    ├── documents.py     # Document management
    ├── health.py        # Health checks
    └── system.py        # System management
```

### Adding New Endpoints

1. Create a new router in `src/api/routers/`
2. Define Pydantic models in `src/api/models.py`
3. Add the router to `src/api/main.py`
4. Write tests in `tests/api/`

### Contributing

1. Follow the existing code style (Black, isort)
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all tests pass before submitting

## Troubleshooting

### Common Issues

1. **503 Service Unavailable**: RAG system not initialized
   - Check system status: `GET /api/v1/system/status`
   - Restart system: `POST /api/v1/system/restart`

2. **429 Rate Limit Exceeded**: Too many requests
   - Check rate limit headers in response
   - Implement exponential backoff in client

3. **401 Unauthorized**: Authentication failed
   - Verify API key or JWT token
   - Check authentication mode in configuration

4. **422 Validation Error**: Invalid request data
   - Check request format against API documentation
   - Validate required fields and data types

### Debug Mode

Enable debug mode for detailed error information:

```bash
export API_DEBUG=true
uvicorn src.api.main:app --reload --log-level debug
```

## Support

For questions or issues:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the [troubleshooting guide](#troubleshooting)
3. Check the system logs and metrics
4. Open an issue in the project repository