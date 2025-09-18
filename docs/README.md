# O-RAN × Nephio RAG API Documentation

Welcome to the comprehensive documentation for the O-RAN × Nephio RAG (Retrieval-Augmented Generation) system API. This documentation provides everything you need to integrate, deploy, and use the system effectively.

## 📚 Documentation Overview

This documentation covers:

- **API Reference**: Complete OpenAPI specification with examples
- **Quick Start**: Get up and running in minutes
- **Integration Examples**: Code samples for multiple languages and tools
- **Deployment Guides**: Docker, Kubernetes, and production setups
- **Configuration**: Environment variables and system tuning
- **Troubleshooting**: Common issues and solutions

## 🚀 Quick Navigation

### Getting Started
- [Quick Start Guide](guides/quick-start.md) - Get running in 5 minutes
- [Environment Setup](guides/environment-setup.md) - Complete development environment
- [Configuration Guide](guides/configuration.md) - All configuration options

### API Documentation
- [OpenAPI Specification](api/openapi.yaml) - Complete API reference
- [Integration Examples](examples/integration-examples.md) - Python, JavaScript, cURL, CLI

### Use Case Examples
- [O-RAN Queries](examples/oran-queries.md) - O-RAN architecture and components
- [Nephio Scenarios](examples/nephio-scenarios.md) - Cloud-native network automation

### Deployment
- [Docker Guide](deployment/docker-guide.md) - Containerization and Docker Compose
- [Kubernetes Guide](deployment/kubernetes-guide.md) - Production Kubernetes deployment
- [Kubernetes Manifests](deployment/kubernetes-manifests.yaml) - Ready-to-use K8s resources

### Operations
- [Troubleshooting Guide](guides/troubleshooting.md) - Common issues and solutions

## 🛠️ API Overview

The O-RAN × Nephio RAG API provides intelligent Q&A capabilities for telecommunications and cloud-native network functions through RESTful endpoints.

### Key Features

- 🤖 **AI-Powered Q&A**: Advanced natural language processing for technical queries
- 📚 **Official Documentation**: Automated ingestion from O-RAN Alliance and Nephio sources
- 🔍 **Semantic Search**: High-precision vector-based document retrieval
- ⚡ **Multiple Deployment Modes**: Browser automation, mock testing, and local inference
- 📊 **Comprehensive Monitoring**: Built-in metrics, logging, and health checks
- 🔒 **Enterprise Security**: Authentication, rate limiting, and audit trails

### Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com
```

### Authentication

```bash
# API Key (recommended for production)
Authorization: Bearer YOUR_API_KEY

# Or header-based
X-API-Key: YOUR_API_KEY
```

## 📋 Quick Examples

### Basic Query

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the O-RAN architecture?",
    "k": 5,
    "include_sources": true
  }'
```

### Python Integration

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "How does Nephio handle network function scaling?",
        "k": 8,
        "include_sources": True
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

### Search Documents

```bash
curl -X POST "http://localhost:8000/api/v1/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "network function scaling",
    "k": 10,
    "source_types": ["nephio"],
    "score_threshold": 0.7
  }'
```

## 🔗 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/api/v1/query` | POST | Query RAG system |
| `/api/v1/query/search` | POST | Search documents |
| `/api/v1/query/bulk` | POST | Bulk query processing |
| `/api/v1/documents` | GET/POST | List/add documents |
| `/api/v1/system/status` | GET | System status |
| `/api/v1/system/config` | GET | Configuration info |
| `/metrics` | GET | Prometheus metrics |

## 📖 Example Use Cases

### O-RAN Architecture Questions

```bash
# Basic O-RAN concepts
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main components of O-RAN architecture?"}'

# O-RAN interfaces
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the E2 interface and its role in O-RAN"}'

# RAN Intelligent Controller
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Near-Real-Time RIC and what are xApps?"}'
```

### Nephio Platform Questions

```bash
# Nephio overview
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does Nephio enable cloud-native network automation?"}'

# Package management
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Nephio package specialization process?"}'

# Free5GC integration
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How to deploy Free5GC using Nephio?"}'
```

## 🚀 Quick Start Options

### Option 1: Docker (Recommended)

```bash
# Development environment
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag
docker-compose -f docker-compose.dev.yml up -d

# Test API
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
echo "API_MODE=mock" > .env
echo "VECTOR_DB_PATH=./oran_nephio_vectordb" >> .env

# Initialize
python create_minimal_database.py
python -m src.api.main
```

### Option 3: Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f docs/deployment/kubernetes-manifests.yaml

# Check status
kubectl get pods -n oran-nephio-rag
kubectl port-forward service/oran-rag-service 8000:8000 -n oran-nephio-rag
```

## 🔧 Configuration Modes

### Mock Mode (Testing)
- **Use case**: Development, testing, demonstrations
- **Setup**: `API_MODE=mock`
- **Pros**: No API keys required, instant setup
- **Cons**: Pre-defined responses only

### Browser Mode (Production)
- **Use case**: Production deployments, full AI capabilities
- **Setup**: `API_MODE=browser` + `PUTER_MODEL=claude-sonnet-4`
- **Pros**: Access to latest AI models
- **Cons**: Requires browser setup

## 📊 System Status

Check system health and configuration:

```bash
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/v1/system/status

# Configuration
curl http://localhost:8000/api/v1/system/config

# Metrics (Prometheus format)
curl http://localhost:8000/metrics
```

## 🛡️ Security and Rate Limits

### Rate Limits
- Query endpoints: 10 requests per minute per IP
- Search endpoints: 20 requests per minute per IP
- Bulk operations: 2 requests per minute per IP

### Security Headers
- CORS support for web applications
- Security headers (HSTS, CSP, etc.)
- Input validation and sanitization
- SQL injection protection

## 📈 Monitoring and Observability

### Built-in Metrics
- Request count and duration
- Query processing time
- Error rates and types
- Resource utilization

### Health Checks
- `/health` - Basic health status
- `/health/ready` - Readiness for traffic
- Kubernetes probes supported

### Logging
- Structured JSON logging
- Configurable log levels
- Request tracing
- Performance metrics

## 🤝 Contributing and Support

### Documentation Structure
```
docs/
├── README.md                     # This file
├── api/
│   └── openapi.yaml             # OpenAPI specification
├── guides/
│   ├── quick-start.md           # Getting started guide
│   ├── configuration.md         # Configuration options
│   ├── environment-setup.md     # Environment setup
│   └── troubleshooting.md       # Troubleshooting guide
├── examples/
│   ├── integration-examples.md  # Code examples
│   ├── oran-queries.md          # O-RAN specific queries
│   └── nephio-scenarios.md      # Nephio use cases
└── deployment/
    ├── docker-guide.md          # Docker deployment
    ├── kubernetes-guide.md      # Kubernetes deployment
    └── kubernetes-manifests.yaml # K8s resources
```

### Getting Help
- 📧 **Email**: hctsai@linux.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/thc1006/oran-nephio-rag/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thc1006/oran-nephio-rag/discussions)

### Contributing
1. Check existing documentation
2. Follow the style guide
3. Test your changes
4. Submit pull requests

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](../LICENSE) file for details.

---

**Ready to get started?** 👉 [Quick Start Guide](guides/quick-start.md)

**Need specific examples?** 👉 [Integration Examples](examples/integration-examples.md)

**Deploying to production?** 👉 [Deployment Guides](deployment/)

---

*Made with ❤️ for the Telecom and Cloud Native Community*