# Docker 部署詳細指南

本指南將詳細說明如何使用 Docker 和 Docker Compose 部署 O-RAN × Nephio RAG 系統。

## 📋 前置需求

### 軟體需求

- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **作業系統**: Linux, macOS, Windows 10/11 with WSL2
- **記憶體**: 最少 8GB，建議 16GB+
- **儲存空間**: 最少 10GB 可用空間

### 環境準備

```bash
# 檢查 Docker 版本
docker --version
docker-compose --version

# 確保 Docker 服務運行
sudo systemctl start docker  # Linux
# 或者啟動 Docker Desktop (Windows/Mac)
```

## 🚀 快速部署

### 1. 基本部署 (開發環境)

```bash
# 克隆專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 複製環境變數檔案
cp .env.example .env

# 編輯環境變數 (必須設定 ANTHROPIC_API_KEY)
nano .env

# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d
```

### 2. 生產環境部署

```bash
# 使用生產配置
docker-compose -f docker-compose.prod.yml up -d

# 檢查服務狀態
docker-compose -f docker-compose.prod.yml ps
```

### 3. 完整監控環境

```bash
# 啟動包含監控的完整環境
docker-compose -f docker-compose.monitoring.yml up -d

# 檢查所有服務狀態
docker-compose -f docker-compose.monitoring.yml ps
```

## 🔧 Docker Compose 檔案詳解

### docker-compose.dev.yml (開發環境)

```yaml
version: '3.8'

services:
  oran-rag-app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: oran-rag-dev
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - VECTOR_DB_PATH=/app/data/vectordb
      - LOG_LEVEL=DEBUG
    volumes:
      - ./src:/app/src
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - oran-rag-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: oran-rag-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - oran-rag-network
    restart: unless-stopped

volumes:
  redis_data:

networks:
  oran-rag-network:
    driver: bridge
```

### docker-compose.prod.yml (生產環境)

```yaml
version: '3.8'

services:
  oran-rag-app:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: oran-rag-prod
    ports:
      - "80:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - CLAUDE_MODEL=${CLAUDE_MODEL:-claude-3-sonnet-20240229}
      - VECTOR_DB_PATH=/app/data/vectordb
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - WORKERS=${WORKERS:-4}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - oran-rag-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  nginx:
    image: nginx:alpine
    container_name: oran-rag-nginx
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./docker/nginx/prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - oran-rag-app
    networks:
      - oran-rag-network
    restart: always

  redis:
    image: redis:7-alpine
    container_name: oran-rag-redis
    volumes:
      - redis_data:/data
    networks:
      - oran-rag-network
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M

volumes:
  redis_data:

networks:
  oran-rag-network:
    driver: bridge
```

## 🖼️ Dockerfile 說明

### 主要 Dockerfile

```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Development stage
FROM base as development
RUN pip install -r requirements-dev.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]

# Production stage  
FROM base as production
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY main.py pyproject.toml ./
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "main:app"]
```

### Dockerfile.production (最佳化版本)

```dockerfile
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production image
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser main.py pyproject.toml ./

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "main:app"]
```

## 🔄 部署流程詳解

### 1. 環境變數配置

建立 `.env` 檔案：

```bash
# API 配置
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# 模型配置
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.1

# 資料庫配置
VECTOR_DB_PATH=/app/data/vectordb
COLLECTION_NAME=oran_nephio_official

# 應用配置
LOG_LEVEL=INFO
WORKERS=4

# 監控配置
ENABLE_MONITORING=true
METRICS_PORT=9090
```

### 2. 資料持久化設定

```bash
# 建立資料目錄
mkdir -p ./data/{vectordb,logs,cache}
mkdir -p ./ssl

# 設定權限
chmod 755 ./data
chmod 644 ./ssl/*  # SSL 憑證檔案
```

### 3. 網路配置

```bash
# 建立專用網路
docker network create oran-rag-network

# 檢查網路
docker network ls
docker network inspect oran-rag-network
```

### 4. 服務部署步驟

```bash
# 1. 拉取最新映像
docker-compose -f docker-compose.prod.yml pull

# 2. 建構自定義映像
docker-compose -f docker-compose.prod.yml build

# 3. 啟動服務 (分階段)
docker-compose -f docker-compose.prod.yml up -d redis
sleep 10
docker-compose -f docker-compose.prod.yml up -d oran-rag-app
sleep 30
docker-compose -f docker-compose.prod.yml up -d nginx

# 4. 檢查服務狀態
docker-compose -f docker-compose.prod.yml ps
```

