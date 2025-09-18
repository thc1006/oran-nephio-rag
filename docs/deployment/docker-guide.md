# Docker Deployment Guide

This guide covers containerization and Docker deployment options for the O-RAN × Nephio RAG system.

## Table of Contents

- [Quick Start with Docker](#quick-start-with-docker)
- [Docker Compose Configurations](#docker-compose-configurations)
- [Custom Docker Builds](#custom-docker-builds)
- [Production Deployment](#production-deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling and Load Balancing](#scaling-and-load-balancing)
- [Troubleshooting](#troubleshooting)

## Quick Start with Docker

### Prerequisites

```bash
# Install Docker and Docker Compose
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# CentOS/RHEL
sudo yum install -y docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### Development Environment

```bash
# Clone repository
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f oran-rag-app

# Test API
curl http://localhost:8000/health
```

### Production Environment

```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# With monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Check all services
docker-compose -f docker-compose.prod.yml ps
```

## Docker Compose Configurations

### Development Configuration (docker-compose.dev.yml)

```yaml
version: '3.8'

services:
  oran-rag-app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    environment:
      - API_MODE=mock
      - LOG_LEVEL=DEBUG
      - BROWSER_HEADLESS=false
      - VECTOR_DB_PATH=/app/data/vectordb
      - EMBEDDINGS_CACHE_PATH=/app/data/embeddings
    volumes:
      - ./oran_nephio_vectordb:/app/data/vectordb
      - ./logs:/app/logs
      - ./embeddings_cache:/app/data/embeddings
      - .:/app/src  # Mount source for development
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Production Configuration (docker-compose.prod.yml)

```yaml
version: '3.8'

services:
  oran-rag-app:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"
    environment:
      - API_MODE=browser
      - PUTER_MODEL=claude-sonnet-4
      - BROWSER_HEADLESS=true
      - LOG_LEVEL=INFO
      - VECTOR_DB_PATH=/app/data/vectordb
      - EMBEDDINGS_CACHE_PATH=/app/data/embeddings
      - API_WORKERS=4
    volumes:
      - oran_vectordb:/app/data/vectordb
      - oran_logs:/app/logs
      - oran_embeddings:/app/data/embeddings
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - oran-rag-app
    restart: unless-stopped

  # Redis for caching
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  oran_vectordb:
  oran_logs:
  oran_embeddings:
  redis_data:
```

### Monitoring Configuration (docker-compose.monitoring.yml)

```yaml
version: '3.8'

services:
  # Main application
  oran-rag-app:
    extends:
      file: docker-compose.prod.yml
      service: oran-rag-app
    environment:
      - METRICS_PORT=8000
      - JAEGER_AGENT_HOST=jaeger
      - OTLP_ENDPOINT=http://jaeger:14268/api/traces

  # Prometheus monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  # Grafana dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    restart: unless-stopped

  # Jaeger tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    restart: unless-stopped

  # Log aggregation
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    restart: unless-stopped

  # Log shipping
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
      - oran_logs:/var/log/oran:ro
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
  oran_logs:
    external: true
```

## Custom Docker Builds

### Multi-stage Dockerfile

```dockerfile
# Multi-stage build for O-RAN × Nephio RAG system
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Development stage
FROM base as development

# Install Chrome for browser automation
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install development dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements*.txt ./
RUN pip install -r requirements-dev.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R app:app /app

USER app

# Create necessary directories
RUN mkdir -p /app/logs /app/data/vectordb /app/data/embeddings

EXPOSE 8000

CMD ["python", "-m", "src.api.main"]

# Production stage
FROM base as production

# Install Chrome for browser automation
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Set ownership
RUN chown -R app:app /app

USER app

# Create necessary directories
RUN mkdir -p /app/logs /app/data/vectordb /app/data/embeddings

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "src.api.main:app"]
```

### Custom Build Commands

```bash
# Build development image
docker build -t oran-rag:dev --target development .

# Build production image
docker build -t oran-rag:prod --target production .

# Build with specific tag
docker build -t oran-rag:v1.0.0 .

# Build with build args
docker build --build-arg PYTHON_VERSION=3.11 -t oran-rag:custom .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t oran-rag:multi .
```

## Production Deployment

### Environment Configuration

Create production environment file:

```bash
# .env.production
API_MODE=browser
PUTER_MODEL=claude-sonnet-4
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=120

# Database settings
VECTOR_DB_PATH=/app/data/vectordb
EMBEDDINGS_CACHE_PATH=/app/data/embeddings
COLLECTION_NAME=oran_nephio_production

# Performance settings
API_WORKERS=4
CHUNK_SIZE=1024
RETRIEVER_K=6
MAX_TOKENS=4000

# Security settings
VERIFY_SSL=true
LOG_LEVEL=INFO

# Monitoring
METRICS_PORT=8000
JAEGER_AGENT_HOST=jaeger
OTLP_ENDPOINT=http://jaeger:14268/api/traces
```

### Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream oran_rag_backend {
        server oran-rag-app:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=search:10m rate=20r/m;

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # API endpoints
        location /api/v1/query {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://oran_rag_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_timeout 300s;
        }

        location /api/v1/query/search {
            limit_req zone=search burst=10 nodelay;
            proxy_pass http://oran_rag_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://oran_rag_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint (no rate limiting)
        location /health {
            proxy_pass http://oran_rag_backend;
            access_log off;
        }

        # Metrics endpoint (restrict access)
        location /metrics {
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
            proxy_pass http://oran_rag_backend;
        }
    }
}
```

### SSL Certificate Setup

```bash
# Generate self-signed certificate for testing
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/CN=localhost"

# For production, use Let's Encrypt
# Install certbot and generate certificates
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'oran-rag-api'
    static_configs:
      - targets: ['oran-rag-app:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "O-RAN × Nephio RAG System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Query Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

### Log Configuration

```yaml
# monitoring/loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

## Scaling and Load Balancing

### Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Create overlay network
docker network create -d overlay oran-rag-network

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml oran-rag

# Scale services
docker service scale oran-rag_app=3
```

### Docker Swarm Configuration

```yaml
# docker-compose.swarm.yml
version: '3.8'

services:
  oran-rag-app:
    image: oran-rag:prod
    networks:
      - oran-rag-network
    environment:
      - API_MODE=browser
      - PUTER_MODEL=claude-sonnet-4
    volumes:
      - oran_vectordb:/app/data/vectordb
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    networks:
      - oran-rag-network
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager

networks:
  oran-rag-network:
    driver: overlay

volumes:
  oran_vectordb:
    driver: local
```

### Kubernetes Alternative

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-rag-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oran-rag-app
  template:
    metadata:
      labels:
        app: oran-rag-app
    spec:
      containers:
      - name: oran-rag
        image: oran-rag:prod
        ports:
        - containerPort: 8000
        env:
        - name: API_MODE
          value: "browser"
        - name: PUTER_MODEL
          value: "claude-sonnet-4"
        resources:
          limits:
            memory: "4Gi"
            cpu: "2000m"
          requests:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Troubleshooting

### Container Debugging

```bash
# Check container logs
docker logs oran-rag-app

# Follow logs in real-time
docker logs -f oran-rag-app

# Execute commands in container
docker exec -it oran-rag-app bash

# Check container stats
docker stats oran-rag-app

# Inspect container
docker inspect oran-rag-app
```

### Common Issues

#### 1. Container Memory Issues

```bash
# Check memory usage
docker stats --no-stream

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G

# Use swap if needed (not recommended for production)
```

#### 2. Volume Permissions

```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./oran_nephio_vectordb
sudo chown -R 1000:1000 ./logs

# Check volume mounts
docker inspect oran-rag-app | jq '.[0].Mounts'
```

#### 3. Network Connectivity

```bash
# Test network connectivity
docker exec oran-rag-app curl localhost:8000/health

# Check Docker networks
docker network ls
docker network inspect bridge
```

#### 4. Browser Automation in Containers

```bash
# Ensure headless mode is enabled
API_MODE=browser
BROWSER_HEADLESS=true

# Check Chrome installation in container
docker exec oran-rag-app google-chrome --version

# Debug browser issues
docker exec oran-rag-app google-chrome --headless --dump-dom https://example.com
```

### Performance Optimization

```bash
# Use multi-stage builds to reduce image size
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Use .dockerignore to exclude unnecessary files
echo "__pycache__" >> .dockerignore
echo "*.pyc" >> .dockerignore
echo ".git" >> .dockerignore

# Optimize container startup
# Use non-root user
# Minimize layers in Dockerfile
```

This comprehensive Docker deployment guide provides everything needed to containerize and deploy the O-RAN × Nephio RAG system in various environments, from development to production with full monitoring and scaling capabilities.