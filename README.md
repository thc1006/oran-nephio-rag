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

<<<<<<< HEAD
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
=======
- **智能問答**: 使用先進 AI 模型提供精確的技術問答
- **官方文檔集成**: 自動抓取並處理 O-RAN 和 Nephio 官方文檔
- **語義搜索**: 基於向量資料庫的高效語義搜索
- **輕量級設計**: 優化的架構提供快速響應和卓越性能
- **完整監控**: 內建監控和日誌系統，提供全面的可觀察性
- **容器化部署**: 完整的 Docker 和 Docker Compose 支援
- **自動化 CI/CD**: GitHub Actions 自動化測試和部署

## 📋 系統需求

- Python 3.9+
- 4GB+ RAM (推薦 8GB)
- 2GB+ 可用儲存空間
- 穩定的網路連接 (用於抓取文檔和 AI 服務)
>>>>>>> edd90c420ce93ca73519222944f0b678536ed1d5

## 🔑 環境設定

<<<<<<< HEAD
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
=======
1. **環境設定**: 複製 `.env.example` 為 `.env` 並配置必要參數
2. **瀏覽器支持**: 系統使用瀏覽器自動化技術進行 AI 整合
>>>>>>> edd90c420ce93ca73519222944f0b678536ed1d5

## ⚡ 快速開始

### 🚀 超級快速 (一鍵設定)

```bash
# 1. 下載專案
git clone https://github.com/company/oran-nephio-rag.git
cd oran-nephio-rag

# 2. 一鍵自動設定 (推薦)
python quick_start.py

<<<<<<< HEAD
# 3. 開始使用
python main.py
```

### 🎯 方案一：手動測試 (Mock 模式)
=======
# 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 環境配置

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯環境變數檔案
nano .env
```

**重要環境變數：**
```bash
# API 模式設定
API_MODE=browser

# 資料庫路徑
VECTOR_DB_PATH=./oran_nephio_vectordb
COLLECTION_NAME=oran_nephio_official

# 日誌設定
LOG_LEVEL=INFO
LOG_FILE=logs/oran_nephio_rag.log

# 監控設定
ENABLE_MONITORING=true
```

### 3. 初始化系統
>>>>>>> edd90c420ce93ca73519222944f0b678536ed1d5

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

<<<<<<< HEAD
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
=======
### 4. 啟動系統

```bash
# 命令列模式
python main.py

# 或使用便捷查詢函數
python -c "
from src import quick_query
result = quick_query('什麼是 Nephio？')
print(result)
"
>>>>>>> edd90c420ce93ca73519222944f0b678536ed1d5
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

# 包含監控的完整環境
docker-compose -f docker-compose.monitoring.yml up -d
```

### 檢查服務狀態

```bash
# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f oran-rag-app

# 檢查健康狀態
curl http://localhost:8000/health
```

## 💻 使用範例

### Python API

```python
from src import create_rag_system, quick_query

# 快速查詢
answer = quick_query("如何部署 Nephio？")
print(answer)

# 完整 API 使用
rag = create_rag_system()
rag.load_existing_database()
rag.setup_qa_chain()

result = rag.query("O-RAN 的核心架構是什麼？")
print("回答:", result["answer"])
print("來源:", result["sources"])
print("查詢時間:", result["query_time"], "秒")
```

### 命令列介面

```bash
# 啟動互動式問答
python main.py

