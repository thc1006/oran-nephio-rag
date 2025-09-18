# O-RAN × Nephio RAG API - Quick Start Guide

This guide will get you up and running with the O-RAN × Nephio RAG API in just a few minutes.

## Prerequisites

- **Python 3.9+** installed on your system
- **4GB RAM** minimum (8GB+ recommended)
- **2GB disk space** available
- **Internet connection** for document retrieval
- **Chrome/Chromium browser** (for browser automation mode)

## 1. Installation

### Option A: Quick Demo (Mock Mode)

Perfect for testing and evaluation without API keys:

```bash
# Clone the repository
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag

# Install dependencies
pip install -r requirements.txt

# Set up environment for mock mode
echo "API_MODE=mock" > .env
echo "VECTOR_DB_PATH=./oran_nephio_vectordb" >> .env

# Create test database
python create_minimal_database.py

# Start the API server
python -m src.api.main
```

### Option B: Full Production Setup (Browser Mode)

For production deployments with full AI capabilities:

```bash
# Clone and install
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag
pip install -r requirements.txt

# Configure for browser automation
cat > .env << EOF
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=120
VECTOR_DB_PATH=./oran_nephio_vectordb
COLLECTION_NAME=oran_nephio_official
EOF

# Build the vector database
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.build_database()
"

# Start the API server
python -m src.api.main
```

### Option C: Docker Setup

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d

# Check status
curl http://localhost:8000/health
```

## 2. Verify Installation

Test your installation with these commands:

```bash
# Check system health
curl http://localhost:8000/health

# Check API root
curl http://localhost:8000/

# Test a simple query (mock mode)
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the O-RAN architecture?",
    "k": 5,
    "include_sources": true
  }'
```

## 3. Basic Usage Examples

### Query the RAG System

```bash
# Basic O-RAN question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the O-RAN architecture?",
    "k": 5,
    "include_sources": true
  }'

# Nephio deployment question
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does Nephio handle network function scaling?",
    "k": 8,
    "context_length": 6000
  }'

# Advanced configuration query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to configure O2IMS integration with Nephio?",
    "k": 10,
    "model": "claude-sonnet-4",
    "include_sources": true
  }'
```

### Search Documents

```bash
# Search for specific topics
curl -X POST http://localhost:8000/api/v1/query/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "network function scaling",
    "k": 10,
    "score_threshold": 0.7
  }'

# Filter by source type
curl -X POST http://localhost:8000/api/v1/query/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Nephio deployment",
    "k": 15,
    "source_types": ["nephio"],
    "score_threshold": 0.8
  }'
```

### System Status

```bash
# Get system status
curl http://localhost:8000/api/v1/system/status

# Get configuration
curl http://localhost:8000/api/v1/system/config

# Get metrics
curl http://localhost:8000/api/v1/system/metrics
```

## 4. Python Client Example

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def query_rag(question, k=5, include_sources=True):
    """Query the RAG system"""
    url = f"{BASE_URL}/api/v1/query"
    payload = {
        "query": question,
        "k": k,
        "include_sources": include_sources
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def search_documents(query, k=10, source_types=None):
    """Search documents"""
    url = f"{BASE_URL}/api/v1/query/search"
    payload = {
        "query": query,
        "k": k
    }
    if source_types:
        payload["source_types"] = source_types

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    # Test basic query
    try:
        result = query_rag("What is the O-RAN architecture?")
        print("Answer:", result["answer"])
        print("Query time:", result["query_time"], "seconds")
        print("Sources:", len(result["sources"]))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Test search
    try:
        results = search_documents("Nephio", source_types=["nephio"])
        print(f"Found {results['total_found']} documents")
        for doc in results["results"][:3]:
            print(f"- {doc['metadata'].get('title', 'Unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
```

## 5. Configuration Options

### Environment Variables

Create or modify your `.env` file with these key settings:

