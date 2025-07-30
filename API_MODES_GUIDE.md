# 🔄 O-RAN × Nephio RAG 系統 - API 模式使用指南

## 📋 概述

O-RAN × Nephio RAG 系統現在支援多種 API 模式，讓您可以根據不同需求和環境選擇最適合的 LLM 整合方案。

## 🎯 支援的 API 模式

### 1. **Anthropic 模式** (推薦 - 生產環境)
- **描述**: 使用官方 Anthropic Claude API
- **優點**: 最佳回答品質、完整功能支援、官方支援
- **缺點**: 需要付費 API 金鑰
- **適用**: 生產環境、正式部署

### 2. **Mock 模式** (測試/開發用)
- **描述**: 使用預設的模擬回答
- **優點**: 免費、快速、無需外部依賴
- **缺點**: 回答內容固定、品質有限
- **適用**: 系統測試、功能開發、展示

### 3. **Local 模式** (隱私保護)
- **描述**: 使用本地部署的 LLM (如 Ollama)
- **優點**: 完全本地化、資料隱私、無 API 費用
- **缺點**: 需要硬體資源、設定複雜
- **適用**: 隱私敏感環境、內部部署

### 4. **Puter 模式** (🧪 實驗性 - 高風險)
- **描述**: 第三方 Claude API 服務整合
- **優點**: 聲稱免費使用 Claude API
- **缺點**: 重大安全和隱私風險、服務不穩定
- **適用**: 僅供學習、研究、概念驗證
- **狀態**: ⚠️ 已實現但需風險確認

---

## ⚙️ 配置設定

### 環境變數配置

在 `.env` 檔案中設定以下變數：

```bash
# ============ API 模式配置 ============
# 選擇 API 模式: anthropic | mock | local | puter
API_MODE=anthropic

# ============ Anthropic API 配置 ============
# (API_MODE=anthropic 時必填)
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.1

# ============ 本地模型配置 ============
# (API_MODE=local 時使用)
LOCAL_MODEL_URL=http://localhost:11434
LOCAL_MODEL_NAME=llama2
```

### 配置模板

我們提供了完整的 `.env.example` 檔案範本，包含所有模式的配置選項。

---

## 🚀 使用方法

### 方法 1: 環境變數切換

```bash
# 設定為 Mock 模式 (測試用)
export API_MODE=mock
python main.py

# 設定為 Anthropic 模式 (生產用)
export API_MODE=anthropic
export ANTHROPIC_API_KEY=your-real-api-key
python main.py

# 設定為本地模式
export API_MODE=local
export LOCAL_MODEL_URL=http://localhost:11434
python main.py

# 設定為實驗性 Puter 模式 (需要風險確認)
export API_MODE=puter
export PUTER_RISK_ACKNOWLEDGED=true
python main.py
```

### 方法 2: 程式碼中切換

```python
from src import create_rag_system

# 創建 RAG 系統
rag = create_rag_system()

# 檢查當前 API 模式狀態
status = rag.get_system_status()
print(f"當前模式: {status['llm_status']['api_mode']}")

# 切換到 Mock 模式
result = rag.switch_api_mode('mock')
if result['success']:
    print(f"✅ {result['message']}")
else:
    print(f"❌ {result['message']}")

# 執行查詢
answer = rag.query("什麼是 Nephio？")
print(answer['answer'])
```

### 方法 3: 快速查詢函數

```python
from src.api_adapters import quick_llm_query

# 直接指定模式進行查詢
answer = quick_llm_query("什麼是 O-RAN？", mode="mock")
print(answer)

# 使用環境變數中的模式
answer = quick_llm_query("Nephio 的核心功能是什麼？")
print(answer)
```

---

## 🔧 各模式詳細設定

### Anthropic 模式設定

1. **取得 API 金鑰**:
   ```bash
   # 前往 https://console.anthropic.com/ 註冊並取得 API 金鑰
   # 新用戶有 $5 免費額度
   ```

2. **設定環境變數**:
   ```bash
   export API_MODE=anthropic
   export ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

3. **驗證設定**:
   ```python
   from src.api_adapters import create_llm_manager
   
   manager = create_llm_manager()
   status = manager.get_status()
   print(f"API 可用: {status['adapter_available']}")
   ```

### Mock 模式設定

1. **啟用 Mock 模式**:
   ```bash
   export API_MODE=mock
   ```

2. **無需額外設定** - Mock 模式提供預設回答

3. **自訂回答** (可選):
   ```python
   # 可以修改 src/api_adapters.py 中的 MockAdapter 回答內容
   ```

### Local 模式設定

1. **安裝 Ollama**:
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows - 下載 Ollama 安裝程式
   # https://ollama.ai/download
   
   # 或使用 Docker
   docker run -d -v ollama:/root/.ollama -p 11434:11434 ollama/ollama
   ```

2. **下載模型**:
   ```bash
   # 下載 Llama 2 模型 (約 3.8GB)
   ollama pull llama2
   
   # 或下載其他模型
   ollama pull codellama    # 程式碼專用
   ollama pull mistral      # 較小的模型
   ```

3. **設定環境變數**:
   ```bash
   export API_MODE=local
   export LOCAL_MODEL_URL=http://localhost:11434
   export LOCAL_MODEL_NAME=llama2
   ```

4. **驗證本地模型**:
   ```bash
   # 測試模型是否運作
   curl http://localhost:11434/api/generate -d '{
     "model": "llama2",
     "prompt": "Hello, world!",
     "stream": false
   }'
   ```

### Puter 模式設定 (🧪 實驗性)

> **⚠️ 警告**: 這是高風險的實驗性功能，僅供學習和研究使用

