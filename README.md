# O-RAN × Nephio RAG 系統

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI/CD](https://github.com/company/oran-nephio-rag/workflows/CI/badge.svg)](https://github.com/company/oran-nephio-rag/actions)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

基於檢索增強生成 (RAG) 技術的智能問答系統，專門針對 O-RAN 和 Nephio 技術文檔設計。

## 🚀 專案特色

- **智能問答**: 使用 Claude AI 模型提供精確的技術問答
- **官方文檔集成**: 自動抓取並處理 O-RAN 和 Nephio 官方文檔
- **語義搜索**: 基於向量資料庫的高效語義搜索
- **異步處理**: 支援高併發的異步處理模式
- **完整監控**: 內建 OpenTelemetry、Prometheus 和 Grafana 監控
- **容器化部署**: 完整的 Docker 和 Docker Compose 支援
- **自動化 CI/CD**: GitHub Actions 自動化測試和部署

## 📋 系統需求

- Python 3.9+
- 8GB+ RAM (推薦 16GB)
- 2GB+ 可用儲存空間
- 穩定的網路連接 (用於抓取文檔和 AI API 調用)

## 🔑 必要條件

1. **Anthropic API Key**: 註冊 [Anthropic](https://www.anthropic.com) 並取得 API 金鑰
2. **環境變數設定**: 複製 `.env.example` 為 `.env` 並配置必要參數

## ⚡ 快速開始

### 1. 安裝與設定

```bash
# 克隆專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 複製環境變數範本
cp .env.example .env
# 編輯 .env 並設定 ANTHROPIC_API_KEY
```

### 2. 初始化系統

```bash
# 建立向量資料庫
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.build_vector_database()
print('✅ 向量資料庫建立完成')
"
```

### 3. 基本使用

```python
from src import quick_query

# 快速問答
answer = quick_query("如何使用 Nephio 進行 O-RAN 網路功能的擴展？")
print(answer)
```

### 4. 完整 API 使用

```python
from src import create_rag_system

# 建立 RAG 系統
rag = create_rag_system()

# 載入現有資料庫
rag.load_existing_database()

# 設定問答鏈
rag.setup_qa_chain()

# 執行查詢
result = rag.query("什麼是 Nephio？")
print("回答:", result["answer"])
print("來源:", result["sources"])
```

## 🐳 Docker 部署

### 快速部署

```bash
# 開發環境
docker-compose -f docker-compose.dev.yml up -d

# 生產環境
docker-compose -f docker-compose.prod.yml up -d

# 包含監控系統
docker-compose -f docker-compose.monitoring.yml up -d
```

### 詳細 Docker 部署指南

請參閱 [Docker 部署指南](docs/DOCKER_DEPLOYMENT.md) 了解完整的容器化部署流程。

## 🔧 配置說明

### 環境變數

| 變數名 | 必填 | 預設值 | 說明 |
|--------|------|--------|------|
| `ANTHROPIC_API_KEY` | ✅ | - | Anthropic API 金鑰 |
| `VECTOR_DB_PATH` | ❌ | `./oran_nephio_vectordb` | 向量資料庫路徑 |
| `CLAUDE_MODEL` | ❌ | `claude-3-sonnet-20240229` | Claude 模型名稱 |
| `CLAUDE_TEMPERATURE` | ❌ | `0.1` | AI 生成溫度 (0-1) |
| `CHUNK_SIZE` | ❌ | `1024` | 文件分塊大小 |
| `LOG_LEVEL` | ❌ | `INFO` | 日誌等級 |

### 完整配置選項

查看 `src/config.py` 了解所有可用的配置選項。

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行單元測試
pytest tests/ -m "unit"

# 執行整合測試
pytest tests/ -m "integration"

# 生成測試覆蓋率報告
pytest --cov=src --cov-report=html
```

## 📊 監控與可觀察性

系統內建完整的監控支援：

- **Metrics**: Prometheus 指標收集
- **Tracing**: Jaeger 分散式追蹤
- **Logging**: 結構化日誌記錄
- **Health Checks**: 健康檢查端點

### 監控儀表板

啟動監控服務後，可通過以下端點訪問：

- Grafana 儀表板: http://localhost:3000
- Prometheus: http://localhost:9090
- Jaeger UI: http://localhost:16686

## 🚀 效能最佳化

### 異步模式

使用異步模式處理高併發請求：

```python
from src import AsyncORANNephioRAG, async_rag_system

# 異步上下文管理器
async with async_rag_system() as rag:
    # 單一查詢
    result = await rag.query_async("Nephio 架構是什麼？")
    
    # 批量查詢
    queries = ["Query 1", "Query 2", "Query 3"]
    results = await rag.batch_query_async(queries)
```

### 快取策略

- **嵌入模型快取**: 自動快取預訓練模型
- **向量搜索快取**: 快取常見查詢結果
- **HTTP 快取**: 快取文檔載入結果

## 🛠️ 開發指南

### 開發環境設定

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 安裝 pre-commit hooks
pre-commit install

# 執行代碼格式化
black src/ tests/
isort src/ tests/

# 執行代碼檢查
flake8 src/ tests/
mypy src/
```

### 專案結構

```
oran-nephio-rag/
├── src/                          # 主要源碼
│   ├── __init__.py              # 模組初始化
│   ├── config.py                # 配置管理
│   ├── document_loader.py       # 文檔載入器
│   ├── oran_nephio_rag.py      # 核心 RAG 系統
│   ├── async_rag_system.py     # 異步 RAG 系統
│   └── monitoring.py           # 監控系統
├── tests/                       # 測試代碼
├── docker/                      # Docker 相關檔案
├── monitoring/                  # 監控配置
├── docs/                        # 文檔
├── examples/                    # 使用範例
├── docker-compose.*.yml         # Docker Compose 配置
├── Dockerfile                   # Docker 映像檔
├── requirements.txt             # Python 依賴
├── pyproject.toml              # 專案配置
└── README.md                   # 專案說明
```

## 📖 API 文檔

### 核心類別

- **`ORANNephioRAG`**: 主要的 RAG 系統類別
- **`DocumentLoader`**: 文檔載入和處理
- **`VectorDatabaseManager`**: 向量資料庫管理
- **`QueryProcessor`**: 查詢處理和 AI 整合

### API 端點 (使用 FastAPI)

```python
# 啟動 FastAPI 服務
from src.async_rag_system import create_fastapi_app
app = create_fastapi_app()

# API 端點:
# POST /query - 單一查詢
# POST /batch-query - 批量查詢
# GET /health - 健康檢查
# GET /status - 系統狀態
```

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 代碼風格

- 使用 Black 進行代碼格式化
- 遵循 PEP 8 規範
- 使用類型提示
- 撰寫有意義的測試

## 🔍 故障排除

### 常見問題

1. **API 金鑰錯誤**
   ```
   解決方案: 檢查 .env 檔案中的 ANTHROPIC_API_KEY 是否正確設定
   ```

2. **記憶體不足**
   ```
   解決方案: 減少 CHUNK_SIZE 或增加系統記憶體
   ```

3. **向量資料庫建立失敗**
   ```
   解決方案: 檢查磁碟空間和網路連接
   ```

### 日誌檢查

```bash
# 檢查應用程式日誌
tail -f logs/oran_nephio_rag.log

# Docker 日誌
docker-compose logs -f oran-rag-app
```

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- [Nephio Project](https://nephio.org/) - 網路自動化平台
- [O-RAN Alliance](https://www.o-ran.org/) - 開放無線接取網路
- [Anthropic](https://www.anthropic.com/) - Claude AI 模型
- [LangChain](https://langchain.com/) - LLM 應用框架

## 📞 支援與聯繫

- 📧 Email: dev-team@company.com
- 🐛 Issues: [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
- 📖 文檔: [完整文檔](https://oran-nephio-rag.readthedocs.io/)
- 💬 討論: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)

---

**Made with ❤️ for the Telecom and Cloud Native Community**