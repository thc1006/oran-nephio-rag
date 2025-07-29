# 🏗️ O-RAN × Nephio RAG 智慧檢索增強生成系統

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green.svg)](https://langchain.com/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Claude](https://img.shields.io/badge/Claude-3.0-purple.svg)](https://www.anthropic.com/)

> **專業的 O-RAN 與 Nephio 整合知識檢索系統**  
> 基於官方文檔構建，提供準確可靠的技術問答服務

## 🌟 核心特色

### 🎯 **官方文檔優先策略**
- 📚 **權威來源**：專注於 O-RAN SC 和 Nephio 官方文檔
- 🔄 **即時同步**：自動更新最新發布內容
- ✅ **準確性保證**：避免過時或不準確的網路資訊

### 🚀 **先進技術架構**
- 🤖 **Claude 3.0 AI**：最新的 Anthropic 大語言模型
- 🔍 **向量檢索**：ChromaDB + Sentence-Transformers 語義搜尋
- 📊 **RAG 架構**：檢索增強生成，確保回答準確性
- 🌐 **中文優先**：完整的繁體中文介面和回應

### 💼 **專業應用場景**
- 🏗️ **NF 擴展實現**：O-RAN DU/CU 在 Nephio 上的 scale-out 細節
- 🔧 **整合架構**：O2IMS 介面、FOCOM、SMO 協作機制
- 📋 **部署指南**：實際生產環境的最佳實踐

## 📁 專案結構

```
oran-nephio-rag/
├── 📄 README.md                    # 本檔案
├── 📋 requirements.txt              # Python 依賴清單
├── 🔐 .env.example                 # 環境變數範例
├── 🚫 .gitignore                   # Git 忽略規則
├── 🚀 main.py                      # 主程式進入點
├── 📁 src/                         # 核心原始碼
│   ├── 🔗 __init__.py
│   ├── 🧠 oran_nephio_rag.py       # RAG 系統核心
│   ├── 📚 document_loader.py        # 文檔載入器
│   └── ⚙️ config.py                # 配置管理
├── 📁 scripts/                     # 工具腳本
│   ├── 🔄 auto_sync.py             # 自動同步服務
│   └── 🧪 test_system.py           # 系統測試
├── 📁 examples/                    # 使用範例
│   ├── 🔗 __init__.py
│   └── 💡 example_usage.py         # 功能示範
├── 📁 tests/                       # 單元測試
│   ├── 🔗 __init__.py
│   ├── 🧪 test_config.py
│   ├── 🧪 test_document_loader.py
│   └── 🧪 test_rag_system.py
├── 📁 docs/                        # 詳細文檔
│   └── 📖 SETUP.md                 # 安裝設定指南
├── 📁 logs/                        # 系統日誌 (自動建立)
├── 📁 oran_nephio_vectordb/        # 向量資料庫 (自動建立)
└── 📁 embeddings_cache/            # 嵌入模型快取 (自動建立)
```

## 🚀 快速開始

### 📋 系統需求

- **Python**: 3.10 或更高版本
- **作業系統**: Windows 10/11, macOS, Linux
- **記憶體**: 建議 8GB 以上
- **磁碟空間**: 至少 2GB 可用空間
- **API 金鑰**: Anthropic Claude API Key

### ⚡ 三分鐘安裝

```bash
# 1️⃣ 複製專案
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag
```

```bash
# 2️⃣ 建立 Python 虛擬環境
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

```bash
# 3️⃣ 安裝依賴套件
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# 4️⃣ 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，加入您的 ANTHROPIC_API_KEY
```

```bash
# 5️⃣ 執行系統測試
python scripts/test_system.py
```

```bash
# 6️⃣ 啟動系統
python main.py
```

## � 使用方式

### 🎯 **互動式查詢**

啟動系統後，您可以詢問關於 O-RAN 和 Nephio 整合的問題：

```
🤖 O-RAN × Nephio RAG 系統
請輸入您的問題 (輸入 'quit' 或 'exit' 結束): 

❓ 如何在 Nephio 上實現 O-RAN DU 的 scale-out？

💡 回答：
在 Nephio 平台上實現 O-RAN DU (Distributed Unit) 的 scale-out 需要考慮以下幾個關鍵步驟...

📚 參考來源 (3 個):
  1. [NEPHIO] Nephio O-RAN Integration Architecture
  2. [ORAN_SC] O-RAN DU Scaling Best Practices  
  3. [NEPHIO] Free5GC NF Deployment Guide

⚡ 查詢耗時: 2.3 秒
```

### 🔧 **程式化使用**

```python
from src.oran_nephio_rag import ORANNephioRAG, quick_query

# 快速查詢
answer = quick_query("什麼是 O2IMS 介面？")

# 完整功能使用
rag = ORANNephioRAG()
rag.load_documents()  # 首次使用載入文檔
result = rag.query("FOCOM 在 O-RAN 架構中的作用？")
```

### 📊 **常見查詢範例**

| 問題類別 | 範例問題 |
|---------|---------|
| **架構設計** | "O-RAN 與 Nephio 的整合架構是什麼？" |
| **NF 擴展** | "如何實現 O-RAN CU 的水平擴展？" |
| **介面協議** | "O2IMS 介面的主要功能和設計原則？" |
| **部署實務** | "在生產環境中部署 O-RAN DU 的最佳實踐？" |
| **故障排除** | "O-RAN NF 擴展失敗的常見原因和解決方案？" |

## 🔧 高級配置

### ⚙️ **環境變數詳解**

```env
# 🔑 必要配置
ANTHROPIC_API_KEY=sk-ant-api03-你的API金鑰

# 🤖 Claude 模型設定
CLAUDE_MODEL=claude-3-sonnet-20240229    # 模型版本
CLAUDE_MAX_TOKENS=4000                    # 最大回應長度
CLAUDE_TEMPERATURE=0.1                    # 創造性程度 (0-1)

# 📊 向量資料庫設定
VECTOR_DB_PATH=./oran_nephio_vectordb     # 資料庫路徑
COLLECTION_NAME=oran_nephio_official      # 集合名稱
CHUNK_SIZE=1000                           # 文字塊大小
CHUNK_OVERLAP=200                         # 重疊字數

# 🔄 自動同步設定
AUTO_SYNC_ENABLED=true                    # 啟用自動同步
SYNC_INTERVAL_HOURS=24                    # 同步間隔 (小時)

# 📝 日誌設定
LOG_LEVEL=INFO                            # 日誌級別
LOG_FILE=logs/oran_nephio_rag.log         # 日誌檔案路徑
```

### � **自動同步服務**

```bash
# 啟動自動同步背景服務
python scripts/auto_sync.py --daemon

# 手動執行一次同步
python scripts/auto_sync.py --once

# 檢查同步狀態
python scripts/auto_sync.py --status
```

## 📚 支援的官方文檔來源

### 🏛️ **Nephio 官方文檔**
- 📖 [核心架構文檔](https://docs.nephio.org/docs/architecture/)
- 🔧 [O-RAN 整合指南](https://docs.nephio.org/docs/network-architecture/o-ran-integration/)
- 💻 [使用者指南](https://docs.nephio.org/docs/guides/user-guides/)
- 📋 [安裝部署](https://docs.nephio.org/docs/installation/)

### 🌐 **O-RAN SC 官方資源**
- 📚 [技術規範文檔](https://oransc.org/specifications/)
- 🏗️ [架構參考](https://wiki.o-ran-sc.org/)
- 🔧 [實作指南](https://docs.o-ran-sc.org/)
- 📊 [發布說明](https://wiki.o-ran-sc.org/display/REL)

## 🧪 測試與品質保證

### ✅ **自動化測試**

```bash
# 執行完整測試套件
pytest tests/ -v

# 執行特定測試模組
pytest tests/test_rag_system.py -v

# 執行測試並生成覆蓋率報告
pytest tests/ --cov=src --cov-report=html
```

### 📊 **系統健檢**

```bash
# 完整系統測試
python scripts/test_system.py

# 快速健康檢查
python -c "from src.oran_nephio_rag import quick_query; print(quick_query('測試'))"
```

## �️ 故障排除

### ❗ **常見問題**

<details>
<summary>📦 <strong>ChromaDB 安裝失敗</strong></summary>

**問題**: `pip install chromadb` 失敗  
**解決方案**:
```bash
# Windows: 確保已安裝 Visual C++ Build Tools
# 然後嘗試:
pip install --no-cache-dir chromadb==0.5.3

# 或使用 conda:
conda install -c conda-forge chromadb
```
</details>

<details>
<summary>🔑 <strong>API 金鑰問題</strong></summary>

**問題**: API 金鑰無效或配額不足  
**解決方案**:
1. 檢查 `.env` 檔案中的 `ANTHROPIC_API_KEY`
2. 確認金鑰格式：`sk-ant-api03-...`
3. 登入 [Anthropic Console](https://console.anthropic.com/) 檢查配額
</details>

<details>
<summary>🚀 <strong>記憶體不足</strong></summary>

**問題**: 系統記憶體使用量過高  
**解決方案**:
```env
# 在 .env 中調整參數
CHUNK_SIZE=512          # 減少文字塊大小
CLAUDE_MAX_TOKENS=2000  # 減少回應長度
```
</details>

### 📞 **技術支援**

如遇到無法解決的問題，請：

1. 🐛 **提交 Issue**: 在 GitHub 上創建詳細的問題報告
2. 📧 **聯繫開發者**: thc1006@example.com
3. 💬 **社群討論**: 加入 Nephio 社群 Slack 頻道

## 🤝 貢獻指南

歡迎參與專案貢獻！請遵循以下步驟：

```bash
# 1️⃣ Fork 專案並複製
git clone https://github.com/你的用戶名/oran-nephio-rag.git

# 2️⃣ 建立功能分支
git checkout -b feature/amazing-feature

# 3️⃣ 進行變更並提交
git commit -m "Add amazing feature"

# 4️⃣ 推送到分支
git push origin feature/amazing-feature

# 5️⃣ 提交 Pull Request
```

### 📝 **貢獻類型**

- 🐛 Bug 修復
- ✨ 新功能開發  
- 📚 文檔改進
- 🧪 測試增強
- 🎨 程式碼品質優化

## 📜 授權條款

本專案採用 [Apache 2.0 授權條款](LICENSE)。您可以自由使用、修改和發布，但需保留原始授權聲明。

## 🌟 致謝

特別感謝以下開源專案和社群：

- 🦜 **LangChain**: 強大的 LLM 應用開發框架
- 🤖 **Anthropic**: 提供 Claude AI 模型
- 🔍 **ChromaDB**: 高效的向量資料庫
- 🏗️ **Nephio Project**: 雲原生網路功能編排
- 🌐 **O-RAN Alliance**: 開放 RAN 架構標準

---

<div align="center">

**🚀 準備好探索 O-RAN × Nephio 的無限可能了嗎？**

[開始使用](#-快速開始) | [查看範例](examples/) | [閱讀文檔](docs/) | [提交問題](../../issues)

</div>
