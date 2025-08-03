# O-RAN × Nephio RAG System

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![System Status](https://img.shields.io/badge/status-functional-brightgreen.svg)](#system-status)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

An intelligent Retrieval-Augmented Generation (RAG) system specialized for O-RAN and Nephio technical documentation, enabling precise Q&A capabilities for telecommunications and cloud-native network functions.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The O-RAN × Nephio RAG System combines advanced AI capabilities with specialized knowledge retrieval to provide accurate, context-aware answers about:

- **O-RAN Architecture**: Open Radio Access Network specifications and implementations
- **Nephio Platform**: Cloud-native network automation and orchestration
- **Network Functions**: Scaling, deployment, and lifecycle management
- **5G/6G Technologies**: Next-generation mobile network infrastructure

### Key Features

- 🤖 **Intelligent Q&A**: Advanced AI-powered responses using multiple model backends
- 📚 **Official Documentation**: Automated processing of O-RAN and Nephio official sources
- 🔍 **Semantic Search**: High-precision vector-based document retrieval
- ⚡ **Multiple API Modes**: Flexible integration options (Browser automation, Mock, Local)
- 🐳 **Production Ready**: Complete Docker support with monitoring and scaling
- 📊 **Observability**: Built-in metrics, logging, and health monitoring
- 🔒 **Security First**: Secure API handling and data protection

## System Requirements

### Prerequisites

- **Python**: 3.9 or higher (tested up to 3.13)
- **Memory**: 4GB RAM minimum, 8GB+ recommended
- **Storage**: 2GB available disk space
- **Network**: Stable internet connection for document retrieval
- **Browser**: Chrome/Chromium for browser automation mode

### Operating System Support

- **Linux**: Ubuntu 20.04+, RHEL 8+, CentOS 8+
- **macOS**: 10.15+ (Catalina or later)
- **Windows**: Windows 10/11, Windows Server 2019+

## Quick Start

### Option 1: Quick Demo (Mock Mode)

Perfect for testing and evaluation without API keys:

```bash
# 1. Clone repository
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set mock mode
echo "API_MODE=mock" > .env
echo "VECTOR_DB_PATH=./oran_nephio_vectordb" >> .env

# 4. Create test database
python create_minimal_database.py

# 5. Run system
python main.py
```

### Option 2: Docker Quick Start

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose ps
curl http://localhost:8000/health
```

## Installation

### 1. Environment Setup

```bash
# Create and activate virtual environment (recommended)
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt

# Install in development mode (for contributors)
pip install -e .
```

### 3. System Verification

```bash
# Basic import test
python test_basic_imports.py

# Full system verification
python test_verification_simple.py

# System demonstration
python demo_system.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_MODE=browser                    # browser|mock|local
PUTER_MODEL=claude-sonnet-4        # AI model for browser mode

# Browser Automation Settings
BROWSER_HEADLESS=true              # Run browser in headless mode
BROWSER_TIMEOUT=120                # Browser timeout in seconds
BROWSER_WAIT_TIME=10               # Wait time between operations

# Database Configuration
VECTOR_DB_PATH=./oran_nephio_vectordb
COLLECTION_NAME=oran_nephio_official
EMBEDDINGS_CACHE_PATH=./embeddings_cache

# Text Processing
CHUNK_SIZE=1024                    # Document chunk size
CHUNK_OVERLAP=200                  # Chunk overlap size
MAX_TOKENS=4000                    # Maximum response tokens
TEMPERATURE=0.1                    # AI response temperature

# System Configuration
LOG_LEVEL=INFO                     # Logging level
LOG_FILE=logs/oran_nephio_rag.log  # Log file path
AUTO_SYNC_ENABLED=true             # Enable automatic document sync
SYNC_INTERVAL_HOURS=24             # Sync interval

# Retrieval Settings
RETRIEVER_K=6                      # Number of retrieved documents
RETRIEVER_FETCH_K=15               # Candidate documents to fetch
RETRIEVER_LAMBDA_MULT=0.7          # MMR diversity parameter

# Performance Tuning
MAX_RETRIES=3                      # Maximum retry attempts
REQUEST_TIMEOUT=30                 # HTTP request timeout
REQUEST_DELAY=1.0                  # Delay between requests

# Security
VERIFY_SSL=true                    # Verify SSL certificates
MIN_CONTENT_LENGTH=500             # Minimum content validation
```

### API Mode Configuration

#### Mock Mode (Testing)
```bash
API_MODE=mock
```
- **Pros**: No API keys required, instant setup
- **Cons**: Pre-defined responses only
- **Use Case**: Development, testing, demonstrations

#### Browser Mode (Production)
```bash
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
```
- **Pros**: Access to latest AI models via browser automation
- **Cons**: Requires browser setup
- **Use Case**: Production deployments, full AI capabilities

#### Local Mode (Offline)
```bash
API_MODE=local
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama2
```
- **Pros**: Complete offline operation
- **Cons**: Requires local model setup (Ollama)
- **Use Case**: Air-gapped environments, privacy-sensitive deployments

## Usage

### Command Line Interface

Start the interactive CLI:

```bash
python main.py
```

Available commands:
- `help` - Show available commands
- `status` - Display system status
- `update` - Update vector database
- `examples` - Show example questions
- `clear` - Clear screen
- `quit` - Exit application

### Python API

```python
from src import create_rag_system, quick_query

# Quick query
answer = quick_query("What is Nephio?")
print(answer)

# Full API usage
rag = create_rag_system()
rag.load_existing_database()
rag.setup_qa_chain()

result = rag.query("How does O-RAN support network function scaling?")
print("Answer:", result["answer"])
print("Sources:", result["sources"])
print("Query time:", result["query_time"], "seconds")
```

### Example Questions

- "What is the O-RAN architecture?"
- "How does Nephio support network function lifecycle management?"
- "What is O2IMS and its role in O-RAN?"
- "How to implement scale-out for DU functions?"
- "What are the key components of Nephio automation?"
- "How does Free5GC integrate with Nephio?"

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/ -m "unit"          # Unit tests only
pytest tests/ -m "integration"   # Integration tests only
pytest tests/ -m "not slow"      # Skip slow tests

# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### System Tests

```bash
# Basic functionality
python test_basic_imports.py

# API mode testing
python test_api_modes_simple.py

# End-to-end testing
python test_final_system.py

# Database building
python test_build_database.py
```

### Test Coverage

Current test coverage includes:
- Configuration validation
- Document loading and processing
- Vector database operations
- Query processing
- API adapter functionality
- Error handling and recovery

## Deployment

### Development Environment

```bash
# Docker development setup
docker-compose -f docker-compose.dev.yml up -d

# Manual development setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
python main.py
```

### Production Environment

```bash
# Docker production deployment
docker-compose -f docker-compose.prod.yml up -d

# With monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

### Cloud Deployment

#### AWS ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
docker build -t oran-rag .
docker tag oran-rag:latest <account>.dkr.ecr.us-west-2.amazonaws.com/oran-rag:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/oran-rag:latest
```

#### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/oran-rag
gcloud run deploy --image gcr.io/PROJECT-ID/oran-rag --platform managed
```

#### Azure Container Instances
```bash
az container create --resource-group myResourceGroup --name oran-rag \
  --image your-registry/oran-rag:latest --environment-variables API_MODE=browser
```

## Architecture

### System Overview

```
┌─────────────────┐
│   User Layer    │  CLI, Web UI, REST API
├─────────────────┤
│ Application     │  RAG Engine, Query Processor, Document Loader
├─────────────────┤
│ AI Services     │  Multiple LLM Backends, Embeddings, Vector Search
├─────────────────┤
│ Data Layer      │  Vector DB, Document Cache, Configuration Store
├─────────────────┤
│ Infrastructure  │  Logging, Metrics, Health Checks, Monitoring
└─────────────────┘
```

### Core Components

```
src/
├── __init__.py              # Package exports and initialization
├── config.py                # Configuration management with Pydantic
├── oran_nephio_rag.py       # Main RAG system implementation
├── document_loader.py       # Document fetching and processing
├── api_adapters.py          # LLM API abstraction layer
├── async_rag_system.py      # Async RAG implementation
├── monitoring.py            # Observability and metrics
└── simple_monitoring.py     # Basic monitoring utilities
```

### Data Flow

1. **Document Ingestion**: Fetch from official O-RAN/Nephio sources
2. **Text Processing**: Clean, chunk, and validate content
3. **Vector Generation**: Create embeddings using sentence transformers
4. **Storage**: Persist in ChromaDB with metadata
5. **Query Processing**: Semantic search + LLM generation
6. **Response**: Formatted answer with source citations

## Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
isort src/ tests/

# Run code quality checks
flake8 src/ tests/
mypy src/
bandit -r src/
```

### Code Quality Standards

- **Formatting**: Black (120 character line length)
- **Import Sorting**: isort with Black profile
- **Type Checking**: MyPy (optional strict mode)
- **Linting**: Flake8 with security checks
- **Testing**: pytest with >90% coverage target

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

#### 1. Installation Problems

```bash
# Issue: Dependency conflicts
# Solution: Use virtual environment
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Issue: Compilation errors
# Solution: Use binary packages
pip install --only-binary=all -r requirements.txt
```

#### 2. Runtime Errors

```bash
# Issue: Module import errors
# Solution: Install in development mode
pip install -e .

# Issue: Vector database empty
# Solution: Create test database
python create_minimal_database.py

# Issue: Browser automation fails
# Solution: Install Chrome and update WebDriver
sudo apt-get install google-chrome-stable
pip install --upgrade webdriver-manager
```

#### 3. Performance Issues

```bash
# Issue: High memory usage
# Solution: Reduce chunk size
echo "CHUNK_SIZE=512" >> .env

# Issue: Slow queries
# Solution: Adjust retrieval parameters
echo "RETRIEVER_K=3" >> .env
echo "RETRIEVER_FETCH_K=10" >> .env
```

### Diagnostic Commands

```bash
# Check system status
python -c "
from src import create_rag_system
rag = create_rag_system()
status = rag.get_system_status()
print('Vector DB Ready:', status.get('vectordb_ready'))
print('QA Chain Ready:', status.get('qa_chain_ready'))
"

# View logs
tail -f logs/oran_nephio_rag.log

# Docker diagnostics
docker-compose ps
docker-compose logs -f oran-rag-app
```

### Getting Help

- 📧 **Email Support**: hctsai@linux.com
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/thc1006/oran-nephio-rag/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thc1006/oran-nephio-rag/discussions)
- 📖 **Documentation**: [Complete Guide](docs/)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **LangChain**: MIT License
- **ChromaDB**: Apache 2.0
- **FastAPI**: MIT License
- **Pydantic**: MIT License

## Acknowledgments

- [Nephio Project](https://nephio.org/) - Network automation platform
- [O-RAN Alliance](https://www.o-ran.org/) - Open RAN specifications
- [LangChain](https://langchain.com/) - LLM application framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Anthropic](https://www.anthropic.com/) - Claude AI models

## Project Metrics

- **Lines of Code**: ~15,000
- **Test Coverage**: >85%
- **Documentation Coverage**: 100%
- **Supported Platforms**: Linux, macOS, Windows
- **Container Ready**: ✅
- **Production Tested**: ✅

---

**Made with ❤️ for the Telecom and Cloud Native Community**

*Empowering the future of O-RAN and cloud-native network functions through intelligent automation and AI-driven insights.*