# Docker 部署詳細指南

本指南將詳細說明如何使用 Docker 和 Docker Compose 部署 O-RAN × Nephio RAG 系統。

## 📋 前置需求

### 軟體需求

- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **作業系統**: Linux, macOS, Windows 10/11 with WSL2
- **記憶體**: 最少 4GB，建議 8GB+
- **儲存空間**: 最少 5GB 可用空間

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

# 編輯環境變數
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
      - API_MODE=browser
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
      - API_MODE=browser
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

# Install system dependencies for browser automation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    unzip \
    # Chrome dependencies
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Development stage
FROM base as development
RUN pip install -r requirements.txt
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

## 🔄 部署流程詳解

### 1. 環境變數配置

建立 `.env` 檔案：

```bash
# API 配置 - 使用瀏覽器模式
API_MODE=browser

# 資料庫配置
VECTOR_DB_PATH=/app/data/vectordb
COLLECTION_NAME=oran_nephio_official

# 應用配置
LOG_LEVEL=INFO
WORKERS=4

# 監控配置
ENABLE_MONITORING=true
METRICS_PORT=9090

# 瀏覽器配置
CHROME_HEADLESS=true
CHROME_NO_SANDBOX=true
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

### 3. 服務部署步驟

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
      - API_MODE=browser
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

# 檢查健康狀態
docker-compose exec oran-rag-app curl http://localhost:8000/health

# 檢查瀏覽器狀態
docker-compose exec oran-rag-app ps aux | grep chrome
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

### 瀏覽器優化

```yaml
  oran-rag-app:
    environment:
      - CHROME_HEADLESS=true
      - CHROME_NO_SANDBOX=true
      - CHROME_DISABLE_DEV_SHM_USAGE=true
      - CHROME_WINDOW_SIZE=1920,1080
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

2. **瀏覽器自動化失敗**
   ```bash
   # 檢查 Chrome 安裝
   docker-compose exec oran-rag-app google-chrome --version
   
   # 檢查 Chrome 權限
   docker-compose exec oran-rag-app ls -la /usr/bin/google-chrome
   
   # 測試瀏覽器啟動
   docker-compose exec oran-rag-app python -c "from selenium import webdriver; from selenium.webdriver.chrome.options import Options; options = Options(); options.add_argument('--headless'); driver = webdriver.Chrome(options=options); print('Browser test OK'); driver.quit()"
   ```

3. **記憶體不足**
   ```bash
   # 檢查資源使用
   docker stats
   
   # 調整記憶體限制
   # 在 docker-compose.yml 中修改 memory 設定
   ```

### 日誌分析

```bash
# 查看應用日誌
docker-compose logs -f --tail=100 oran-rag-app

# 查看系統日誌
docker-compose exec oran-rag-app tail -f /app/logs/oran_nephio_rag.log

# 查看瀏覽器日誌
docker-compose exec oran-rag-app tail -f /app/logs/browser.log
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
3. 聯繫開發團隊: hctsai@linux.com

---

**Happy Deploying! 🚀**