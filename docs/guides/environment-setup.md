# Environment Setup and Configuration Guide

This comprehensive guide covers setting up the development and production environments for the O-RAN × Nephio RAG system, including all necessary dependencies, configurations, and best practices.

## Table of Contents

- [System Requirements](#system-requirements)
- [Development Environment Setup](#development-environment-setup)
- [Production Environment Setup](#production-environment-setup)
- [Environment Variables Reference](#environment-variables-reference)
- [Database Setup](#database-setup)
- [Browser Automation Setup](#browser-automation-setup)
- [Testing Environment](#testing-environment)
- [IDE Configuration](#ide-configuration)
- [Troubleshooting Environment Issues](#troubleshooting-environment-issues)

## System Requirements

### Minimum Requirements

```bash
# Hardware
CPU: 4 cores (x86_64)
RAM: 8GB (4GB minimum)
Storage: 10GB available space
Network: Stable internet connection

# Software
OS: Linux (Ubuntu 20.04+), macOS (10.15+), Windows (10/11)
Python: 3.9 - 3.11 (3.11 recommended)
Browser: Chrome/Chromium (for browser automation)
Git: 2.20+
```

### Recommended Production Requirements

```bash
# Hardware
CPU: 8+ cores (x86_64)
RAM: 16GB+
Storage: 50GB+ SSD
Network: High-speed internet, low latency

# Additional
Load Balancer: Nginx/HAProxy
Monitoring: Prometheus + Grafana
Container Runtime: Docker 20.10+
Orchestration: Kubernetes 1.20+
```

## Development Environment Setup

### 1. Install System Dependencies

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    build-essential \
    git \
    curl \
    wget \
    unzip \
    software-properties-common

# Install Chrome for browser automation
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install additional dependencies
sudo apt install -y \
    libssl-dev \
    libffi-dev \
    libblas-dev \
    liblapack-dev \
    pkg-config \
    chromium-browser
```

#### CentOS/RHEL

```bash
# Install EPEL repository
sudo yum install -y epel-release

# Install Python and development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    python39 \
    python39-devel \
    python39-pip \
    git \
    curl \
    wget \
    unzip

# Install Chrome
sudo yum install -y google-chrome-stable

# Or install chromium
sudo yum install -y chromium
```

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 git curl wget

# Install Chrome
brew install --cask google-chrome

# Install development tools
xcode-select --install
```

#### Windows

```powershell
# Install Python from python.org or use winget
winget install Python.Python.3.11

# Install Git
winget install Git.Git

# Install Chrome
winget install Google.Chrome

# Install Visual Studio Build Tools (for native extensions)
winget install Microsoft.VisualStudio.2022.BuildTools
```

### 2. Create Python Virtual Environment

```bash
# Create project directory
mkdir -p ~/projects/oran-nephio-rag
cd ~/projects/oran-nephio-rag

# Clone repository
git clone https://github.com/thc1006/oran-nephio-rag.git .

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify Python version
python --version  # Should show Python 3.11.x

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 3. Install Python Dependencies

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode (editable)
pip install -e .

# Verify installation
python -c "import src; print('✅ Package installed successfully')"

# Run basic tests
python test_basic_imports.py
```

### 4. Configure Development Environment

```bash
# Create development configuration
cat > .env.development << 'EOF'
# Development Configuration
API_MODE=mock
LOG_LEVEL=DEBUG
BROWSER_HEADLESS=false

# Database paths (development)
VECTOR_DB_PATH=./dev_vectordb
EMBEDDINGS_CACHE_PATH=./dev_embeddings
COLLECTION_NAME=oran_nephio_dev

# Development settings
CHUNK_SIZE=512
RETRIEVER_K=3
AUTO_SYNC_ENABLED=false
REQUEST_TIMEOUT=10
MAX_RETRIES=2

# API settings
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=true
API_WORKERS=1

# Browser settings
BROWSER_TIMEOUT=60
BROWSER_WAIT_TIME=5
EOF

# Copy development config to main .env
cp .env.development .env

# Create development directories
mkdir -p dev_vectordb dev_embeddings logs
```

### 5. Initialize Development Database

```bash
# Create minimal test database
python create_minimal_database.py

# Verify database creation
ls -la dev_vectordb/

# Test system functionality
python -c "
from src import create_rag_system
rag = create_rag_system()
status = rag.get_system_status()
print(f'System ready: {status.get(\"system_ready\", False)}')
print(f'Document count: {status.get(\"document_count\", 0)}')
"
```

### 6. Start Development Server

```bash
# Start API server in development mode
python -m src.api.main

# Or use auto-reload
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/system/status
```

## Production Environment Setup

### 1. Production System Preparation

```bash
# Create production user
sudo useradd -m -s /bin/bash oran-rag
sudo usermod -aG sudo oran-rag

# Create application directories
sudo mkdir -p /opt/oran-rag
sudo mkdir -p /var/lib/oran-rag/{vectordb,embeddings,logs}
sudo mkdir -p /etc/oran-rag

# Set ownership
sudo chown -R oran-rag:oran-rag /opt/oran-rag
sudo chown -R oran-rag:oran-rag /var/lib/oran-rag
sudo chown -R oran-rag:oran-rag /etc/oran-rag
```

### 2. Production Installation

```bash
# Switch to production user
sudo su - oran-rag

# Clone repository
cd /opt/oran-rag
git clone https://github.com/thc1006/oran-nephio-rag.git .

# Create production virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Install application
pip install -e .
```

### 3. Production Configuration

```bash
# Create production configuration
cat > /etc/oran-rag/production.env << 'EOF'
# Production Configuration
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=120

# Database paths (production)
VECTOR_DB_PATH=/var/lib/oran-rag/vectordb
EMBEDDINGS_CACHE_PATH=/var/lib/oran-rag/embeddings
COLLECTION_NAME=oran_nephio_production

# Production settings
LOG_LEVEL=INFO
LOG_FILE=/var/lib/oran-rag/logs/oran_nephio_rag.log
CHUNK_SIZE=1024
RETRIEVER_K=6
AUTO_SYNC_ENABLED=true
SYNC_INTERVAL_HOURS=24

# Performance settings
MAX_TOKENS=4000
TEMPERATURE=0.1
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# API settings
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_DEBUG=false

# Security settings
VERIFY_SSL=true
MIN_CONTENT_LENGTH=500

# Browser settings
BROWSER_WAIT_TIME=10
EOF

# Secure configuration file
sudo chmod 640 /etc/oran-rag/production.env
sudo chown oran-rag:oran-rag /etc/oran-rag/production.env

# Link to application directory
ln -s /etc/oran-rag/production.env /opt/oran-rag/.env
```

### 4. Production Database Setup

```bash
# Initialize production database
cd /opt/oran-rag
source venv/bin/activate

# Create initial database with full sources (requires API access)
python -c "
import os
os.environ['API_MODE'] = 'browser'
from src import create_rag_system
rag = create_rag_system()
success = rag.build_database()
print(f'Production database build: {\"Success\" if success else \"Failed\"}')
"

# Verify database
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.load_existing_database()
status = rag.get_system_status()
print(f'Document count: {status.get(\"document_count\", 0)}')
print(f'Enabled sources: {status.get(\"enabled_sources\", 0)}')
"
```

### 5. Systemd Service Configuration

```bash
# Create systemd service file
sudo cat > /etc/systemd/system/oran-rag.service << 'EOF'
[Unit]
Description=O-RAN × Nephio RAG API Service
After=network.target
Wants=network.target

[Service]
Type=exec
User=oran-rag
Group=oran-rag
WorkingDirectory=/opt/oran-rag
Environment=PATH=/opt/oran-rag/venv/bin
EnvironmentFile=/etc/oran-rag/production.env
ExecStart=/opt/oran-rag/venv/bin/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 300 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile /var/lib/oran-rag/logs/access.log \
    --error-logfile /var/lib/oran-rag/logs/error.log \
    --log-level info \
    src.api.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/oran-rag
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable oran-rag
sudo systemctl start oran-rag

# Check service status
sudo systemctl status oran-rag
sudo journalctl -u oran-rag -f
```

### 6. Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/oran-rag << 'EOF'
upstream oran_rag_backend {
    server 127.0.0.1:8000;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=search:10m rate=20r/m;
limit_req_zone $binary_remote_addr zone=bulk:10m rate=2r/m;

server {
    listen 80;
    server_name your-domain.com;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Logging
    access_log /var/log/nginx/oran-rag-access.log;
    error_log /var/log/nginx/oran-rag-error.log;

    # API endpoints with rate limiting
    location /api/v1/query {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://oran_rag_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /api/v1/query/search {
        limit_req zone=search burst=10 nodelay;
        proxy_pass http://oran_rag_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/v1/query/bulk {
        limit_req zone=bulk burst=2 nodelay;
        proxy_pass http://oran_rag_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_timeout 600s;
        proxy_read_timeout 600s;
    }

    # Health check (no rate limiting)
    location /health {
        proxy_pass http://oran_rag_backend;
        access_log off;
    }

    # Metrics (restricted access)
    location /metrics {
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
        proxy_pass http://oran_rag_backend;
    }

    # All other endpoints
    location / {
        proxy_pass http://oran_rag_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/oran-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables Reference

### Core Configuration

```bash
# API Mode Selection
API_MODE=browser              # Options: browser, mock
PUTER_MODEL=claude-sonnet-4   # AI model for browser mode

# Database Configuration
VECTOR_DB_PATH=./oran_nephio_vectordb
EMBEDDINGS_CACHE_PATH=./embeddings_cache
COLLECTION_NAME=oran_nephio_official

# Logging Configuration
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/oran_nephio_rag.log
```

### Performance Tuning

```bash
# Text Processing
CHUNK_SIZE=1024               # Document chunk size (characters)
CHUNK_OVERLAP=200             # Overlap between chunks
MAX_TOKENS=4000               # Maximum response tokens
TEMPERATURE=0.1               # AI response creativity (0.0-1.0)

# Retrieval Settings
RETRIEVER_K=6                 # Documents to retrieve
RETRIEVER_FETCH_K=15          # Candidates to fetch
RETRIEVER_LAMBDA_MULT=0.7     # MMR diversity (0.0-1.0)

# HTTP Settings
MAX_RETRIES=3                 # Maximum retry attempts
REQUEST_TIMEOUT=30            # HTTP timeout (seconds)
REQUEST_DELAY=1.0             # Delay between requests
```

### Browser Automation

```bash
# Browser Configuration
BROWSER_HEADLESS=true         # Run without GUI
BROWSER_TIMEOUT=120           # Operation timeout
BROWSER_WAIT_TIME=10          # Wait between operations

# Content Validation
MIN_CONTENT_LENGTH=500        # Minimum content size
MIN_KEYWORD_COUNT=2           # Required keywords
```

### API Server

```bash
# Server Configuration
API_HOST=0.0.0.0             # Bind address
API_PORT=8000                # Server port
API_WORKERS=4                # Worker processes
API_DEBUG=false              # Debug mode

# Security
VERIFY_SSL=true              # SSL verification
JWT_SECRET_KEY=your_secret   # JWT secret (production)
```

### Monitoring

```bash
# Metrics
METRICS_PORT=8000            # Metrics endpoint port
JAEGER_AGENT_HOST=localhost  # Tracing host
OTLP_ENDPOINT=http://localhost:4317

# Auto-sync
AUTO_SYNC_ENABLED=true       # Enable automatic updates
SYNC_INTERVAL_HOURS=24       # Update interval
```

## Database Setup

### 1. Vector Database Initialization

```bash
# Create minimal database (for testing)
python create_minimal_database.py

# Create full database (requires API access)
python -c "
from src import create_rag_system
rag = create_rag_system()
success = rag.build_database()
print(f'Database created: {success}')
"

# Verify database
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.load_existing_database()
status = rag.get_system_status()
print(f'Documents: {status.get(\"document_count\", 0)}')
print(f'Sources: {status.get(\"enabled_sources\", 0)}')
"
```

### 2. Database Backup and Restore

```bash
# Backup database
tar -czf oran_vectordb_backup_$(date +%Y%m%d).tar.gz oran_nephio_vectordb/

# Restore database
tar -xzf oran_vectordb_backup_20240115.tar.gz

# Backup embeddings cache
tar -czf embeddings_backup_$(date +%Y%m%d).tar.gz embeddings_cache/
```

### 3. Database Migration

```bash
# Export current database info
python -c "
from src.config import Config
sources = Config.get_enabled_sources()
for source in sources:
    print(f'{source.url} | {source.source_type} | {source.priority}')
" > current_sources.txt

# Rebuild database with new sources
rm -rf oran_nephio_vectordb/
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.build_database()
"
```

## Browser Automation Setup

### 1. Chrome/Chromium Installation

```bash
# Ubuntu/Debian
sudo apt install -y google-chrome-stable

# Alternative: Chromium
sudo apt install -y chromium-browser

# CentOS/RHEL
sudo yum install -y google-chrome-stable

# macOS
brew install --cask google-chrome

# Verify installation
google-chrome --version
chromium --version
```

### 2. WebDriver Configuration

```bash
# Install ChromeDriver manager
pip install webdriver-manager

# Test WebDriver
python -c "
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
driver.get('https://example.com')
print(f'Title: {driver.title}')
driver.quit()
print('✅ Browser automation working')
"
```

### 3. Browser Troubleshooting

```bash
# Check Chrome installation
which google-chrome
google-chrome --version

# Test headless mode
google-chrome --headless --dump-dom https://example.com

# Check Chrome flags
google-chrome --headless --no-sandbox --disable-dev-shm-usage --dump-dom https://example.com

# Debug browser issues
export BROWSER_HEADLESS=false
python test_api_modes.py
```

## Testing Environment

### 1. Test Environment Setup

```bash
# Create test configuration
cat > .env.testing << 'EOF'
API_MODE=mock
LOG_LEVEL=WARNING
VECTOR_DB_PATH=./test_vectordb
EMBEDDINGS_CACHE_PATH=./test_embeddings
COLLECTION_NAME=oran_nephio_test
CHUNK_SIZE=256
RETRIEVER_K=2
AUTO_SYNC_ENABLED=false
REQUEST_TIMEOUT=10
MAX_RETRIES=1
EOF

# Create test database
API_MODE=mock VECTOR_DB_PATH=./test_vectordb python create_minimal_database.py

# Run test suite
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### 2. Continuous Integration Setup

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Chrome
      run: |
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        pip install -e .

    - name: Run tests
      run: |
        pytest tests/ -v --cov=src
      env:
        API_MODE: mock
        VECTOR_DB_PATH: ./test_vectordb

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## IDE Configuration

### 1. VS Code Configuration

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.associations": {
        "*.env*": "dotenv"
    },
    "python.envFile": "${workspaceFolder}/.env"
}
```

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug API Server",
            "type": "python",
            "request": "launch",
            "module": "src.api.main",
            "envFile": "${workspaceFolder}/.env",
            "console": "integratedTerminal"
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "envFile": "${workspaceFolder}/.env.testing",
            "console": "integratedTerminal"
        }
    ]
}
```

### 2. PyCharm Configuration

```python
# PyCharm run configuration
# Name: API Server
# Script path: src/api/main.py
# Environment variables: Load from .env file
# Python interpreter: Project venv

# Test configuration
# Target: tests/
# Pattern: pytest
# Environment variables: Load from .env.testing
```

## Troubleshooting Environment Issues

### 1. Python Environment Issues

```bash
# Check Python version
python --version
which python

# Check virtual environment
echo $VIRTUAL_ENV
pip list

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Fix import issues
pip install -e .
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. Browser Issues

```bash
# Check Chrome installation
google-chrome --version
which google-chrome

# Fix display issues (Linux)
export DISPLAY=:0
xvfb-run google-chrome --headless --dump-dom https://example.com

# Alternative: use Firefox
sudo apt install -y firefox-esl
export BROWSER=firefox
```

### 3. Permission Issues

```bash
# Fix file permissions
chmod -R 755 logs/
chmod -R 755 oran_nephio_vectordb/
chmod -R 755 embeddings_cache/

# Fix ownership (Linux)
sudo chown -R $USER:$USER ./
```

### 4. Network Issues

```bash
# Test connectivity
curl -I https://docs.nephio.org
curl -I https://www.o-ran.org

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test API connectivity
curl http://localhost:8000/health
```

### 5. Memory Issues

```bash
# Check memory usage
free -h
top

# Reduce memory usage
echo "CHUNK_SIZE=512" >> .env
echo "RETRIEVER_K=3" >> .env

# Monitor application memory
ps aux | grep python
```

This comprehensive environment setup guide provides all the necessary information to set up development and production environments for the O-RAN × Nephio RAG system, ensuring optimal performance and reliability across different deployment scenarios.