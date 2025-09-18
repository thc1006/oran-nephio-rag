# Configuration Guide

This guide covers all configuration options for the O-RAN × Nephio RAG system.

## Environment Variables

All configuration is done through environment variables. Create a `.env` file in the project root or set these variables in your deployment environment.

### Core Configuration

#### API Mode Selection
```bash
# Choose your deployment mode
API_MODE=browser  # Options: browser, mock
```

**Available Modes:**
- **`browser`**: Production mode using browser automation with Puter.js integration
- **`mock`**: Testing mode with pre-defined responses (no AI models required)

#### Model Configuration
```bash
# Browser mode settings
PUTER_MODEL=claude-sonnet-4  # AI model for browser automation
CLAUDE_MODEL=claude-3-sonnet-20240229  # Legacy compatibility

# Model parameters
MAX_TOKENS=4000        # Maximum response tokens
TEMPERATURE=0.1        # Response creativity (0.0-1.0)
```

**Supported Models:**
- `claude-sonnet-4` (recommended)
- `claude-opus-4`
- `claude-sonnet-3.7`
- `claude-sonnet-3.5`

### Browser Automation Settings

```bash
# Browser configuration
BROWSER_HEADLESS=true    # Run browser without GUI
BROWSER_TIMEOUT=120      # Browser operation timeout (seconds)
BROWSER_WAIT_TIME=10     # Wait time between operations (seconds)
```

**Browser Settings Explained:**
- **`BROWSER_HEADLESS=true`**: Recommended for production environments
- **`BROWSER_HEADLESS=false`**: Useful for debugging and development
- **`BROWSER_TIMEOUT`**: Increase for slower networks or complex operations
- **`BROWSER_WAIT_TIME`**: Increase if experiencing stability issues

### Database Configuration

```bash
# Vector database settings
VECTOR_DB_PATH=./oran_nephio_vectordb     # Database storage path
COLLECTION_NAME=oran_nephio_official      # Collection name
EMBEDDINGS_CACHE_PATH=./embeddings_cache  # Embeddings cache directory

# Document processing
CHUNK_SIZE=1024         # Document chunk size (characters)
CHUNK_OVERLAP=200       # Overlap between chunks (characters)
```

**Database Path Guidelines:**
- Use absolute paths for production deployments
- Ensure sufficient disk space (2GB+ recommended)
- Use fast storage (SSD) for better performance

### Retrieval Configuration

```bash
# Document retrieval settings
RETRIEVER_K=6           # Number of documents to retrieve
RETRIEVER_FETCH_K=15    # Candidate documents to fetch
RETRIEVER_LAMBDA_MULT=0.7  # MMR diversity parameter (0.0-1.0)

# Content validation
MIN_CONTENT_LENGTH=500              # Minimum content length (bytes)
MIN_EXTRACTED_CONTENT_LENGTH=100    # Minimum extracted content
MIN_KEYWORD_COUNT=2                 # Minimum O-RAN/Nephio keywords
```

**Retrieval Tuning:**
- **Higher `RETRIEVER_K`**: More context, slower queries
- **Lower `RETRIEVER_K`**: Faster queries, less context
- **`RETRIEVER_LAMBDA_MULT`**: 0.0 = max relevance, 1.0 = max diversity

### Performance and Reliability

```bash
# HTTP settings
MAX_RETRIES=3           # Maximum retry attempts
REQUEST_TIMEOUT=30      # HTTP request timeout (seconds)
REQUEST_DELAY=1.0       # Delay between requests (seconds)
RETRY_DELAY_BASE=2.0    # Base retry delay (seconds)
MAX_RETRY_DELAY=10      # Maximum retry delay (seconds)

# SSL settings
VERIFY_SSL=true         # Verify SSL certificates
SSL_TIMEOUT=30          # SSL connection timeout (seconds)
```

### Logging and Monitoring

```bash
# Logging configuration
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/oran_nephio_rag.log      # Log file path

# Monitoring endpoints
METRICS_PORT=8000       # Metrics server port
JAEGER_AGENT_HOST=localhost  # Jaeger tracing host
JAEGER_AGENT_PORT=14268      # Jaeger tracing port
OTLP_ENDPOINT=http://localhost:4317  # OpenTelemetry endpoint
```

### Auto-Sync Configuration

```bash
# Automatic document synchronization
AUTO_SYNC_ENABLED=true      # Enable automatic sync
SYNC_INTERVAL_HOURS=24      # Sync interval (hours)
```

### API Server Configuration

```bash
# API server settings
API_HOST=0.0.0.0        # Server bind address
API_PORT=8000           # Server port
API_WORKERS=1           # Number of worker processes
API_DEBUG=false         # Enable debug mode
```

## Configuration Profiles

### Development Profile

Perfect for local development and testing:

```bash
# .env.development
API_MODE=mock
LOG_LEVEL=DEBUG
BROWSER_HEADLESS=false
CHUNK_SIZE=512
RETRIEVER_K=3
AUTO_SYNC_ENABLED=false
API_DEBUG=true
```

### Testing Profile

Optimized for automated testing:

```bash
# .env.testing
API_MODE=mock
LOG_LEVEL=WARNING
CHUNK_SIZE=256
RETRIEVER_K=2
AUTO_SYNC_ENABLED=false
REQUEST_TIMEOUT=10
MAX_RETRIES=1
```

### Production Profile

Production-ready configuration:

```bash
# .env.production
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=120
LOG_LEVEL=INFO
CHUNK_SIZE=1024
RETRIEVER_K=6
AUTO_SYNC_ENABLED=true
SYNC_INTERVAL_HOURS=24
VERIFY_SSL=true
API_WORKERS=4
```

