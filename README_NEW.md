# O-RAN × Nephio RAG System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

An intelligent Retrieval-Augmented Generation (RAG) system specialized for O-RAN and Nephio technical documentation, providing accurate answers to telecommunications and cloud-native networking questions.

## ⚠️ IMPORTANT: LLM Integration Constraint

This system **must** integrate with Anthropic Claude exclusively through the [Puter.js browser API](https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/). Direct Anthropic API usage is not permitted.

## 🎯 Key Features

- **Intelligent Q&A**: Claude AI-powered responses using official O-RAN and Nephio documentation
- **Semantic Search**: Vector-based document retrieval with ChromaDB
- **Browser-Based LLM**: Integration via Puter.js for free Claude access
- **Async Processing**: High-performance concurrent operations
- **Production Monitoring**: OpenTelemetry, Prometheus, and Grafana integration
- **Containerized Deployment**: Multi-stage Docker builds with development/production configurations

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows 10/11
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection for document fetching

### Required Dependencies
- Python 3.9+ with pip
- Docker and Docker Compose (for containerized deployment)
- Git (if cloning from repository)
- Web browser with JavaScript support (for Puter.js integration)

### Build Tools (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools or use pre-compiled packages
```

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <your-repository-url>
cd oran-nephio-rag

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access the application
docker-compose exec oran-rag-app python main.py
```

### Option 2: Local Installation

```bash
# 1. Clone and setup
git clone <your-repository-url>
cd oran-nephio-rag

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies (use binary packages to avoid compilation)
pip install --upgrade pip
pip install --only-binary=all -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env file with your settings (see Configuration section)

# 6. Initialize the system
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.build_vector_database()
print('✅ System initialized successfully')
"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

**Required Settings:**
```bash
# API Configuration - MUST use Puter.js integration
API_MODE=puter
PUTER_RISK_ACKNOWLEDGED=true
PUTER_MODEL=claude-sonnet-4

# Vector Database
VECTOR_DB_PATH=./oran_nephio_vectordb
COLLECTION_NAME=oran_nephio_official

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/oran_nephio_rag.log
```

**Optional Settings:**
```bash
# Text Processing
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
MAX_RETRIES=3
REQUEST_TIMEOUT=30

# Document Synchronization
AUTO_SYNC_ENABLED=true
SYNC_INTERVAL_HOURS=24

# Retrieval Configuration
RETRIEVER_K=6
RETRIEVER_FETCH_K=15
RETRIEVER_LAMBDA_MULT=0.7
```

### Puter.js Browser Integration

Since this system uses Puter.js for Claude integration, you'll need to set up the browser component:

1. **Create an HTML interface** (if not using CLI):
```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://js.puter.com/v2/"></script>
</head>
<body>
    <script>
        async function queryRAG(question) {
            const response = await puter.ai.chat(question, {
                model: 'claude-sonnet-4'
            });
            return response.message.content[0].text;
        }
    </script>
</body>
</html>
```

2. **For Python integration**, the system will use browser automation to interface with Puter.js.

## 💻 Usage Examples

### Command Line Interface

```bash
# Start interactive CLI
python main.py

# Available commands:
# - help: Show available commands
# - status: Display system status
# - update: Refresh document database
# - examples: Show sample questions
# - clear: Clear screen
# - quit/exit: Close application
```

### Python API

```python
from src import create_rag_system, quick_query

# Quick query (simplest method)
answer = quick_query("How does Nephio integrate with O-RAN?")
print(answer)

# Full API usage
rag = create_rag_system()
rag.load_existing_database()
rag.setup_qa_chain()

result = rag.query("What is the role of SMO in O-RAN architecture?")
print("Answer:", result["answer"])
print("Sources:", result["sources"])
```

### Async Usage (High Performance)

```python
import asyncio
from src import async_rag_system

async def main():
    async with async_rag_system() as rag:
        # Single query
        result = await rag.query_async("Explain Nephio package specialization")
        
        # Batch queries
        questions = [
            "What is O-CU in O-RAN?",
            "How does Nephio handle network functions?",
            "What are the benefits of O-RAN disaggregation?"
        ]
        results = await rag.batch_query_async(questions)
        
        for i, result in enumerate(results):
            print(f"Q{i+1}: {result['answer'][:100]}...")