```bash
# API Configuration
API_MODE=browser                    # browser|mock
PUTER_MODEL=claude-sonnet-4        # AI model for browser mode

# Browser Settings
BROWSER_HEADLESS=true              # Run browser in headless mode
BROWSER_TIMEOUT=120                # Browser timeout in seconds
BROWSER_WAIT_TIME=10               # Wait time between operations

# Database Configuration
VECTOR_DB_PATH=./oran_nephio_vectordb
COLLECTION_NAME=oran_nephio_official
EMBEDDINGS_CACHE_PATH=./embeddings_cache

# Performance Tuning
CHUNK_SIZE=1024                    # Document chunk size
CHUNK_OVERLAP=200                  # Chunk overlap size
MAX_TOKENS=4000                    # Maximum response tokens
TEMPERATURE=0.1                    # AI response temperature

# Retrieval Settings
RETRIEVER_K=6                      # Number of retrieved documents
RETRIEVER_FETCH_K=15               # Candidate documents to fetch
RETRIEVER_LAMBDA_MULT=0.7          # MMR diversity parameter

# System Configuration
LOG_LEVEL=INFO                     # Logging level
AUTO_SYNC_ENABLED=true             # Enable automatic document sync
SYNC_INTERVAL_HOURS=24             # Sync interval
```

### API Modes

#### Mock Mode (Testing)
- **Use case**: Development, testing, demonstrations
- **Setup**: `API_MODE=mock`
- **Pros**: No API keys required, instant setup
- **Cons**: Pre-defined responses only

#### Browser Mode (Production)
- **Use case**: Production deployments, full AI capabilities
- **Setup**: `API_MODE=browser` + `PUTER_MODEL=claude-sonnet-4`
- **Pros**: Access to latest AI models
- **Cons**: Requires browser setup

## 6. Common O-RAN and Nephio Queries

Try these example queries to explore the system capabilities:

### O-RAN Architecture Questions
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main components of O-RAN architecture?"}'

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does O-RAN support network slicing?"}'

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the role of O-DU and O-CU in O-RAN?"}'
```

### Nephio Platform Questions
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does Nephio automate network function lifecycle management?"}'

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Nephio package specialization process?"}'

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to deploy Free5GC with Nephio?"}'
```

### O2IMS Integration Questions
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is O2IMS and its role in O-RAN?"}'

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to configure O2IMS integration with Nephio?"}'
```

## 7. Troubleshooting

### Common Issues

#### 1. Service Unavailable (503)
```bash
# Check if RAG system is ready
curl http://localhost:8000/health

# Check logs
tail -f logs/oran_nephio_rag.log

# Reinitialize system if needed
curl -X POST http://localhost:8000/api/v1/documents/refresh
```

#### 2. Empty or Poor Responses
```bash
# Check if vector database exists
ls -la ./oran_nephio_vectordb/

# Rebuild database if empty
python create_minimal_database.py

# Or build from official sources (browser mode)
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.build_database()
"
```

#### 3. Browser Automation Issues (Browser Mode)
```bash
# Check Chrome installation
google-chrome --version

# Update WebDriver
pip install --upgrade webdriver-manager

# Try headless mode
echo "BROWSER_HEADLESS=true" >> .env
```

#### 4. Performance Issues
```bash
# Reduce chunk size for lower memory usage
echo "CHUNK_SIZE=512" >> .env

# Reduce retrieval documents
echo "RETRIEVER_K=3" >> .env

# Monitor memory usage
curl http://localhost:8000/api/v1/system/metrics
```

## 8. Next Steps

1. **Explore the API Documentation**: Visit `/docs` for interactive Swagger UI
2. **Set up Authentication**: Configure API keys for production use
3. **Monitor Performance**: Set up metrics collection and monitoring
4. **Customize Sources**: Add your own documentation sources
5. **Scale Deployment**: Use Docker Compose or Kubernetes for production

## 9. Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Health Status**: http://localhost:8000/health
- **GitHub Issues**: https://github.com/thc1006/oran-nephio-rag/issues
- **Email Support**: hctsai@linux.com

## 10. API Reference Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root information |
| `/health` | GET | Health check |
| `/api/v1/query` | POST | Query RAG system |
| `/api/v1/query/search` | POST | Search documents |
| `/api/v1/query/bulk` | POST | Bulk query processing |
| `/api/v1/documents` | GET/POST | List/add documents |
| `/api/v1/documents/{id}` | GET/PUT/DELETE | Manage specific document |
| `/api/v1/documents/refresh` | POST | Refresh vector database |
| `/api/v1/system/status` | GET | System status |
| `/api/v1/system/config` | GET | System configuration |
| `/api/v1/system/metrics` | GET | Performance metrics |
| `/metrics` | GET | Prometheus metrics |

Happy querying! 🚀