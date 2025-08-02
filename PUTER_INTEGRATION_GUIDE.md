# 🚀 Puter.js 整合指南 - 預設 Claude API 存取方法

## 📋 概述

本文檔描述如何使用 Puter.js 整合功能，這是系統的預設 Claude API 存取方法。Puter.js 提供免費的 Claude API 存取，通過瀏覽器自動化技術實現。

## ✅ 特色與優勢

### 🎯 主要優勢

1. **免費使用**
   - 無需 Anthropic API 金鑰
   - 無使用量限制
   - 節省 API 成本

2. **完整功能支援**
   - 支援所有 Claude 模型 (claude-sonnet-4, claude-opus-4, claude-sonnet-3.5)
   - 支援串流回應
   - 完整的對話功能

3. **易於設定**
   - 基於 Puter.js 官方教學: https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/
   - 自動化瀏覽器整合
   - 無需複雜配置

4. **技術架構**
   - 基於瀏覽器自動化技術 (Chrome + Selenium)
   - 直接整合 Puter.js JavaScript API
   - 支援無頭瀏覽器模式

## ⚙️ 系統配置

### 步驟 1: 環境設定

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，設定以下內容：
API_MODE=browser
BROWSER_HEADLESS=true
PUTER_MODEL=claude-sonnet-4
BROWSER_TIMEOUT=120
BROWSER_WAIT_TIME=10
MAX_TOKENS=4000
TEMPERATURE=0.1
```

### 步驟 2: 系統需求

確保系統已安裝必要依賴：

```bash
# 安裝 Chrome 瀏覽器依賴
# 在 Docker 中會自動安裝，本地開發需要：
pip install selenium webdriver-manager

# Chrome 瀏覽器 (會自動下載)
# 或手動安裝 Google Chrome
```

### 步驟 3: 測試整合

```bash
# 執行快速測試
python test_puter_quick.py

# 執行完整測試 (較耗時)
python test_puter_integration.py
```

## 🔧 使用方式

### 程式碼範例

```python
from src.puter_integration import PuterRAGManager, quick_puter_query

# 方法 1: 快速查詢
result = quick_puter_query("什麼是 O-RAN?", model="claude-sonnet-4")
print(result)

# 方法 2: 使用 RAG 管理器
manager = PuterRAGManager(model='claude-sonnet-4', headless=True)
response = manager.query(
    prompt="解釋 Nephio 的核心概念",
    context="根據文檔內容..."
)
print(response['answer'])
```

### Docker 部署

```bash
# 生產環境部署
docker-compose -f docker-compose.prod.yml up -d

# 開發環境部署
docker-compose -f docker-compose.dev.yml up -d
```

## 🛠️ 可用模型

| 模型名稱 | 描述 | 適用場景 |
|---------|------|----------|
| `claude-sonnet-4` | 平衡性能與品質 | 預設推薦，適合大多數用途 |
| `claude-opus-4` | 最高智能水準 | 複雜推理、創意任務 |
| `claude-sonnet-3.5` | 較舊版本 | 兼容性測試 |

## 🔍 故障排除

### 常見問題

1. **瀏覽器啟動失敗**
   ```bash
   # 檢查 Chrome 是否正確安裝
   google-chrome --version
   
   # 更新 WebDriver
   pip install --upgrade webdriver-manager
   ```

2. **Puter.js 載入失敗**
   ```bash
   # 檢查網路連接
   curl -I https://js.puter.com/v2/
   
   # 增加等待時間
   export BROWSER_WAIT_TIME=20
   ```

3. **權限問題 (Docker)**
   ```bash
   # 確保 Chrome 有適當權限
   docker run --rm --cap-add=SYS_ADMIN your-image
   ```

### 日誌檢查

```bash
# 檢查應用日誌
docker logs oran-nephio-rag-app

# 檢查 Chrome 瀏覽器日誌
# 在程式碼中啟用 --enable-logging
```

## 📊 性能調優

### 配置建議

```bash
# 高效能設定
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=60
WORKERS=2  # Docker 環境下

# 偵錯模式
BROWSER_HEADLESS=false  # 可視化瀏覽器
LOG_LEVEL=DEBUG
```

### 資源使用

- **記憶體**: 每個瀏覽器實例約需 200-500MB
- **CPU**: 中等使用量，主要在頁面載入時
- **網路**: 持續連接到 Puter.js 服務

## 🔐 安全考量

1. **資料傳輸**: 所有查詢通過 Puter.js 服務
2. **本地儲存**: 無敏感資料本地儲存
3. **瀏覽器隔離**: 使用無頭瀏覽器減少風險
4. **日誌管理**: 避免在日誌中記錄敏感查詢內容

## 📈 監控與維護

### 健康檢查

```bash
# 檢查服務狀態
curl http://localhost:8000/health

# 檢查 Puter.js 整合狀態
python -c "
from src.puter_integration import PuterRAGManager
manager = PuterRAGManager()
print(manager.get_status())
"
```

### 定期維護

- 定期更新 Chrome 瀏覽器
- 監控 Puter.js 服務可用性
- 清理瀏覽器緩存和臨時文件

## 📚 參考資源

- [Puter.js 官方教學](https://developer.puter.com/tutorials/free-unlimited-claude-35-sonnet-api/)
- [Selenium WebDriver 文檔](https://selenium-python.readthedocs.io/)
- [Chrome 瀏覽器選項](https://peter.sh/experiments/chromium-command-line-switches/)