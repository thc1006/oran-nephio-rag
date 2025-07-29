# 🔧 O-RAN × Nephio RAG 系統快速修復指南

## 📋 問題解決狀態

✅ **已修復的問題**:
- ✅ requirements.txt 依賴配置已更新
- ✅ pyproject.toml 依賴順序已優化  
- ✅ 代碼中的 LangChain 導入警告已修正
- ✅ 新增 langchain-huggingface 支援
- ✅ 核心系統架構驗證通過 (3/4 測試)

⚠️ **剩餘問題**: 
- `sentence-transformers` 套件需要手動安裝

## 🚀 快速修復方案

### 方案 1: 完整安裝 (推薦)

```bash
# 1. 安裝核心依賴
pip install sentence-transformers>=2.2.2

# 2. 安裝 LangChain HuggingFace 支援
pip install langchain-huggingface

# 3. 安裝其餘依賴
pip install -r requirements.txt

# 4. 驗證安裝
python test_fixed_system.py
```

### 方案 2: Docker 部署 (最簡單)

```bash
# 直接使用 Docker (會自動安裝所有依賴)
docker-compose -f docker-compose.dev.yml up -d

# 或生產環境
docker-compose -f docker-compose.prod.yml up -d
```

### 方案 3: 分步安裝

```bash
# 1. 升級 pip
python -m pip install --upgrade pip

# 2. 安裝 PyTorch (sentence-transformers 依賴)
pip install torch

# 3. 安裝 sentence-transformers
pip install sentence-transformers

# 4. 安裝剩餘套件
pip install -r requirements.txt
```

## ✅ 驗證系統狀態

執行以下命令驗證修復結果:

```bash
# 驗證核心功能
python test_fixed_system.py

# 預期輸出:
# Tests passed: 4/4
# SUCCESS: sentence-transformers dependency is now available!
# VERDICT: FULLY_FIXED
```

## 🎯 實際使用

修復完成後，你可以:

### 1. 設定環境變數
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，設定:
ANTHROPIC_API_KEY=your-real-api-key-here
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

### 3. 執行查詢
```bash
# 快速測試
python -c "
from src import quick_query
answer = quick_query('什麼是 Nephio？')
print(answer)
"
```

### 4. 啟動互動式界面
```bash
python main.py
```

## 🐳 Docker 部署驗證

如果使用 Docker:

```bash
# 檢查容器狀態
docker-compose ps

# 查看日誌
docker-compose logs oran-rag-app

# 測試 API
curl http://localhost:8000/health
```

## 📊 修復前後對比

| 項目 | 修復前 | 修復後 |
|------|--------|--------|
| **依賴管理** | ❌ sentence-transformers 缺失 | ✅ 完整依賴配置 |
| **導入警告** | ⚠️ LangChain 棄用警告 | ✅ 使用新版 langchain-huggingface |
| **測試通過率** | 75% (3/4) | 100% (4/4) 安裝後 |
| **部署就緒度** | ⚠️ 需手動修復 | ✅ 立即可用 |

## 🔍 故障排除

### 問題 1: sentence-transformers 安裝失敗
```bash
# 解決方案: 先安裝 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

### 問題 2: ChromaDB 相容性問題
```bash
# 解決方案: 使用指定版本
pip install chromadb==0.4.24
```

### 問題 3: 記憶體不足
```bash
# 解決方案: 調整環境變數
export CHUNK_SIZE=512
export CLAUDE_MAX_TOKENS=2048
```

## 🎉 修復完成確認

執行以下檢查確認系統完全修復:

```bash
# 1. 依賴檢查
python -c "import sentence_transformers; print('✅ sentence-transformers OK')"

# 2. 核心模組檢查  
python -c "from src.oran_nephio_rag import create_rag_system; print('✅ RAG system OK')"

# 3. 配置檢查
python -c "from src.config import Config; c=Config(); print(f'✅ Config OK: {len(c.OFFICIAL_SOURCES)} sources')"

# 4. 完整系統測試
python test_fixed_system.py
```

**如果所有檢查都通過，恭喜！系統已完全修復並可投入使用！** 🚀

## 📞 技術支援

如果仍有問題:
- 📧 Email: dev-team@company.com  
- 🐛 Issues: [GitHub Issues](https://github.com/company/oran-nephio-rag/issues)
- 💬 討論: [GitHub Discussions](https://github.com/company/oran-nephio-rag/discussions)

---

*修復指南版本: 1.0*  
*最後更新: 2024年1月*