# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/ -m "unit"          # Unit tests only
pytest tests/ -m "integration"   # Integration tests only
pytest tests/ -m "not slow"      # Skip slow tests

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run parallel tests
pytest -n auto

# Run with timeout
pytest --timeout=300
```

### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Security check
bandit -r src/

# Run all quality checks
pre-commit run --all-files
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Setup pre-commit hooks
pre-commit install
```

### Docker Operations
```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d

# Production environment  
docker-compose -f docker-compose.prod.yml up -d

# With monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Build and run
docker build -t oran-rag .
docker run -p 8000:8000 oran-rag
```

### System Testing & CLI Commands
```bash
# Test system components
python scripts/test_system.py
oran-rag-test  # Alternative command via pyproject.toml

# Verify installation
python test_verification.py
python test_verification_simple.py

# API mode testing
python test_api_modes.py
python test_api_modes_simple.py

# Puter.js integration testing (experimental)
python test_puter_integration.py
python test_puter_quick.py

# System repair/fix verification
python test_fixed_system.py

# Auto-sync documents
python scripts/auto_sync.py
oran-rag-sync  # Alternative command via pyproject.toml

# Main CLI application
python main.py
oran-rag       # Alternative command via pyproject.toml
```

### Build & Installation Commands
```bash
# Install in development mode
pip install -e .

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Fix dependencies issues
python fix_dependencies.py

# Install dependencies with verification
python install_dependencies.py

# Build package
python -m build

# Install from built package
pip install dist/oran-nephio-rag-*.whl
```

### Common Build/Test Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: sentence-transformers` | Missing ML dependencies | `pip install sentence-transformers>=2.2.2` |
| `ImportError: langchain_huggingface` | Missing LangChain HF integration | `pip install langchain-huggingface` |
| `AttributeError: 'NoneType' ANTHROPIC_API_KEY` | Missing API key | Set `ANTHROPIC_API_KEY` in `.env` file |
| `ChromaDB persistence error` | Vector DB path issues | Check `VECTOR_DB_PATH` permissions & disk space |
| `pytest collection failed` | Import path issues | Run `pip install -e .` first |
| `Docker build fails` | Context or dependency issues | Check `docker/TROUBLESHOOTING.md` |
| `Pre-commit hook failures` | Code quality issues | Run `pre-commit run --all-files` to see details |
| `Memory errors during testing` | Insufficient RAM | Use `pytest -m "not slow"` or increase system memory |

## Project Structure (Monorepo Layout)

