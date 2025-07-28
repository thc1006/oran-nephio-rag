# 詳細安裝設定指南

## Windows 11 完整安裝流程

### 1. 前置需求檢查

#### Python 版本

```
python --version
```

確保版本為 3.10 或以上。如果不是，請從 [python.org](https://www.python.org/downloads/) 下載安裝。

#### Microsoft Visual C++ Build Tools
1. 前往 https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. 下載 "Build Tools for Visual Studio"
3. 安裝時選擇 "C++ build tools" 和 "Windows 10/11 SDK"

### 2. 專案設定
```
# 複製專案
git clone https://github.com/your-username/oran-nephio-rag.git
cd oran-nephio-rag
```
```
# 建立虛擬環境
python -m venv venv
```

```
# 啟動虛擬環境（Windows）
venv\Scripts\activate
```

```
# 或者在 PowerShell 中
venv\Scripts\Activate.ps1
```

### 3. 套件安裝

```
# 升級 pip
python -m pip install --upgrade pip
```

```
# 安裝依賴（按順序安裝以避免相容性問題）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 4. 環境變數設定
```
# 複製範例環境檔案
copy .env.example .env
```

```
# 編輯 .env 檔案，添加你的 API 金鑰
# ANTHROPIC_API_KEY=your_key_here
```

### 5. 系統測試

```
# 執行系統測試
python scripts/test_system.py
```


### 6. 首次執行

```
# 啟動主程式
python main.py
```

## 常見問題排解

### ChromaDB 安裝失敗

**問題**: `pip install chromadb` 失敗
**解決方案**:
1. 確保已安裝 Visual C++ Build Tools
2. 嘗試: `pip install --no-cache-dir chromadb==0.5.3`
3. 如果仍失敗，嘗試: `conda install -c conda-forge chromadb`

### 嵌入模型下載慢

**問題**: SentenceTransformers 模型下載緩慢
**解決方案**:
1. 使用 VPN 或代理
2. 手動下載模型到 `./embeddings_cache/` 目錄

### API 配額問題

**問題**: Anthropic API 配額不足
**解決方案**:
1. 檢查 API 使用量
2. 升級 API 方案
3. 調整 `CLAUDE_MAX_TOKENS` 參數

### 記憶體不足

**問題**: 系統記憶體不足
**解決方案**:
1. 關閉其他應用程式
2. 調整 `chunk_size` 參數
3. 使用較小的嵌入模型

## 效能調優

### 向量資料庫優化
- 調整 `chunk_size` 和 `chunk_overlap` 參數
- 定期清理向量資料庫
- 使用 SSD 儲存向量資料庫

### 查詢優化
- 調整檢索器的 `k` 和 `fetch_k` 參數
- 使用更精確的查詢關鍵字
- 啟用查詢結果快取

## 進階設定

### 自訂文件來源
編輯 `src/config.py` 中的 `OFFICIAL_SOURCES` 列表：

```
OFFICIAL_SOURCES.append(
    DocumentSource(
        url="your_custom_url",
        source_type="custom",
        description="Custom Documentation",
        priority=3
    )
)
```

### 調整模型參數
修改 `.env` 檔案中的參數：

```
CLAUDE_TEMPERATURE=0.1    \# 創造性（0-1）
CLAUDE_MAX_TOKENS=2048    \# 最大回應長度
```