1. **風險確認**:
   ```bash
   # 必須明確確認風險
   export PUTER_RISK_ACKNOWLEDGED=true
   ```

2. **設定環境變數**:
   ```bash
   export API_MODE=puter
   export PUTER_RISK_ACKNOWLEDGED=true
   export PUTER_MODEL=claude-sonnet-4  # 或 claude-opus-4
   ```

3. **執行測試**:
   ```bash
   # 快速測試
   python test_puter_quick.py
   
   # 完整測試
   python test_puter_integration.py
   ```

4. **風險說明**:
   - 📄 詳細風險分析: [PUTER_API_ANALYSIS.md](./PUTER_API_ANALYSIS.md)
   - 🧪 使用指南: [EXPERIMENTAL_PUTER_INTEGRATION.md](./EXPERIMENTAL_PUTER_INTEGRATION.md)
   - ⚠️ 僅供教育和概念驗證用途

---

## 🧪 測試和驗證

### 執行 API 模式測試

```bash
# 執行完整的 API 模式測試
python test_api_modes.py

# 輸出會顯示每種模式的測試結果
```

### 手動測試每種模式

```python
# 測試腳本範例
import os
from src.api_adapters import create_llm_manager

def test_mode(mode):
    os.environ['API_MODE'] = mode
    manager = create_llm_manager()
    
    status = manager.get_status()
    print(f"{mode} 模式: {'✅' if status['adapter_available'] else '❌'}")
    
    if status['adapter_available']:
        result = manager.query("測試查詢")
        print(f"查詢結果: {result['answer'][:100]}...")

# 測試所有模式 (包括實驗性)
for mode in ['anthropic', 'mock', 'local', 'puter']:
    if mode == 'puter':
        os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'true'
    test_mode(mode)
```

---

## 🔍 故障排除

### 常見問題

#### 1. Anthropic API 錯誤

**問題**: `❌ API 金鑰無效或已過期`

**解決方案**:
```bash
# 檢查 API 金鑰格式
echo $ANTHROPIC_API_KEY  # 應該以 sk-ant-api03- 開頭

# 驗證 API 金鑰
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-sonnet-20240229","max_tokens":100,"messages":[{"role":"user","content":"Hello!"}]}'
```

#### 2. 本地模型連接錯誤

**問題**: `❌ 無法連接本地模型服務`

**解決方案**:
```bash
# 檢查 Ollama 是否運行
ps aux | grep ollama

# 檢查端口
netstat -an | grep 11434

# 重新啟動 Ollama
ollama serve

# 測試連接
curl http://localhost:11434/api/tags
```

#### 3. 模式切換失敗

**問題**: 無法切換 API 模式

**解決方案**:
```python
# 檢查當前系統狀態
from src import create_rag_system

rag = create_rag_system()
status = rag.get_system_status()
print("系統狀態:", status)

# 強制重新初始化
rag.query_processor._setup_llm()
```

### 日誌除錯

```python
import logging

# 設定詳細日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('src.api_adapters')

# 執行查詢並檢查日誌
```

---

## 🎯 最佳實踐建議

### 開發環境設定

```bash
# 開發時使用 Mock 模式進行快速測試
export API_MODE=mock

# 功能測試時使用少量 Anthropic API 額度
export API_MODE=anthropic
export ANTHROPIC_API_KEY=your-test-key
```

### 生產環境設定

```bash
# 生產環境使用 Anthropic API
export API_MODE=anthropic
export ANTHROPIC_API_KEY=your-production-key

# 設定合理的限制
export CLAUDE_MAX_TOKENS=2048
export CLAUDE_TEMPERATURE=0.1
```

### 隱私敏感環境

```bash
# 使用本地模型避免資料外洩
export API_MODE=local
export LOCAL_MODEL_URL=http://localhost:11434
export LOCAL_MODEL_NAME=llama2
```

### 成本控制

```python
# 在程式中實現成本監控
def query_with_cost_control(question, max_cost=10):
    # 檢查當前 API 使用量
    # 如果超過預算，自動切換到 Mock 模式
    pass
```

---

## 📈 效能比較

| 模式 | 回答品質 | 回應速度 | 成本 | 隱私性 | 設定複雜度 |
|------|----------|----------|------|--------|------------|
| Anthropic | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 💰💰💰 | ⭐⭐ | ⭐⭐ |
| Mock | ⭐⭐ | ⭐⭐⭐⭐⭐ | 免費 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Local | ⭐⭐⭐⭐ | ⭐⭐ | 免費* | ⭐⭐⭐⭐⭐ | ⭐⭐ |

*本地模式需要硬體成本

---

## 🔄 版本更新

### v1.0.0 (目前版本)
- ✅ 支援 Anthropic、Mock、Local 三種模式
- ✅ 動態模式切換功能
- ✅ 完整的錯誤處理和日誌記錄
- ✅ 測試腳本和文檔

### 未來規劃
- 🔜 支援更多本地模型 (Mistral、CodeLlama)
- 🔜 API 使用量監控和成本控制
- 🔜 自動模式切換 (基於可用性和成本)
- 🔜 批量查詢優化

---

## 💡 總結

新的 API 模式功能讓 O-RAN × Nephio RAG 系統更加靈活和實用：

1. **開發階段**: 使用 Mock 模式進行快速開發和測試
2. **測試階段**: 使用少量 Anthropic API 額度進行功能驗證
3. **生產階段**: 根據需求選擇 Anthropic API 或本地模型
4. **隱私環境**: 使用本地模型確保資料不外流

這個設計讓您可以在不同階段和環境中都能有效使用系統，同時保持高度的彈性和控制力。

需要協助設定任何模式嗎？請參考相關章節或執行測試腳本來驗證配置！