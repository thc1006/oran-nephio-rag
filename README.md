# O-RAN × Nephio RAG 整合助手

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

一個專為 O-RAN 和 Nephio 整合而設計的智能檢索增強生成（RAG）系統，專注於 Network Function (NF) 的 scale-out 和 scale-in 實作指導。

## 🎯 專案特色

- **官方文件優先**：僅從 O-RAN SC 和 Nephio 官方文件檢索資訊
- **準確性保證**：避免過時或不準確的網路資訊
- **專業焦點**：專注於 NF 擴縮容實作細節
- **即時更新**：自動同步最新官方文件
- **中文支援**：完整的繁體中文介面和回答

## 檔案結構
```
oran-nephio-rag/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py
├── src/
│   ├── __init__.py
│   ├── oran_nephio_rag.py
│   ├── document_loader.py
│   └── config.py
├── scripts/
│   ├── auto_sync.py
│   └── test_system.py
├── examples/
│   └── example_usage.py
├── docs/
│   └── SETUP.md
└── logs/ (執行時自動建立)
```



## 🚀 快速開始

### 前置需求

- Python 3.10 或以上版本
- Microsoft Visual C++ Build Tools（Windows）
- Anthropic API Key

### 安裝步驟

```
# 1. 複製專案
git clone https://github.com/your-username/oran-nephio-rag.git
cd oran-nephio-rag
```

```
# 2. 建立虛擬環境
python -m venv venv
venv\Scripts\activate  \# Windows
source venv/bin/activate  \# Linux/macOS
```

```
# 3. 安裝依賴
pip install -r requirements.txt
```

```
# 4. 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，添加你的 ANTHROPIC_API_KEY
```

```
# 5. 執行系統
python main.py
```


## 📖 使用方式

啟動系統後，您可以詢問關於 O-RAN 和 Nephio 整合的問題：

- "如何在 Nephio 上實現 O-RAN DU 的 scale-out？"
- "O2IMS 介面在 NF 擴縮中扮演什麼角色？"
- "FOCOM 和 SMO 如何協作進行自動擴縮？"

## 🛠️ 支援的文件來源

- [O-RAN SC Confluence](https://lf-o-ran-sc.atlassian.net/wiki/spaces/ORAN/overview)
- [Nephio Documentation](https://docs.nephio.org/)
- O-RAN SC 官方部落格和技術規範

## 📝 授權

本專案採用 Apache 2.0 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解詳細指南。
