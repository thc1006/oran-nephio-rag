# O-RAN × Nephio RAG 系統

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI/CD](https://github.com/company/oran-nephio-rag/workflows/CI/badge.svg)](https://github.com/company/oran-nephio-rag/actions)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

基於檢索增強生成 (RAG) 技術的智能問答系統，專門針對 O-RAN 和 Nephio 技術文檔設計。

## 🚀 專案特色

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

## 🔑 必要條件

1. **環境設定**: 複製 `.env.example` 為 `.env` 並配置必要參數
2. **瀏覽器支持**: 系統使用瀏覽器自動化技術進行 AI 整合

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

```bash
# 建立向量資料庫
python -c "
from src import create_rag_system
rag = create_rag_system()
rag.build_vector_database()
print('✅ 向量資料庫建立完成')
"
```

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
```

## 🐳 Docker 部署

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