```
oran-nephio-rag/
├── 📁 src/                          # Core application modules
│   ├── __init__.py                  # Package initialization & exports
│   ├── config.py                    # Configuration management (Pydantic)
│   ├── document_loader.py           # Document fetching & processing
│   ├── oran_nephio_rag.py          # Main RAG system (sync)
│   ├── async_rag_system.py         # Async RAG implementation
│   ├── api_adapters.py             # LLM API abstraction layer
│   ├── monitoring.py               # OpenTelemetry observability
│   └── simple_monitoring.py        # Basic monitoring utilities
│
├── 📁 tests/                        # Test suite
│   ├── conftest.py                  # pytest fixtures & configuration
│   ├── test_*.py                    # Unit tests for each module
│   └── test_integration_comprehensive.py # E2E integration tests
│
├── 📁 scripts/                      # Automation & utility scripts
│   ├── auto_sync.py                 # Auto document synchronization
│   └── test_system.py               # System verification script
│
├── 📁 examples/                     # Usage examples & demos
│   ├── example_usage.py             # Basic usage demonstration
│   └── __init__.py
│
├── 📁 docker/                       # Docker deployment configs
│   ├── config/                      # Environment configurations
│   ├── scripts/                     # Deployment automation
│   ├── monitoring/                  # Docker monitoring setup
│   └── TROUBLESHOOTING.md          # Docker-specific troubleshooting
│
├── 📁 monitoring/                   # Observability configurations
│   ├── prometheus.yml               # Prometheus configuration
│   ├── grafana-*.json              # Grafana dashboard definitions
│   ├── alert_rules.yml             # Alerting rules
│   └── otel-collector-config.yml   # OpenTelemetry collector config
│
├── 📁 docs/                         # Documentation
│   ├── SETUP.md                     # Setup instructions
│   └── DOCKER_DEPLOYMENT.md        # Docker deployment guide
│
├── 📁 _pages/                       # Jekyll/GitHub Pages content
├── 📁 _includes/ & _layouts/        # Jekyll templates
├── 📁 assets/                       # Static web assets
│
├── 🚀 Entry Points
│   ├── main.py                      # CLI application entry point
│   ├── test_*.py                    # Various system tests
│   └── utils.py                     # Shared utilities
│
├── 📦 Configuration Files
│   ├── pyproject.toml               # Project metadata & dependencies
│   ├── requirements*.txt            # Python dependencies
│   ├── docker-compose.*.yml         # Multi-service deployment
│   ├── .pre-commit-config.yaml      # Code quality automation
│   └── Dockerfile*                  # Container definitions
│
└── 📄 Documentation & Reports
    ├── README.md                    # Main project documentation
    ├── API_MODES_GUIDE.md          # API integration guide
    ├── DEPLOYMENT.md               # Deployment instructions
    ├── FIX_REPORT.md               # System fix documentation
    ├── QUICK_FIX_GUIDE.md          # Troubleshooting guide
    └── EXPERIMENTAL_*.md           # Experimental features docs
```

### Module Overview

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `src/oran_nephio_rag.py` | Core RAG system | `ORANNephioRAG`, `VectorDatabaseManager`, `QueryProcessor` |
| `src/async_rag_system.py` | High-performance async RAG | `AsyncORANNephioRAG`, `AsyncDocumentLoader` |
| `src/document_loader.py` | Document processing | `DocumentLoader`, `DocumentContentCleaner` |
| `src/config.py` | Configuration management | `Config`, `DocumentSource`, `validate_config` |
| `src/api_adapters.py` | LLM API abstraction | `LLMManager`, API failover logic |
| `src/monitoring.py` | Observability | `RAGSystemMetrics`, `HealthChecker`, `AlertManager` |

## Architecture Overview

### Core System Design
This is a RAG (Retrieval-Augmented Generation) system specialized for O-RAN and Nephio documentation. The architecture follows a modular design with clear separation of concerns:

**Main Components:**
- `src/oran_nephio_rag.py` - Core RAG system with sync operations
- `src/async_rag_system.py` - Async RAG system for high-performance scenarios  
- `src/document_loader.py` - Document fetching and processing
- `src/config.py` - Configuration management with Pydantic models
- `src/monitoring.py` - Observability with OpenTelemetry support

### Data Flow
1. **Document Ingestion**: DocumentLoader fetches O-RAN/Nephio docs from official sources
2. **Processing**: Text is chunked using RecursiveCharacterTextSplitter (default 1024 chunks)
3. **Vectorization**: HuggingFaceEmbeddings creates vector representations
4. **Storage**: ChromaDB stores vectors with metadata
5. **Retrieval**: Semantic search finds relevant context
6. **Generation**: Claude AI (Anthropic) generates responses with retrieved context

### Key Design Patterns
- **Factory Pattern**: `create_rag_system()` and `async_rag_system()` context managers
- **Adapter Pattern**: `api_adapters.py` provides unified LLM interface
- **Observer Pattern**: Monitoring system tracks metrics across components
- **Context Manager Pattern**: Async components use proper resource management

### Async Architecture
The async system (`AsyncORANNephioRAG`) supports:
- Concurrent document processing with semaphore-based rate limiting
- Batch query processing with configurable concurrency
- Optional uvloop integration for performance
- Proper async context management for resources

## Configuration

