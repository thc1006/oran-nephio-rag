# O-RAN × Nephio RAG 系統

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![System Status](https://img.shields.io/badge/status-functional-brightgreen.svg)](#system-status)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

基於檢索增強生成 (RAG) 技術的智能問答系統，專門針對 O-RAN 和 Nephio 技術文檔設計。

## ✅ 系統狀態

**🎉 系統已驗證並可正常運行！**

- ✅ **核心功能**: 配置管理、文檔處理、向量搜索
- ✅ **Mock 模式**: 可立即測試，無需 API 金鑰
- ✅ **多 API 支援**: Anthropic Claude、本地模型、測試模式
- ✅ **向量資料庫**: ChromaDB 整合完成
- ✅ **完整架構**: 所有核心組件已就緒

## 🚀 專案特色

- **🤖 智能問答**: 支援 Claude AI、本地模型和測試模式
- **📚 官方文檔集成**: 自動處理 O-RAN 和 Nephio 技術文檔
- **🔍 語義搜索**: 基於 ChromaDB 的高效向量搜索
- **⚡ 多 API 模式**: 靈活的 API 適配器架構
- **🎭 測試友好**: 內建 Mock 模式，無需外部依賴
- **🐳 容器化就緒**: 完整的 Docker 支援
- **📊 監控整合**: 內建指標收集和健康檢查

## 📋 系統需求

- **Python**: 3.9+ (已測試至 3.13)
- **記憶體**: 4GB+ (推薦 8GB)
- **儲存空間**: 1GB+ 可用空間
- **網路**: 穩定連接 (用於下載模型和文檔)

## 🔑 環境設定

### 必要設定
```bash
# 複製環境變數範本
cp .env.example .env
```

### API 模式選擇
- **Mock 模式** (預設): 無需 API 金鑰，立即可用
- **Anthropic 模式**: 需要 `ANTHROPIC_API_KEY`
- **本地模式**: 需要本地 Ollama 服務
- **Puter 模式**: 實驗性功能

## ⚡ 快速開始

### 🚀 超級快速 (一鍵設定)

```bash
# 1. 下載專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 2. 一鍵自動設定 (推薦)
python quick_start.py

# 3. 開始使用
python main.py
```

### 🎯 方案一：手動測試 (Mock 模式)

```bash
# 1. 克隆專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 2. 建立虛擬環境 (可選)
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. 安裝核心依賴
pip install python-dotenv requests beautifulsoup4 lxml
pip install langchain langchain-community langchain-anthropic
pip install sentence-transformers chromadb

# 4. 設定 Mock 模式
echo "API_MODE=mock" > .env

# 5. 建立測試資料庫
python create_minimal_database.py

# 6. 運行系統
python main.py
```

### 🚀 方案二：生產模式 (需要 API 金鑰)

```bash
# 1-4 步驟同上

# 5. 設定生產模式
echo "API_MODE=anthropic" > .env
echo "ANTHROPIC_API_KEY=your-actual-api-key" >> .env

# 6. 建立完整資料庫 (可選)
python -c "
from src.oran_nephio_rag import ORANNephioRAG
rag = ORANNephioRAG()
rag.build_vector_database()
print('✅ 完整向量資料庫建立完成')
"

# 7. 運行系統
python main.py
```

### 🧪 系統驗證

```bash
# 🚀 一鍵快速開始 (推薦新手)
python quick_start.py

# 🔍 完整系統驗證
python verify_system.py

# 🎭 系統演示
python demo_system.py

# 🧪 功能測試
python test_final_system.py
```

## 💡 使用範例

### 基本問答
```python
# 在 main.py 運行後，您可以詢問：
- "什麼是 Nephio？"
- "O-RAN 架構的主要組件有哪些？"
- "如何實現網路功能的 scale-out？"
- "O2IMS 在網路功能管理中的作用是什麼？"
```

### 程式化使用
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_adapters import LLMManager
from config import Config

# 初始化系統
config = Config()
config_dict = {
    'api_key': config.ANTHROPIC_API_KEY,
    'model_name': config.CLAUDE_MODEL,
    'max_tokens': config.CLAUDE_MAX_TOKENS,
    'temperature': config.CLAUDE_TEMPERATURE
}

llm_manager = LLMManager(config_dict)

# 執行查詢
result = llm_manager.query("Nephio 如何支援 O-RAN 網路功能擴縮？")
print(result.get('answer', 'No response'))
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

### 自定義 Docker 建置

```bash
# 建置開發映像
docker build --target development -t oran-rag:dev .

# 建置生產映像
docker build --target production -t oran-rag:prod .

# 運行容器
docker run -d \
  --name oran-rag \
  -p 8000:8000 \
  -e API_MODE=mock \
  -v $(pwd)/oran_nephio_vectordb:/app/oran_nephio_vectordb \
  oran-rag:dev
```

## 🔧 配置說明

### 環境變數

| 變數名 | 必填 | 預設值 | 說明 |
|--------|------|--------|------|
| `API_MODE` | ❌ | `mock` | API 模式 (anthropic/mock/local/puter) |
| `ANTHROPIC_API_KEY` | ⚠️ | - | Anthropic API 金鑰 (生產模式必填) |
| `CLAUDE_MODEL` | ❌ | `claude-3-sonnet-20240229` | Claude 模型名稱 |
| `CLAUDE_TEMPERATURE` | ❌ | `0.1` | AI 生成溫度 (0-1) |
| `VECTOR_DB_PATH` | ❌ | `./oran_nephio_vectordb` | 向量資料庫路徑 |
| `LOG_LEVEL` | ❌ | `INFO` | 日誌等級 |
| `CHUNK_SIZE` | ❌ | `1024` | 文件分塊大小 |

### API 模式詳細說明

#### 🎭 Mock 模式 (推薦測試)
- **優點**: 無需 API 金鑰，立即可用
- **用途**: 開發測試、系統驗證
- **回應**: 預設的 O-RAN/Nephio 相關回答

#### 🤖 Anthropic 模式 (推薦生產)
- **優點**: 最高品質的 AI 回答
- **需求**: 有效的 ANTHROPIC_API_KEY
- **成本**: 按 API 使用量計費

#### 🏠 Local 模式 (離線使用)
- **優點**: 完全離線，無外部依賴
- **需求**: 本地 Ollama 服務
- **設定**: `LOCAL_MODEL_URL` 和 `LOCAL_MODEL_NAME`

#### 🧪 Puter 模式 (實驗性)
- **狀態**: 實驗性功能
- **風險**: 需要設定 `PUTER_RISK_ACKNOWLEDGED=true`
- **用途**: 研究和概念驗證

## 🧪 測試與驗證

### 系統健康檢查

```bash
# 基本系統測試
python test_basic_imports.py

# 完整功能測試
python test_final_system.py

# 系統演示
python demo_system.py

# 建立測試資料庫
python create_minimal_database.py
```

### 測試覆蓋範圍

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

## 🔍 故障排除

### 常見問題

#### 1. 依賴安裝失敗
```bash
# 解決方案：使用虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. 向量資料庫為空
```bash
# 解決方案：建立測試資料庫
python create_minimal_database.py
```

#### 3. API 金鑰錯誤
```bash
# 解決方案：檢查 .env 檔案
cat .env | grep ANTHROPIC_API_KEY
# 或使用 Mock 模式
echo "API_MODE=mock" > .env
```

#### 4. 模組導入失敗
```bash
# 解決方案：檢查 Python 路徑
python -c "import sys; print(sys.path)"
# 確保在專案根目錄執行
```

### 日誌檢查

```bash
# 檢查應用程式日誌
tail -f logs/oran_nephio_rag.log

# Docker 日誌
docker-compose logs -f oran-rag-app
```

### 系統狀態檢查

```bash
# 檢查系統狀態
python -c "
import sys, os
sys.path.insert(0, 'src')
from demo_system import demo_system
demo_system()
"
```

## 📚 文檔與資源

### 快速參考
- 🚀 **[快速部署指南](QUICK_DEPLOY.md)** - 5分鐘快速部署
- 📊 **[系統狀態報告](SYSTEM_STATUS_REPORT.md)** - 詳細系統驗證結果
- 🐳 **[Docker 部署](docker-compose.dev.yml)** - 容器化部署配置

### 開發資源
- 🎯 **[Steering Rules](.kiro/steering/)** - AI 助手指導規則
- 🧪 **[測試腳本](test_final_system.py)** - 系統功能驗證
- 📝 **[API 文檔](src/api_adapters.py)** - API 適配器說明

### 範例與演示
- 🎭 **[系統演示](demo_system.py)** - 完整功能展示
- 🔨 **[資料庫建立](create_minimal_database.py)** - 測試資料庫建立
- 🧩 **[使用範例](examples/)** - 程式化使用範例

## 🏗️ 專案架構

### 核心組件
```
src/
├── config.py              # 配置管理
├── oran_nephio_rag.py     # 主要 RAG 系統
├── document_loader.py     # 文檔處理
├── api_adapters.py        # API 適配器
└── monitoring.py          # 監控系統
```

### 資料流程
```
用戶查詢 → API適配器 → 向量搜索 → 文檔檢索 → AI生成 → 回答輸出
```

### 支援的文檔來源
- **Nephio 官方文檔**: 架構、部署、最佳實踐
- **O-RAN 規範**: 技術標準、介面定義
- **整合指南**: O-RAN × Nephio 整合文檔
- **社群資源**: 案例研究、實作經驗

## 🤝 貢獻指南

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

### 貢獻流程
1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- [Nephio Project](https://nephio.org/) - 網路自動化平台
- [O-RAN Alliance](https://www.o-ran.org/) - 開放無線接取網路
- [Anthropic](https://www.anthropic.com/) - Claude AI 模型
- [LangChain](https://langchain.com/) - LLM 應用框架
- [ChromaDB](https://www.trychroma.com/) - 向量資料庫

## 📞 支援與聯繫

- 📧 **Email**: dev-team@company.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
- 📖 **文檔**: [完整文檔](https://oran-nephio-rag.readthedocs.io/)
- 💬 **討論**: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)

---

**Made with ❤️ for the Telecom and Cloud Native Community**

**🎉 系統已驗證可正常運行 - 立即開始使用！**

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