# 🚀 O-RAN × Nephio RAG 系統 - 快速部署指南

## ✅ 系統狀態

**系統已驗證可正常運行！** 支援多種部署模式，從測試到生產環境。

## 🎯 部署選項

### 選項 1: 立即測試 (Mock 模式) - 推薦新手

**優點**: 無需 API 金鑰，5 分鐘內可運行
**適用**: 系統測試、功能驗證、開發環境

```bash
# 1. 下載專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 2. 安裝 Python 依賴
pip install python-dotenv requests beautifulsoup4 lxml
pip install langchain langchain-community langchain-anthropic
pip install sentence-transformers chromadb

# 3. 設定 Mock 模式
echo "API_MODE=mock" > .env

# 4. 建立測試資料庫
python create_minimal_database.py

# 5. 啟動系統
python main.py
```

### 選項 2: 生產部署 (Anthropic API)

**優點**: 最高品質 AI 回答
**需求**: Anthropic API 金鑰
**適用**: 生產環境、正式服務

```bash
# 1-2 步驟同上

# 3. 設定生產模式
echo "API_MODE=anthropic" > .env
echo "ANTHROPIC_API_KEY=your-actual-api-key" >> .env

# 4. 建立完整資料庫 (可選)
python -c "
from src.oran_nephio_rag import ORANNephioRAG
rag = ORANNephioRAG()
rag.build_vector_database()
"

# 5. 啟動系統
python main.py
```

### 選項 3: Docker 部署

**優點**: 環境隔離，易於管理
**適用**: 容器化環境、雲端部署

```bash
# 開發環境
docker-compose -f docker-compose.dev.yml up -d

# 生產環境
docker-compose -f docker-compose.prod.yml up -d

# 檢查狀態
docker-compose ps
docker-compose logs -f
```

### 選項 4: 本地模型部署

**優點**: 完全離線，無外部依賴
**需求**: Ollama 服務
**適用**: 內網環境、隱私要求高的場景

```bash
# 1. 安裝 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 下載模型
ollama pull llama2

# 3. 設定本地模式
echo "API_MODE=local" > .env
echo "LOCAL_MODEL_URL=http://localhost:11434" >> .env
echo "LOCAL_MODEL_NAME=llama2" >> .env

# 4. 啟動系統
python main.py
```

## 🔧 環境配置

### 基本配置 (.env 檔案)

```bash
# API 模式選擇
API_MODE=mock                    # mock/anthropic/local/puter

# Anthropic 設定 (生產模式)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_TEMPERATURE=0.1

# 本地模型設定
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama2

# 系統設定
VECTOR_DB_PATH=./oran_nephio_vectordb
LOG_LEVEL=INFO
CHUNK_SIZE=1024
```

### 進階配置

```bash
# 檢索設定
RETRIEVER_K=6                    # 檢索結果數量
RETRIEVER_FETCH_K=15            # 候選檢索數量
RETRIEVER_LAMBDA_MULT=0.7       # MMR 多樣性參數

# 效能設定
MAX_RETRIES=3                   # 最大重試次數
REQUEST_TIMEOUT=30              # 請求超時時間
CHUNK_OVERLAP=200               # 文字塊重疊字元數

# 監控設定
AUTO_SYNC_ENABLED=true          # 自動同步
SYNC_INTERVAL_HOURS=24          # 同步間隔
```

## 🧪 部署驗證

### 快速驗證

```bash
# 系統演示
python demo_system.py

# 完整測試
python test_final_system.py

# 基本功能測試
python test_basic_imports.py
```

### 預期輸出

```
🚀 O-RAN × Nephio RAG System Demo
==================================================

1️⃣ Configuration Status:
   ✅ API Mode: mock
   ✅ Vector DB: ./oran_nephio_vectordb
   ✅ Model: claude-3-sonnet-20240229
   ✅ Log Level: INFO

4️⃣ API Adapter Test:
   ✅ LLM Manager initialized (mock mode)
   ✅ Query successful!
   💬 Response: Nephio 是一個基於 Kubernetes 的網路自動化平台...

🎉 System Demo Complete!
```