### High-Performance Profile

For high-throughput scenarios:

```bash
# .env.performance
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
CHUNK_SIZE=512           # Smaller chunks for speed
RETRIEVER_K=3            # Fewer documents for speed
RETRIEVER_FETCH_K=10     # Fewer candidates
REQUEST_TIMEOUT=15       # Shorter timeout
MAX_RETRIES=2            # Fewer retries
API_WORKERS=8            # More workers
```

## Configuration Validation

The system automatically validates configuration on startup. Common validation errors:

### Invalid API Mode
```
Error: API_MODE must be one of: browser, mock
Solution: Set API_MODE=browser or API_MODE=mock
```

### Missing Model Configuration
```
Error: API_MODE=browser requires PUTER_MODEL
Solution: Set PUTER_MODEL=claude-sonnet-4
```

### Invalid Temperature
```
Error: TEMPERATURE must be between 0-1
Solution: Set TEMPERATURE to value between 0.0 and 1.0
```

### Invalid Chunk Configuration
```
Error: CHUNK_OVERLAP cannot be greater than or equal to CHUNK_SIZE
Solution: Ensure CHUNK_OVERLAP < CHUNK_SIZE
```

## Document Source Configuration

### Official Sources

The system includes pre-configured official sources:

```python
# Nephio sources
- https://docs.nephio.org/docs/network-architecture/o-ran-integration/
- https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-4-o2ims/
- https://docs.nephio.org/docs/architecture/
- https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-2-free5gc-operator/

# O-RAN Software Community sources (when available)
```

### Adding Custom Sources

```python
from src.config import Config, DocumentSource

# Add custom source
custom_source = DocumentSource(
    url="https://your-custom-docs.com/api/",
    source_type="nephio",  # or "oran_sc"
    description="Custom Nephio Documentation",
    priority=2,  # 1=highest, 5=lowest
    enabled=True
)

Config.add_custom_source(custom_source)
```

### Source Management

```python
# Disable a source
Config.disable_source_by_url("https://example.com/docs/")

# Enable a source
Config.enable_source_by_url("https://example.com/docs/")

# Get sources by type
nephio_sources = Config.get_sources_by_type("nephio")
oran_sources = Config.get_sources_by_type("oran_sc")

# Get high-priority sources
priority_sources = Config.get_sources_by_priority(max_priority=2)
```

## Security Configuration

### Authentication

```bash
# API key authentication
ANTHROPIC_API_KEY=your_api_key_here    # For testing compatibility

# JWT settings (if using JWT)
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Rate Limiting

Rate limits are configured in the application code:

```python
# Default rate limits
- Query endpoints: 10/minute per IP
- Search endpoints: 20/minute per IP
- Bulk operations: 2/minute per IP
```

### CORS Configuration

```python
# CORS settings (modify in src/api/main.py)
allow_origins=["*"]          # Configure for production
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

## Docker Configuration

### Environment Files

```bash
# docker-compose.dev.yml environment
- API_MODE=mock
- LOG_LEVEL=DEBUG
- BROWSER_HEADLESS=false

# docker-compose.prod.yml environment
- API_MODE=browser
- PUTER_MODEL=claude-sonnet-4
- BROWSER_HEADLESS=true
- LOG_LEVEL=INFO
```

### Volume Mounts

```yaml
volumes:
  - ./oran_nephio_vectordb:/app/oran_nephio_vectordb
  - ./logs:/app/logs
  - ./embeddings_cache:/app/embeddings_cache
```

## Kubernetes Configuration

### ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: oran-rag-config
data:
  API_MODE: "browser"
  PUTER_MODEL: "claude-sonnet-4"
  BROWSER_HEADLESS: "true"
  LOG_LEVEL: "INFO"
  CHUNK_SIZE: "1024"
  RETRIEVER_K: "6"
```

### Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: oran-rag-secrets
type: Opaque
data:
  ANTHROPIC_API_KEY: <base64-encoded-key>
```

## Configuration Best Practices

### 1. Environment Separation
- Use different `.env` files for development, testing, and production
- Never commit `.env` files to version control
- Use secrets management in production

### 2. Performance Tuning
- Start with default values and adjust based on monitoring
- Monitor memory usage when increasing `CHUNK_SIZE` or `RETRIEVER_K`
- Use smaller chunks for faster processing, larger for better context

### 3. Reliability
- Set appropriate timeouts based on your network conditions
- Configure retries based on your error tolerance
- Enable SSL verification in production

### 4. Monitoring
- Use structured logging with appropriate log levels
- Enable metrics collection for production monitoring
- Set up alerts for key system metrics

### 5. Security
- Disable debug mode in production
- Use HTTPS in production
- Configure CORS appropriately for your deployment
- Regularly rotate API keys and secrets

## Troubleshooting Configuration

### Check Current Configuration

```python
from src.config import Config

# Get configuration summary
summary = Config.get_config_summary()
print(summary)

# Validate configuration
try:
    Config.validate()
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### Common Configuration Issues

1. **Directory Permissions**: Ensure write access to log and database directories
2. **Memory Settings**: Reduce chunk size if experiencing memory issues
3. **Network Timeouts**: Increase timeouts for slow networks
4. **Browser Issues**: Try different headless settings or update Chrome

### Configuration Testing

```bash
# Test configuration validity
python -c "from src.config import Config; Config.validate()"

# Test system with configuration
python test_config_isolated.py

# Test API with configuration
curl http://localhost:8000/api/v1/system/config
```

This comprehensive configuration guide should help you optimize the O-RAN × Nephio RAG system for your specific use case and deployment environment.