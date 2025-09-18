# Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common issues with the O-RAN × Nephio RAG system.

## Table of Contents

- [Common Issues](#common-issues)
- [Installation Problems](#installation-problems)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [API-Specific Problems](#api-specific-problems)
- [Database Issues](#database-issues)
- [Browser Automation Issues](#browser-automation-issues)
- [Configuration Problems](#configuration-problems)
- [Monitoring and Diagnostics](#monitoring-and-diagnostics)
- [Getting Help](#getting-help)

## Common Issues

### Quick Diagnostics

Run these commands to quickly assess system health:

```bash
# Check API health
curl -s http://localhost:8000/health | jq '.'

# Check system status
curl -s http://localhost:8000/api/v1/system/status | jq '.'

# Check configuration
python -c "from src.config import Config; Config.validate(); print('✅ Config OK')"

# Check basic imports
python test_basic_imports.py

# Test simple query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": 1}' | jq '.success'
```

## Installation Problems

### 1. Dependency Conflicts

**Symptoms:**
- Import errors during installation
- Version conflicts between packages
- Build failures during pip install

**Solutions:**

```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Clean install
pip uninstall -y $(pip freeze | cut -d= -f1)
pip install -r requirements.txt

# Use binary packages only (if compilation fails)
pip install --only-binary=all -r requirements.txt

# Install in development mode
pip install -e .
```

### 2. Python Version Issues

**Symptoms:**
- Syntax errors with modern Python features
- Module compatibility issues

**Solutions:**

```bash
# Check Python version
python --version  # Should be 3.9+

# Use pyenv for version management
pyenv install 3.11.0
pyenv local 3.11.0

# Or use conda
conda create -n oran-rag python=3.11
conda activate oran-rag
```

### 3. System Dependencies

**Symptoms:**
- Missing system libraries
- Compilation errors for native extensions

**Solutions:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libblas-dev \
    liblapack-dev \
    pkg-config

# CentOS/RHEL
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel openssl-devel libffi-devel

# macOS
xcode-select --install
brew install openssl libffi
```

## Runtime Errors

### 1. Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solutions:**

```bash
# Install in development mode
pip install -e .

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run from project root
cd /path/to/oran-nephio-rag
python -m src.api.main
```

### 2. Configuration Errors

**Error:** `ValueError: Configuration validation failed`

**Solutions:**

```bash
# Check configuration
python -c "
from src.config import Config
try:
    Config.validate()
    print('✅ Configuration valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
"

# Fix common configuration issues
echo "API_MODE=mock" > .env
echo "VECTOR_DB_PATH=./oran_nephio_vectordb" >> .env
echo "PUTER_MODEL=claude-sonnet-4" >> .env
```

### 3. Permission Errors

**Error:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**

```bash
# Fix directory permissions
sudo chown -R $USER:$USER ./oran_nephio_vectordb
sudo chown -R $USER:$USER ./logs
sudo chown -R $USER:$USER ./embeddings_cache

# Create directories with proper permissions
mkdir -p logs oran_nephio_vectordb embeddings_cache
chmod 755 logs oran_nephio_vectordb embeddings_cache
```

## Performance Issues

### 1. High Memory Usage

**Symptoms:**
- System becomes slow or unresponsive
- Out of memory errors
- Swapping activity

**Solutions:**

```bash
# Reduce chunk size
echo "CHUNK_SIZE=512" >> .env
echo "CHUNK_OVERLAP=100" >> .env

# Reduce retrieval documents
echo "RETRIEVER_K=3" >> .env
echo "RETRIEVER_FETCH_K=10" >> .env

# Monitor memory usage
curl http://localhost:8000/api/v1/system/metrics | jq '.memory_usage'

# Use system monitoring
htop
# or
top
```

### 2. Slow Query Response

**Symptoms:**
- Long query processing times
- Timeouts

**Solutions:**

```bash
# Optimize retrieval settings
echo "RETRIEVER_K=3" >> .env           # Fewer documents
echo "MAX_TOKENS=2000" >> .env         # Shorter responses
echo "CHUNK_SIZE=512" >> .env          # Smaller chunks

# Check query performance
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": 3}' | jq '.query_time'

# Enable performance monitoring
echo "LOG_LEVEL=DEBUG" >> .env
tail -f logs/oran_nephio_rag.log
```

### 3. Database Performance

**Symptoms:**
- Slow vector similarity search
- Long database initialization

**Solutions:**

```bash
# Rebuild with smaller dataset
python create_minimal_database.py

# Use SSD storage for vector database
mv ./oran_nephio_vectordb /path/to/ssd/storage/
ln -s /path/to/ssd/storage/oran_nephio_vectordb ./

# Optimize embeddings cache
echo "EMBEDDINGS_CACHE_PATH=/tmp/embeddings_cache" >> .env
```

## API-Specific Problems

### 1. Service Unavailable (503)

**Error:** `503 Service Unavailable: RAG system not available`

**Diagnosis:**

```bash
# Check if vector database exists
ls -la ./oran_nephio_vectordb/

# Check system status
curl http://localhost:8000/api/v1/system/status | jq '.'

# Check logs
tail -f logs/oran_nephio_rag.log
```

**Solutions:**

```bash
# Create/rebuild database
python create_minimal_database.py

# Force system reinitialization
curl -X POST http://localhost:8000/api/v1/documents/refresh \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": true}'

# Restart API server
# Kill existing process and restart
pkill -f "python.*api.main"
python -m src.api.main
```

### 2. Rate Limiting (429)

**Error:** `429 Too Many Requests: Rate limit exceeded`

**Solutions:**

```bash
# Wait and retry
sleep 60

# Check rate limit headers
curl -I http://localhost:8000/api/v1/query

# Use bulk endpoint for multiple queries
curl -X POST http://localhost:8000/api/v1/query/bulk \
  -H "Content-Type: application/json" \
  -d '{"queries": ["query1", "query2"], "k": 3}'
```

### 3. Authentication Errors (401)

**Error:** `401 Unauthorized: Invalid or missing API key`

**Solutions:**

```bash
# Check if API key is set
echo $API_KEY

# Use correct header format
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/api/v1/system/status

# For development, API key might not be required
curl http://localhost:8000/health  # Should work without auth
```

## Database Issues

### 1. Empty Vector Database

**Symptoms:**
- No search results returned
- "No documents found" errors
- Empty vector database directory

**Solutions:**

```bash
# Check database contents
ls -la ./oran_nephio_vectordb/

# Create minimal test database
python create_minimal_database.py

# Build from official sources (requires browser mode)
python -c "
from src import create_rag_system
rag = create_rag_system()
success = rag.build_database()
print(f'Database build: {\"Success\" if success else \"Failed\"}')
"

# Verify database
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.load_existing_database()
status = rag.get_system_status()
print(f'Document count: {status.get(\"document_count\", 0)}')
"
```

### 2. Corrupted Database

**Symptoms:**
- Database loading errors
- Inconsistent search results
- ChromaDB errors

**Solutions:**

```bash
# Backup existing database
cp -r ./oran_nephio_vectordb ./oran_nephio_vectordb.backup

# Remove corrupted database
rm -rf ./oran_nephio_vectordb

# Rebuild database
python create_minimal_database.py

# Or restore from backup
mv ./oran_nephio_vectordb.backup ./oran_nephio_vectordb
```

### 3. Database Connection Issues

**Error:** `sqlite3.OperationalError: database is locked`

**Solutions:**

```bash
# Check for running processes
ps aux | grep oran

# Kill hanging processes
pkill -f "python.*oran"

# Remove lock files
rm -f ./oran_nephio_vectordb/*.lock

# Restart with clean state
python -m src.api.main
```

## Browser Automation Issues

### 1. Chrome/Browser Not Found

**Error:** `selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solutions:**

```bash
# Install Chrome (Ubuntu/Debian)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install Chrome (CentOS/RHEL)
sudo yum install -y google-chrome-stable

# Update WebDriver
pip install --upgrade webdriver-manager

# Use headless mode
echo "BROWSER_HEADLESS=true" >> .env
```

### 2. Browser Timeout Issues

**Error:** `TimeoutException: Message: timeout`

**Solutions:**

```bash
# Increase timeout
echo "BROWSER_TIMEOUT=180" >> .env
echo "BROWSER_WAIT_TIME=15" >> .env

# Check network connectivity
curl -I https://puter.com

# Use mock mode for testing
echo "API_MODE=mock" >> .env
```

### 3. Browser Crash or Hang

**Symptoms:**
- Browser processes consuming high CPU
- Selenium timeout errors
- Browser windows not closing

**Solutions:**

```bash
# Kill hanging browser processes
pkill -f chrome
pkill -f chromium

# Clear browser cache/tmp files
rm -rf /tmp/.com.google.Chrome.*
rm -rf /tmp/chrome_*

# Restart with clean browser state
python -m src.api.main
```

## Configuration Problems

### 1. Invalid Environment Variables

**Common Issues:**

```bash
# Check for invalid values
python -c "
import os
from src.config import Config

# Check numeric values
try:
    chunk_size = int(os.getenv('CHUNK_SIZE', '1024'))
    print(f'✅ CHUNK_SIZE: {chunk_size}')
except ValueError:
    print('❌ CHUNK_SIZE must be integer')

# Check temperature range
try:
    temp = float(os.getenv('TEMPERATURE', '0.1'))
    if 0 <= temp <= 1:
        print(f'✅ TEMPERATURE: {temp}')
    else:
        print('❌ TEMPERATURE must be 0-1')
except ValueError:
    print('❌ TEMPERATURE must be float')
"

# Fix common issues
sed -i 's/TEMPERATURE=1.5/TEMPERATURE=0.1/' .env
sed -i 's/CHUNK_SIZE=abc/CHUNK_SIZE=1024/' .env
```

### 2. Path Configuration Issues

**Solutions:**

```bash
# Use absolute paths
echo "VECTOR_DB_PATH=$(pwd)/oran_nephio_vectordb" >> .env
echo "LOG_FILE=$(pwd)/logs/oran_nephio_rag.log" >> .env

# Create required directories
mkdir -p logs oran_nephio_vectordb embeddings_cache

# Check path permissions
ls -la logs/ oran_nephio_vectordb/ embeddings_cache/
```

## Monitoring and Diagnostics

### 1. Enable Debug Logging

```bash
# Set debug level
echo "LOG_LEVEL=DEBUG" >> .env

# Watch logs in real-time
tail -f logs/oran_nephio_rag.log

# Filter specific log levels
grep "ERROR" logs/oran_nephio_rag.log
grep "WARNING" logs/oran_nephio_rag.log
```

### 2. System Diagnostics

```bash
# Check system resources
df -h  # Disk space
free -h  # Memory
top     # CPU usage

# Check network connectivity
curl -I http://localhost:8000/health
ping localhost

# Check port availability
netstat -tlnp | grep 8000
# or
ss -tlnp | grep 8000
```

### 3. API Diagnostics

```bash
# Test API endpoints
curl -v http://localhost:8000/health
curl -v http://localhost:8000/api/v1/system/status

# Check response times
time curl -s http://localhost:8000/health > /dev/null

# Monitor API metrics
curl http://localhost:8000/metrics
```

### 4. Performance Profiling

```python
# Add to your Python scripts for profiling
import cProfile
import pstats
from src import create_rag_system

def profile_query():
    rag = create_rag_system()
    rag.load_existing_database()
    result = rag.query("What is O-RAN?")
    return result

# Run profiling
cProfile.run('profile_query()', 'profile_stats.prof')

# Analyze results
stats = pstats.Stats('profile_stats.prof')
stats.sort_stats('tottime').print_stats(20)
```

## Common Error Messages and Solutions

### Error: "No module named 'src'"
```bash
# Solution: Install in development mode
pip install -e .
```

### Error: "CUDA out of memory"
```bash
# Solution: Use CPU-only mode or reduce batch size
echo "DEVICE=cpu" >> .env
echo "CHUNK_SIZE=256" >> .env
```

### Error: "ChromaDB connection failed"
```bash
# Solution: Reset database
rm -rf ./oran_nephio_vectordb
python create_minimal_database.py
```

### Error: "Rate limit exceeded for API"
```bash
# Solution: Wait and implement retry logic
sleep 60
# Use exponential backoff in your client code
```

### Error: "SSL certificate verification failed"
```bash
# Solution: Disable SSL verification (development only)
echo "VERIFY_SSL=false" >> .env
```

## Docker-Specific Issues

### 1. Container Won't Start

```bash
# Check container logs
docker logs oran-rag-app

# Check container status
docker ps -a

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 2. Volume Mount Issues

```bash
# Check volume mounts
docker inspect oran-rag-app | jq '.[0].Mounts'

# Fix permissions
sudo chown -R 1000:1000 ./oran_nephio_vectordb
sudo chown -R 1000:1000 ./logs
```

### 3. Network Issues

```bash
# Check Docker network
docker network ls
docker network inspect oran-rag_default

# Test container connectivity
docker exec oran-rag-app curl localhost:8000/health
```

## Getting Help

### 1. Gather Diagnostic Information

Before seeking help, collect this information:

```bash
# System information
cat > diagnostic_info.txt << EOF
=== System Information ===
OS: $(uname -a)
Python: $(python --version)
Pip packages: $(pip list | grep -E "(langchain|chromadb|fastapi)")

=== Configuration ===
$(cat .env)

=== Recent Logs ===
$(tail -50 logs/oran_nephio_rag.log)

=== System Status ===
$(curl -s http://localhost:8000/api/v1/system/status)

=== Health Check ===
$(curl -s http://localhost:8000/health)
EOF

cat diagnostic_info.txt
```

### 2. Test with Minimal Setup

```bash
# Create clean test environment
cd /tmp
git clone https://github.com/thc1006/oran-nephio-rag.git test-oran-rag
cd test-oran-rag

# Minimal setup
python -m venv test-venv
source test-venv/bin/activate
pip install -r requirements.txt

# Test basic functionality
echo "API_MODE=mock" > .env
python test_basic_imports.py
python create_minimal_database.py
```

### 3. Contact Support

When contacting support, include:

1. **Error message** (exact text)
2. **Steps to reproduce** the issue
3. **System information** (OS, Python version)
4. **Configuration** (.env file contents)
5. **Log files** (recent entries)
6. **What you tried** to fix the issue

**Support Channels:**
- 📧 Email: hctsai@linux.com
- 🐛 GitHub Issues: https://github.com/thc1006/oran-nephio-rag/issues
- 💬 Discussions: https://github.com/thc1006/oran-nephio-rag/discussions

### 4. Community Resources

- **Documentation**: Check `/docs` for detailed guides
- **Examples**: Review `/examples` for working code
- **Tests**: Run existing tests to verify functionality
- **Configuration**: Use provided configuration templates

This troubleshooting guide should help you resolve most common issues. If you encounter a problem not covered here, please contribute by documenting the solution for future users.