## 🌐 雲端部署

### AWS 部署

```bash
# 使用 AWS EC2
# 1. 啟動 EC2 實例 (Ubuntu 20.04+)
# 2. 安裝 Docker
sudo apt update
sudo apt install docker.io docker-compose -y

# 3. 部署應用
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag
docker-compose -f docker-compose.prod.yml up -d
```

### Google Cloud 部署

```bash
# 使用 Google Cloud Run
# 1. 建置映像
gcloud builds submit --tag gcr.io/PROJECT-ID/oran-rag

# 2. 部署服務
gcloud run deploy --image gcr.io/PROJECT-ID/oran-rag \
  --platform managed \
  --set-env-vars API_MODE=anthropic,ANTHROPIC_API_KEY=your-key
```

### Azure 部署

```bash
# 使用 Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name oran-rag \
  --image your-registry/oran-rag:latest \
  --environment-variables API_MODE=mock \
  --ports 8000
```

## 📊 監控與維護

### 健康檢查

```bash
# HTTP 健康檢查端點
curl http://localhost:8000/health

# 系統狀態檢查
python -c "
from src.oran_nephio_rag import ORANNephioRAG
rag = ORANNephioRAG()
status = rag.get_system_status()
print(f'Vector DB Ready: {status.get(\"vectordb_ready\")}')
"
```

### 日誌監控

```bash
# 應用程式日誌
tail -f logs/oran_nephio_rag.log

# Docker 日誌
docker-compose logs -f oran-rag-app

# 系統資源監控
docker stats
```

### 資料庫維護

```bash
# 更新向量資料庫
python -c "
from src.oran_nephio_rag import ORANNephioRAG
rag = ORANNephioRAG()
rag.update_database()
"

# 備份資料庫
cp -r oran_nephio_vectordb oran_nephio_vectordb_backup_$(date +%Y%m%d)
```

## 🔒 安全考量

### 生產環境安全

```bash
# 1. 使用環境變數而非檔案儲存 API 金鑰
export ANTHROPIC_API_KEY="your-key-here"

# 2. 限制網路存取
# 使用防火牆限制只允許必要的端口

# 3. 定期更新依賴
pip install --upgrade -r requirements.txt

# 4. 使用 HTTPS
# 在反向代理 (nginx/traefik) 中配置 SSL
```

### API 金鑰管理

```bash
# 使用 Docker Secrets
echo "your-api-key" | docker secret create anthropic_key -

# 使用 Kubernetes Secrets
kubectl create secret generic anthropic-key \
  --from-literal=api-key=your-api-key
```

## 🚨 故障排除

### 常見問題快速修復

```bash
# 問題 1: 依賴安裝失敗
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 問題 2: 向量資料庫為空
python create_minimal_database.py

# 問題 3: 記憶體不足
# 減少 CHUNK_SIZE 或增加系統記憶體
echo "CHUNK_SIZE=512" >> .env

# 問題 4: API 連接失敗
# 切換到 Mock 模式測試
echo "API_MODE=mock" > .env
```

### 支援資源

- 📧 **技術支援**: dev-team@company.com
- 🐛 **問題回報**: [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
- 📖 **完整文檔**: [README.md](README.md)
- 💬 **社群討論**: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)

---

## 🎉 部署成功！

恭喜！您的 O-RAN × Nephio RAG 系統已成功部署。

**下一步**:
1. 測試系統功能: `python demo_system.py`
2. 開始提問關於 O-RAN 和 Nephio 的問題
3. 根據需求調整配置參數
4. 考慮升級到生產模式以獲得更好的 AI 回答品質

**系統已就緒，開始探索 O-RAN 和 Nephio 的世界吧！** 🚀