### Environment Variables
Required:
- `ANTHROPIC_API_KEY` - Claude AI API key

Optional but important:
- `VECTOR_DB_PATH` - Vector database location (default: `./oran_nephio_vectordb`)
- `CLAUDE_MODEL` - Model name (default: `claude-3-sonnet-20240229`)
- `CLAUDE_TEMPERATURE` - Generation temperature (default: `0.1`)
- `CHUNK_SIZE` - Text chunk size (default: `1024`)
- `LOG_LEVEL` - Logging level (default: `INFO`)

### Configuration Files
- `pyproject.toml` - Project metadata, dependencies, and tool configurations
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- Docker environment files in `docker/config/`

## Testing Strategy

### Test Structure
- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_*.py` - Unit tests for individual components
- `tests/test_integration_comprehensive.py` - Full system integration tests
- Root-level `test_*.py` files - System verification and API mode tests

### Test Markers
- `unit` - Fast unit tests
- `integration` - Slower integration tests  
- `slow` - Resource-intensive tests

### Mock Strategy
Uses `pytest-mock` and `responses` for HTTP mocking. Key fixtures mock external dependencies like Anthropic API and document sources.

## Monitoring and Observability

The system includes comprehensive monitoring:
- **Metrics**: Prometheus-compatible metrics via `prometheus-client`
- **Tracing**: OpenTelemetry distributed tracing
- **Health Checks**: Built-in health check endpoints
- **Dashboards**: Grafana dashboards in `monitoring/` directory

Monitor endpoints when running:
- Health: `/health`
- Metrics: `/metrics` 
- Status: `/status`

## Development Notes

### Code Style
- Uses Black formatter with 120 character line length
- isort for import organization with Black profile
- MyPy for type checking (not strict mode)
- Flake8 for additional linting

### API Integration
The system supports multiple API modes through `api_adapters.py`:
- Direct Anthropic integration (primary)
- Fallback mechanisms for different model endpoints
- Configurable model parameters and retry logic

### Experimental Features
- `EXPERIMENTAL_PUTER_INTEGRATION.md` documents Puter.js API integration
- Experimental branch contains additional API integration work

### Docker Deployment
Three deployment modes:
- Development: Basic setup with hot reloading
- Production: Optimized with nginx reverse proxy
- Monitoring: Full observability stack with Prometheus, Grafana, Jaeger

The production deployment includes:
- Multi-stage Docker builds
- Nginx load balancing and SSL
- Persistent volume mounts for vector database
- Health checks and restart policies

## Git Workflow

### Branch Naming Convention
```bash
# Feature branches
feature/description-of-feature
feature/add-vector-database-optimization

# Bug fixes
bugfix/issue-description
bugfix/fix-anthropic-api-timeout

# Experimental features
experimental/feature-name
experimental/puter-api-integration

# Hotfixes
hotfix/critical-issue-description

# Documentation updates
docs/update-description
docs/add-deployment-guide
```

### Commit Message Standards
The project uses **Conventional Commits** with emoji prefixes:

```bash
# Format: <emoji> <type>: <description>
🚀 feat: add new vector database optimization
🐛 fix: resolve Anthropic API timeout issues
📝 docs: update installation guide
🧪 experimental: implement Puter.js API integration
♻️ refactor: restructure document loader module
🔧 chore: update dependencies to latest versions
🎨 style: format code with black
✅ test: add integration tests for async RAG system
🔥 remove: delete deprecated monitoring code
⚡ perf: improve query response time by 40%
```

### Development Workflow

#### 1. Starting New Work
```bash
# Create and checkout new branch
git checkout -b feature/your-feature-name

# Make sure you're up to date
git pull origin main  # or appropriate base branch
```

#### 2. Development Process
```bash
# Make changes and commit frequently
git add .
git commit -m "🚀 feat: implement core functionality"

# Push to remote regularly
git push -u origin feature/your-feature-name
```

#### 3. Code Quality (Pre-commit)
```bash
# Install pre-commit hooks (one time)
pre-commit install

