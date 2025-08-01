# Project Structure

## Directory Organization

### Root Level
```
oran-nephio-rag/
├── main.py                      # Main application entry point
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pyproject.toml              # Project configuration and build settings
├── .env.example                # Environment variables template
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.*.yml        # Docker Compose configurations
└── README.md                   # Project documentation (Chinese)
```

### Source Code (`src/`)
Core application modules following clean architecture principles:

```
src/
├── __init__.py                 # Package initialization with public API
├── config.py                   # Configuration management and validation
├── oran_nephio_rag.py         # Main RAG system implementation
├── async_rag_system.py        # Async RAG system for high concurrency
├── document_loader.py         # Document fetching and processing
├── api_adapters.py            # LLM API abstraction layer
├── monitoring.py              # OpenTelemetry monitoring integration
└── simple_monitoring.py       # Basic monitoring utilities
```

### Testing (`tests/`)
Comprehensive test suite with fixtures and utilities:

```
tests/
├── conftest.py                 # Shared test configuration and fixtures
├── test_config.py             # Configuration testing
├── test_document_loader.py    # Document loading tests
├── test_rag_system.py         # Core RAG system tests
├── test_integration_comprehensive.py  # End-to-end integration tests
└── test_utils.py              # Testing utilities
```

### Docker Configuration (`docker/`)
```
docker/
├── config/                     # Container configuration files
├── monitoring/                 # Monitoring stack configs
├── nginx/                     # Reverse proxy configuration
├── scripts/                   # Container startup scripts
└── TROUBLESHOOTING.md         # Docker-specific troubleshooting
```

### Documentation (`docs/`)
```
docs/
├── SETUP.md                   # Setup and installation guide
└── DOCKER_DEPLOYMENT.md       # Docker deployment guide
```

### Monitoring (`monitoring/`)
Complete observability stack configuration:

```
monitoring/
├── prometheus.yml             # Prometheus configuration
├── grafana-dashboard.json     # Grafana dashboard definitions
├── grafana-datasources.yml    # Grafana data source config
├── otel-collector-config.yml  # OpenTelemetry collector
├── alertmanager.yml          # Alert manager rules
└── alert_rules.yml           # Prometheus alerting rules
```

### Scripts (`scripts/`)
```
scripts/
├── auto_sync.py              # Automated document synchronization
└── test_system.py            # System testing utilities
```

### Examples (`examples/`)
```
examples/
├── __init__.py
└── example_usage.py          # Usage examples and demos
```

## Architecture Patterns

### Module Organization
- **Single Responsibility**: Each module has a clear, focused purpose
- **Dependency Injection**: Configuration and dependencies injected via constructors
- **Interface Segregation**: Abstract base classes for key components
- **Error Boundaries**: Graceful error handling at module boundaries

### Import Conventions
```python
# Relative imports within package
try:
    from .config import Config
    from .document_loader import DocumentLoader
except ImportError:
    # Fallback for direct execution
    from config import Config
    from document_loader import DocumentLoader
```

### Configuration Management
- Centralized in `src/config.py`
- Environment-based configuration with `.env` support
- Pydantic models for validation
- Dataclasses for structured configuration objects

### Logging Strategy
- Module-level loggers: `logger = logging.getLogger(__name__)`
- UTF-8 encoding for Chinese text support
- Structured logging with consistent format
- Log files in `logs/` directory

### Testing Organization
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component interaction testing
- **End-to-End Tests**: Full system workflow testing
- **Fixtures**: Shared test data and mock objects in `conftest.py`

### Data Storage
```
# Runtime data directories
oran_nephio_vectordb/          # Vector database storage
embeddings_cache/              # Cached embeddings
test_embeddings_cache/         # Test environment cache
logs/                          # Application logs
```

## File Naming Conventions

### Python Files
- **Snake case**: `document_loader.py`, `oran_nephio_rag.py`
- **Descriptive names**: Clearly indicate module purpose
- **Test prefix**: `test_` prefix for all test files

### Configuration Files
- **Descriptive extensions**: `.yml` for YAML, `.json` for JSON
- **Environment specific**: `docker-compose.dev.yml`, `docker-compose.prod.yml`
- **Dot files**: `.env.example`, `.gitignore`, `.pre-commit-config.yaml`

### Documentation
- **Uppercase**: `README.md`, `LICENSE`, `DEPLOYMENT.md`
- **Descriptive**: Clear indication of content purpose

## Code Organization Principles

### Class Structure
```python
class ComponentName:
    """Clear docstring describing purpose"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize with dependency injection"""
        
    def _private_method(self):
        """Private methods prefixed with underscore"""
        
    def public_method(self):
        """Public API methods"""
```

### Error Handling
- Custom exceptions in relevant modules
- Comprehensive logging of errors
- Graceful degradation where possible
- User-friendly error messages in Chinese

### Resource Management
- Context managers for file operations
- Proper cleanup in `__del__` methods
- Memory-conscious vector database operations
- Connection pooling for HTTP requests

## Development Workflow

### Branch Structure
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `hotfix/*`: Critical fixes

### Code Quality Gates
1. **Pre-commit hooks**: Format and lint before commit
2. **Unit tests**: Must pass before merge
3. **Integration tests**: Full system validation
4. **Type checking**: MyPy validation
5. **Security scanning**: Bandit security checks