# 可用指令:
# help     - 顯示可用指令
# status   - 顯示系統狀態
# update   - 更新向量資料庫
# examples - 顯示範例問題
# clear    - 清除螢幕
# quit     - 退出程式
```

## 🏗️ 系統架構

```
┌─────────────────┐
│   使用者介面層   │  Web UI, REST API, CLI Tool
├─────────────────┤
│   應用服務層     │  RAG Engine, Query Processor, Document Loader
├─────────────────┤
│   AI 服務層      │  AI Models, Text Processing, Vector Search
├─────────────────┤
│   資料儲存層     │  Vector DB, Document Cache, Metadata Store
├─────────────────┤
│  監控可觀察性    │  Logging, Metrics, Health Checks
└─────────────────┘
```

## 📊 監控與日誌

### 系統狀態檢查

```bash
# 檢查系統狀態
python -c "
from src import create_rag_system
rag = create_rag_system()
status = rag.get_system_status()
print(f'向量資料庫: {"✅" if status["vectordb_ready"] else "❌"}')
print(f'問答鏈: {"✅" if status["qa_chain_ready"] else "❌"}')
print(f'文檔數量: {status["total_documents"]}')
"
```

### 日誌查看

```bash
# 查看應用日誌
tail -f logs/oran_nephio_rag.log

# Docker 環境日誌
docker-compose logs -f oran-rag-app
```

## 🧪 測試

```bash
# 安裝測試依賴
pip install -r requirements-dev.txt

# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_rag_system.py -v

# 生成覆蓋率報告
pytest --cov=src --cov-report=html

# 查看覆蓋率報告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🔧 故障排除

### 常見問題

1. **依賴安裝失敗**
   ```bash
   # 使用預編譯包
   pip install --only-binary=all -r requirements.txt
   
   # 或安裝編譯工具
   # Ubuntu/Debian
   sudo apt-get install build-essential python3-dev
   # macOS
   xcode-select --install
   ```

2. **模組導入錯誤**
   ```bash
   # 安裝為開發模式
   pip install -e .
   
   # 或設定 Python 路徑
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

3. **向量資料庫建立失敗**
   ```bash
   # 檢查權限
   mkdir -p oran_nephio_vectordb
   chmod 755 oran_nephio_vectordb
   
   # 檢查磁碟空間
   df -h
   ```

4. **瀏覽器自動化問題**
   ```bash
   # 檢查 Chrome 安裝
   google-chrome --version
   
   # 更新 WebDriver
   pip install --upgrade webdriver-manager
   ```

### 效能調優

```bash
# 調整工作進程數量
export WORKERS=4

# 調整記憶體限制
export MAX_MEMORY=4G

# 啟用快取
export ENABLE_CACHE=true
```

## 📚 進階配置

### 自定義文檔來源

```python
# 在 src/config.py 中添加自定義來源
CUSTOM_SOURCES = [
    {
        "name": "Custom O-RAN Docs",
        "url": "https://your-domain.com/docs",
        "type": "web",
        "enabled": True
    }
]
```

### API 模式切換

```bash
# 設定不同的 API 模式
export API_MODE=browser  # 瀏覽器模式（預設）
export API_MODE=local    # 本地模式
```

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支: `git checkout -b feature/your-feature`
3. 提交變更: `git commit -am 'Add your feature'`
4. 推送分支: `git push origin feature/your-feature`
5. 提交 Pull Request

### 開發規範

- 使用 Black 進行程式碼格式化
- 遵循 PEP 8 程式碼風格
- 為新功能添加測試
- 更新文檔

```bash
# 程式碼品質檢查
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 👤 作者資訊

**Tsai, Hsiu-Chi (thc1006)**
- Email: hctsai@linux.com
- 專案網站: [O-RAN × Nephio RAG](https://github.com/company/oran-nephio-rag)

## 🙏 致謝

- [Nephio Project](https://nephio.org/) - 網路自動化平台
- [O-RAN Alliance](https://www.o-ran.org/) - 開放 RAN 標準
- [Python](https://python.org/) - 程式語言支援
- [Docker](https://docker.com/) - 容器化技術

## 📞 支援與回饋

- 🐛 問題回報: [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
- 💬 功能建議: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)
- 📧 技術支援: hctsai@linux.com
- 📖 文檔: [線上文檔](https://oran-nephio-rag.readthedocs.io/)

---

**Made with ❤️ for the Telecom and Cloud Native Community**