# Pre-commit will automatically run on commits
# To run manually:
pre-commit run --all-files
```

#### 4. Before Merging
```bash
# Update your branch with latest main
git fetch origin
git rebase origin/main  # Preferred for clean history
# OR
git merge origin/main   # Alternative if rebase conflicts are complex

# Push updated branch
git push --force-with-lease origin feature/your-feature-name
```

### Merge vs Rebase Policy

**Recommended: Rebase for feature branches, merge for integration**

```bash
# For feature branches (clean linear history)
git rebase origin/main
git push --force-with-lease

# For merging completed features (preserve context)
git checkout main
git merge --no-ff feature/your-feature-name
git push origin main
```

**When to use each:**
- **Rebase**: Feature branches, small changes, maintaining clean history
- **Merge**: Integration branches, collaborative features, preserving branch context

### Release Workflow
```bash
# Current active branch
experimental/puter-api-integration  # Active development

# Recommended branch structure for releases:
main                    # Stable production code
develop                 # Integration branch (if needed)
feature/*              # New features
bugfix/*               # Bug fixes
hotfix/*               # Critical production fixes
experimental/*         # Experimental features
```

## Technical Debt & TODOs

Based on project analysis, here are identified improvement areas:

### 📋 System Architecture
- [ ] **Async/Sync Integration**: Unify async and sync RAG implementations into single coherent API
- [ ] **API Adapter Refactoring**: Consolidate multiple API integration patterns in `api_adapters.py`
- [ ] **Configuration Management**: Centralize all environment-specific configs (currently scattered across docker/, src/, root)
- [ ] **Error Handling**: Implement consistent error handling patterns across all modules

### 🔧 Code Quality
- [ ] **Type Annotations**: Complete type hints for all modules (currently partial in some files)
- [ ] **Documentation Coverage**: Add comprehensive docstrings to all public methods
- [ ] **Test Coverage**: Increase test coverage from current ~75% to >90%
- [ ] **Code Duplication**: Refactor duplicate monitoring logic between `monitoring.py` and `simple_monitoring.py`

### 🚀 Performance & Scalability  
- [ ] **Vector Database Optimization**: Implement connection pooling for ChromaDB
- [ ] **Caching Strategy**: Add Redis/memory caching for frequent queries
- [ ] **Batch Processing**: Optimize document ingestion for large document sets
- [ ] **Resource Management**: Implement proper cleanup for async contexts

### 🐳 Infrastructure & Deployment
- [ ] **Multi-stage Docker Optimization**: Reduce final image size (currently ~2GB)
- [ ] **Health Check Improvements**: Add detailed component-level health checks
- [ ] **Monitoring Dashboard**: Complete Grafana dashboard configuration
- [ ] **SSL/TLS Configuration**: Implement proper certificate management for production

### 🧪 Experimental Features
- [ ] **Puter.js Integration**: Complete experimental API integration (currently in progress)
- [ ] **Multi-language Support**: Extend beyond current Chinese/English documentation
- [ ] **Plugin Architecture**: Design extensible plugin system for custom document sources
- [ ] **Real-time Updates**: Implement document change detection and auto-sync

### 📊 Monitoring & Observability
- [ ] **Distributed Tracing**: Complete OpenTelemetry implementation across all services
- [ ] **Log Aggregation**: Implement structured logging with ELK stack integration
- [ ] **Performance Metrics**: Add business-level metrics (query accuracy, user satisfaction)
- [ ] **Alert Tuning**: Fine-tune alert thresholds based on production usage patterns

### 🔐 Security & Compliance
- [ ] **API Key Rotation**: Implement automatic API key rotation mechanism
- [ ] **Input Validation**: Add comprehensive input sanitization for all endpoints
- [ ] **Audit Logging**: Implement audit trail for all system interactions
- [ ] **Dependency Scanning**: Automate security vulnerability scanning in CI/CD