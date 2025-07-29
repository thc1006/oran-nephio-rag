---
layout: default
title: 使用說明文檔
permalink: /docs/
description: "O-RAN × Nephio RAG 系統完整使用說明文檔 - 安裝、配置、部署、API 使用指南"
---

# 📖 使用說明文檔

## 目錄
- [系統概述](#系統概述)
- [安裝指南](#安裝指南)
- [配置說明](#配置說明)
- [基本使用](#基本使用)
- [API 文檔](#api-文檔)
- [Docker 部署](#docker-部署)
- [監控配置](#監控配置)
- [故障排除](#故障排除)
- [常見問題](#常見問題)

---

## 系統概述

O-RAN × Nephio RAG 系統是一個基於檢索增強生成 (RAG) 技術的智能問答系統，專門針對 O-RAN 和 Nephio 技術文檔設計。

### 核心技術棧

- **AI 模型**: Anthropic Claude 3.5 Sonnet
- **向量資料庫**: ChromaDB
- **文本處理**: LangChain
- **異步框架**: FastAPI + AsyncIO
- **監控**: Prometheus + Grafana + Jaeger
- **容器化**: Docker + Docker Compose

### 系統特色

- 🤖 **智能問答**: 使用 Claude AI 提供精確回答
- 📚 **官方文檔**: 自動同步 O-RAN 和 Nephio 官方文檔
- 🔍 **語義搜索**: 基於向量資料庫的高效搜索
- ⚡ **異步處理**: 支援高併發查詢
- 📊 **完整監控**: 內建可觀察性工具
- 🐳 **容器化**: 一鍵部署

---

## 安裝指南

### 系統需求

- **Python**: 3.9 或更高版本
- **記憶體**: 8GB+ (推薦 16GB)
- **儲存空間**: 2GB+ 可用空間
- **網路**: 穩定的網路連接

### 1. 標準安裝

```bash
# 1. 克隆專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 2. 建立虛擬環境
python -m venv venv

# 3. 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 複製環境變數範本
cp .env.example .env
```

### 2. 開發環境安裝

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 安裝 pre-commit hooks
pre-commit install

# 執行測試確認安裝
pytest tests/ -v
```

### 3. 使用 Poetry 安裝

```bash
# 使用 Poetry 安裝
poetry install

# 進入 Poetry shell
poetry shell
```

---

## 配置說明

### 環境變數配置

編輯 `.env` 檔案，設定必要的環境變數：

```bash
# === 必填配置 ===
ANTHROPIC_API_KEY=your_claude_api_key_here

# === 可選配置 ===
# 向量資料庫設定
VECTOR_DB_PATH=./oran_nephio_vectordb
COLLECTION_NAME=oran_nephio_docs

# Claude 模型設定
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_TEMPERATURE=0.1
CLAUDE_MAX_TOKENS=4096

# 文件處理設定
CHUNK_SIZE=1024
CHUNK_OVERLAP=200

# 系統設定
LOG_LEVEL=INFO
DEBUG=false

# 監控設定
ENABLE_MONITORING=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### 配置檔案說明

#### src/config.py

系統的核心配置檔案，包含所有可調整的參數：

```python
from src.config import Config

# 建立配置實例
config = Config()

# 檢視當前配置
print(f"Claude 模型: {config.CLAUDE_MODEL}")
print(f"向量資料庫路徑: {config.VECTOR_DB_PATH}")
print(f"文檔分塊大小: {config.CHUNK_SIZE}")
```

### 進階配置

#### 自訂文檔來源

修改 `config.py` 中的 `OFFICIAL_SOURCES` 以新增或修改文檔來源：

```python
OFFICIAL_SOURCES = [
    SourceConfig(
        name="Custom O-RAN Docs",
        urls=["https://your-custom-docs.com"],
        enabled=True,
        description="自訂 O-RAN 文檔"
    )
]
```

---

## 基本使用

### 1. 初始化系統

```python
from src import create_rag_system

# 建立 RAG 系統實例
rag = create_rag_system()

# 建立向量資料庫（首次運行）
success = rag.build_vector_database()
if success:
    print("✅ 向量資料庫建立成功")
else:
    print("❌ 向量資料庫建立失敗")
```

### 2. 載入現有資料庫

```python
# 載入已建立的向量資料庫
if rag.load_existing_database():
    print("✅ 向量資料庫載入成功")
    
    # 設定問答鏈
    if rag.setup_qa_chain():
        print("✅ 問答鏈設定成功")
```

### 3. 執行查詢

```python
# 基本查詢
result = rag.query("什麼是 Nephio？")
print("回答:", result["answer"])
print("來源:", result["sources"])
print("查詢時間:", result["query_time"], "秒")

# 快速查詢（適用於簡單場景）
from src import quick_query
answer = quick_query("如何部署 O-RAN DU？")
print(answer)
```

### 4. 相似度搜索

```python
# 執行相似度搜索
documents = rag.similarity_search("Nephio 架構", k=5)
for doc in documents:
    print(f"相關文檔: {doc.metadata.get('title', 'Unknown')}")
    print(f"內容預覽: {doc.page_content[:200]}...")
```

### 5. 系統狀態檢查

```python
# 取得系統狀態
status = rag.get_system_status()
print(f"向量資料庫狀態: {'就緒' if status['vectordb_ready'] else '未就緒'}")
print(f"問答鏈狀態: {'就緒' if status['qa_chain_ready'] else '未就緒'}")
print(f"文檔數量: {status['vectordb_info']['document_count']}")
```

---

## API 文檔

### REST API

系統提供完整的 REST API 介面，基於 FastAPI 框架。

#### 啟動 API 服務

```python
from src.async_rag_system import create_fastapi_app
import uvicorn

# 建立 FastAPI 應用
app = create_fastapi_app()

# 啟動服務
uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### API 端點

##### 1. 查詢端點

```http
POST /query
Content-Type: application/json

{
    "question": "什麼是 Nephio？",
    "include_sources": true
}
```

**回應範例**:
```json
{
    "answer": "Nephio 是一個基於 Kubernetes 的網路自動化平台...",
    "sources": [
        {
            "url": "https://nephio.org/docs/",
            "title": "Nephio Documentation",
            "content_preview": "Nephio is a Kubernetes-based..."
        }
    ],
    "query_time": 1.23
}
```

##### 2. 批量查詢

```http
POST /batch-query
Content-Type: application/json

{
    "questions": [
        "什麼是 Nephio？",
        "O-RAN 的架構是什麼？"
    ]
}
```

##### 3. 健康檢查

```http
GET /health
```

**回應**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
}
```

##### 4. 系統狀態

```http
GET /status
```

### Python SDK

```python
from src.async_rag_system import AsyncORANNephioRAG

# 使用異步 RAG 系統
async def main():
    async with AsyncORANNephioRAG() as rag:
        # 單一查詢
        result = await rag.query_async("什麼是 Nephio？")
        print(result["answer"])
        
        # 批量查詢
        questions = ["Query 1", "Query 2", "Query 3"]
        results = await rag.batch_query_async(questions)
        
        for i, result in enumerate(results):
            print(f"Q{i+1}: {questions[i]}")
            print(f"A{i+1}: {result['answer']}")

# 執行
import asyncio
asyncio.run(main())
```

---

## Docker 部署

### 1. 快速部署

```bash
# 開發環境
docker-compose -f docker-compose.dev.yml up -d

# 生產環境
docker-compose -f docker-compose.prod.yml up -d

# 包含監控
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. 單容器部署

```bash
# 建立 Docker 映像
docker build -t oran-nephio-rag .

# 運行容器
docker run -d \
  --name oran-rag \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  oran-nephio-rag
```

### 3. Docker Compose 配置

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  oran-rag:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - VECTOR_DB_PATH=/app/data/vectordb
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

### 4. Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-nephio-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oran-nephio-rag
  template:
    metadata:
      labels:
        app: oran-nephio-rag
    spec:
      containers:
      - name: oran-rag
        image: oran-nephio-rag:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: oran-rag-secrets
              key: anthropic-api-key
        volumeMounts:
        - name: vector-db
          mountPath: /app/data
      volumes:
      - name: vector-db
        persistentVolumeClaim:
          claimName: vector-db-pvc
```

---

## 監控配置

### Prometheus 監控

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'oran-rag'
    static_configs:
      - targets: ['oran-rag:8000']
    metrics_path: /metrics
    scrape_interval: 30s
```

### Grafana 儀表板

系統提供預建的 Grafana 儀表板：

1. **系統概覽**: CPU、記憶體、磁碟使用率
2. **查詢監控**: 查詢次數、響應時間、錯誤率
3. **AI 模型監控**: Token 使用量、模型響應時間
4. **向量資料庫監控**: 搜索性能、資料庫大小

### 日誌收集

```python
import logging
from src.config import Config

# 配置日誌
logging.basicConfig(
    level=Config().LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/oran_rag.log'),
        logging.StreamHandler()
    ]
)
```

---

## 故障排除

### 常見錯誤

#### 1. API 金鑰錯誤

**錯誤訊息**:
```
❌ Claude 模型設定失敗: Invalid API key
```

**解決方案**:
1. 檢查 `.env` 檔案中的 `ANTHROPIC_API_KEY`
2. 確認 API 金鑰有效且有足夠額度
3. 檢查網路連接

#### 2. 記憶體不足

**錯誤訊息**:
```
❌ 記憶體不足，無法建立向量資料庫
```

**解決方案**:
1. 減少 `CHUNK_SIZE` 設定
2. 增加系統記憶體
3. 使用 Docker 限制記憶體使用

#### 3. 向量資料庫建立失敗

**錯誤訊息**:
```
❌ 建立向量資料庫時發生未預期的錯誤
```

**解決方案**:
1. 檢查磁碟空間
2. 確認網路連接
3. 檢查文檔來源可用性

### 除錯模式

```bash
# 啟用除錯模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 執行系統
python -c "from src import create_rag_system; rag = create_rag_system()"
```

### 日誌檢查

```bash
# 檢查應用程式日誌
tail -f logs/oran_nephio_rag.log

# Docker 日誌
docker-compose logs -f oran-rag-app

# 檢查系統資源
docker stats
```

---

## 常見問題

### Q: 如何更新向量資料庫？

A: 使用以下代碼更新資料庫：
```python
from src import create_rag_system
rag = create_rag_system()
success = rag.update_database()
```

### Q: 如何自訂 AI 模型溫度？

A: 在 `.env` 檔案中設定：
```bash
CLAUDE_TEMPERATURE=0.3  # 0-1 之間，越小越保守
```

### Q: 如何增加新的文檔來源？

A: 修改 `src/config.py` 中的 `OFFICIAL_SOURCES` 配置。

### Q: 如何優化查詢速度？

A: 
1. 調整 `RETRIEVER_K` 參數減少檢索文檔數量
2. 增加系統記憶體
3. 使用 SSD 儲存向量資料庫

### Q: 如何部署到雲端？

A: 支援部署到：
- AWS ECS/EKS
- Google Cloud Run/GKE  
- Azure Container Instances/AKS
- 任何支援 Docker 的雲端平台

### Q: 如何監控 API 使用量？

A: 查看 Grafana 儀表板或使用 Prometheus 查詢：
```promql
rate(http_requests_total[5m])
```

---

## 技術支援

如果遇到問題或需要協助：

- 📧 **Email**: [dev-team@company.com](mailto:dev-team@company.com)
- 🐛 **Issue 回報**: [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
- 💬 **技術討論**: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)
- 📖 **完整文檔**: [Read the Docs](https://oran-nephio-rag.readthedocs.io/)

---

*最後更新: 2024年1月*