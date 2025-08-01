# Technology Stack

## Core Technologies

### Python Environment
- **Python Version**: 3.9+ (supports up to 3.13)
- **Package Management**: pip with requirements.txt
- **Virtual Environment**: Standard venv recommended
- **Build System**: setuptools with pyproject.toml configuration

### AI/ML Framework
- **LangChain**: Core RAG framework (>=0.1.0,<0.4.0)
  - langchain-community for integrations
  - langchain-anthropic for Claude AI
  - langchain-huggingface for embeddings
- **Anthropic Claude**: Primary LLM (claude-3-sonnet-20240229)
- **Sentence Transformers**: Text embeddings (>=2.2.2,<4.0.0)
- **ChromaDB**: Vector database (>=0.4.0,<0.6.0)

### Web & HTTP
- **Requests**: HTTP client for document fetching
- **BeautifulSoup4**: HTML parsing and cleaning
- **aiohttp**: Async HTTP support
- **lxml**: XML/HTML processing

### Configuration & Environment
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and settings
- **pydantic-settings**: Configuration management

### Development Tools
- **pytest**: Testing framework with async support
- **black**: Code formatting (line-length: 120)
- **flake8**: Linting
- **mypy**: Type checking
- **isort**: Import sorting
- **pre-commit**: Git hooks

### Monitoring & Observability
- **OpenTelemetry**: Distributed tracing
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Jaeger**: Trace visualization

### Containerization
- **Docker**: Multi-stage builds with Python 3.11 slim base
- **Docker Compose**: Development, production, and monitoring configurations
- **Non-root user**: Security-focused container setup

## API Modes

The system supports multiple API modes via `API_MODE` environment variable:
- `anthropic`: Production Claude API (default)
- `mock`: Testing with mock responses
- `local`: Local LLM via Ollama
- `puter`: Experimental Puter.js integration

## Common Commands

### Development Setup
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools

# Setup environment
cp .env.example .env
# Edit .env with ANTHROPIC_API_KEY
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/ -m "unit"
pytest tests/ -m "integration"
```

### Code Quality
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/

# Install pre-commit hooks
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

# Build specific target
docker build --target development -t oran-rag:dev .
```

### Application Usage
```bash
# Run main application
python main.py

# Initialize vector database
python -c "from src import create_rag_system; rag = create_rag_system(); rag.build_vector_database()"

# Quick query
python -c "from src import quick_query; print(quick_query('Your question here'))"
```

## Configuration Standards

### Environment Variables
- Use `.env` file for local development
- Prefix system variables with appropriate namespaces
- Provide sensible defaults in Config class
- Document all variables in README

### Logging
- Structured logging with timestamps
- UTF-8 encoding for Chinese text support
- File and console handlers
- Configurable log levels via LOG_LEVEL

### Error Handling
- Graceful degradation for API failures
- Comprehensive exception logging
- User-friendly error messages in Chinese
- Retry mechanisms for transient failures