## 📊 監控配置

### docker-compose.monitoring.yml

完整的監控堆疊包含：

- **Prometheus**: 指標收集
- **Grafana**: 儀表板視覺化
- **Jaeger**: 分散式追蹤
- **Alertmanager**: 警報管理

```yaml
version: '3.8'

services:
  # RAG 應用
  oran-rag-app:
    build: .
    environment:
      - ENABLE_MONITORING=true
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:14268
    depends_on:
      - prometheus
      - jaeger
    networks:
      - monitoring

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml
    networks:
      - monitoring

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - ./monitoring/grafana-dashboard.json:/var/lib/grafana/dashboards/
      - ./monitoring/grafana-datasources.yml:/etc/grafana/provisioning/datasources/
    networks:
      - monitoring

  # Jaeger
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge
```

## 🛠️ 常用操作指令

### 服務管理

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟特定服務
docker-compose restart oran-rag-app

# 查看日誌
docker-compose logs -f oran-rag-app

# 進入容器
docker-compose exec oran-rag-app bash
```

### 監控和除錯

```bash
# 檢查容器狀態
docker-compose ps

# 檢查容器資源使用
docker stats

# 檢查網路連接
docker-compose exec oran-rag-app curl http://redis:6379

# 檢查健康狀態
docker-compose exec oran-rag-app curl http://localhost:8000/health
```

### 備份和恢復

```bash
# 備份向量資料庫
docker-compose exec oran-rag-app tar -czf /app/backup/vectordb-$(date +%Y%m%d).tar.gz /app/data/vectordb

# 恢復資料庫
docker-compose exec oran-rag-app tar -xzf /app/backup/vectordb-20240115.tar.gz -C /app/data/
```

## 🔧 效能調優

### 資源限制設定

```yaml
services:
  oran-rag-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    environment:
      - WORKERS=4
      - WORKER_CONNECTIONS=1000
      - MAX_REQUESTS=1000
      - MAX_REQUESTS_JITTER=100
```

### 快取配置

```yaml
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
```

## 🔒 安全配置

### SSL/TLS 設定

```bash
# 生成自簽憑證 (開發用)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./ssl/private.key \
    -out ./ssl/certificate.crt

# 生產環境使用 Let's Encrypt
certbot certonly --webroot -w /var/www/html -d your-domain.com
```

### Nginx 安全配置

```nginx
# docker/nginx/prod.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    
    # 安全標頭
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location / {
        proxy_pass http://oran-rag-app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚨 故障排除

### 常見問題

1. **容器無法啟動**
   ```bash
   # 檢查日誌
   docker-compose logs oran-rag-app
   
   # 檢查映像
   docker images
   
   # 重新建構
   docker-compose build --no-cache
   ```

2. **記憶體不足**
   ```bash
   # 檢查資源使用
   docker stats
   
   # 調整記憶體限制
   # 在 docker-compose.yml 中修改 memory 設定
   ```

3. **網路連接問題**
   ```bash
   # 檢查網路
   docker network ls
   docker network inspect oran-rag-network
   
   # 測試連接
   docker-compose exec oran-rag-app ping redis
   ```

### 日誌分析

```bash
# 查看應用日誌
docker-compose logs -f --tail=100 oran-rag-app

# 查看系統日誌
docker-compose exec oran-rag-app tail -f /app/logs/oran_nephio_rag.log

# 查看 Nginx 日誌
docker-compose logs nginx
```

## 📈 擴展和集群部署

### Docker Swarm 部署

```bash
# 初始化 Swarm
docker swarm init

# 部署服務堆疊
docker stack deploy -c docker-compose.prod.yml oran-rag-stack

# 檢查服務
docker service ls
docker service ps oran-rag-stack_oran-rag-app
```

### Kubernetes 部署

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
      - name: app
        image: oran-rag:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: oran-rag-secrets
              key: anthropic-api-key
```

## 🔄 CI/CD 整合

### GitHub Actions 範例

```yaml
# .github/workflows/docker-deploy.yml
name: Docker Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v3
      with:
        context: .
        push: true
        tags: oran-rag:latest
    
    - name: Deploy to production
      run: |
        docker-compose -f docker-compose.prod.yml pull
        docker-compose -f docker-compose.prod.yml up -d
```

## 📞 支援

如果在 Docker 部署過程中遇到問題，請：

1. 檢查本指南的故障排除章節
2. 查看 [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
3. 聯繫開發團隊: dev-team@company.com

---

**Happy Deploying! 🚀**