asyncio.run(main())
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start development stack
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### Production Environment

```bash
# Set production environment variables
export ANTHROPIC_API_KEY="your-key-here"
export SECRET_KEY="your-secret-key"
export REDIS_PASSWORD="your-redis-password"

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Scale application
docker-compose -f docker-compose.prod.yml up -d --scale oran-rag-app=3
```

### Monitoring Stack

```bash
# Start with monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access monitoring dashboards:
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Jaeger: http://localhost:16686
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest

# Run specific test categories
pytest tests/ -m "unit"           # Unit tests only
pytest tests/ -m "integration"    # Integration tests only
pytest tests/ -m "not slow"       # Skip slow tests

# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Suite Categories

- **Unit Tests**: Fast tests for individual components
- **Integration Tests**: End-to-end system functionality
- **API Tests**: LLM integration and response validation
- **Docker Tests**: Container build and deployment validation

## 🔧 Troubleshooting

### Common Issues

#### 1. Installation Failures

**Problem**: `pip install -r requirements.txt` fails with compilation errors

**Solutions**:
```bash
# Option A: Use binary packages only
pip install --only-binary=all -r requirements.txt

# Option B: Install build tools (Linux)
sudo apt-get install build-essential python3-dev

# Option C: Use conda for problematic packages
conda install numpy scipy
pip install -r requirements.txt
```

#### 2. Import Errors

**Problem**: `ModuleNotFoundError` when importing from `src`

**Solutions**:
```bash
# Option A: Install in development mode
pip install -e .

# Option B: Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Option C: Use absolute imports
python -c "import sys; sys.path.insert(0, './src'); from config import Config"
```

#### 3. Docker Issues

**Problem**: Docker Compose warnings about missing environment variables

**Solution**:
```bash
# Create complete .env file
cp .env.example .env

# Add missing production variables
echo "REDIS_PASSWORD=your-redis-password" >> .env
echo "SECRET_KEY=your-secret-key" >> .env
echo "GRAFANA_PASSWORD=admin-password" >> .env
```

#### 4. Puter.js Integration Issues

**Problem**: Puter.js API calls fail or return errors

**Solutions**:
1. Verify `PUTER_RISK_ACKNOWLEDGED=true` in `.env`
2. Check internet connectivity
3. Ensure browser automation is properly configured
4. Try different Claude models: `claude-sonnet-4`, `claude-opus-4`

### Getting Help

1. **Check Logs**: 
   ```bash
   tail -f logs/oran_nephio_rag.log
   docker-compose logs oran-rag-app
   ```

2. **Validate Configuration**:
   ```bash
   python -c "from src.config import validate_config; validate_config()"
   ```

3. **System Status**:
   ```bash
   python main.py
   # Then type: status
   ```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <your-repository-url>
cd oran-nephio-rag

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code quality checks
black src/ tests/           # Format code
flake8 src/ tests/          # Lint code
mypy src/                   # Type checking
pytest                      # Run tests
```

### Code Standards

- **Formatting**: Black with 120-character line length
- **Linting**: Flake8 with project-specific rules
- **Type Hints**: Required for all public functions
- **Testing**: Minimum 90% code coverage
- **Documentation**: Docstrings for all modules and classes

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Run code quality checks: `pre-commit run --all-files`
6. Commit with descriptive message: `git commit -m "feat: add new feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Tsai, Hsiu-Chi (thc1006)**
- Email: hctsai@linux.com
- Issues: Please report via email

## 🙏 Acknowledgments

- [Nephio Project](https://nephio.org/) - Network automation platform
- [O-RAN Alliance](https://www.o-ran.org/) - Open RAN standards
- [Puter.js](https://puter.com/) - Browser-based Claude API access
- [LangChain](https://langchain.com/) - LLM application framework

---

**Made with ❤️ for the Telecom and Cloud Native Community**