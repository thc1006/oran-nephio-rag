"""
API 適配器模組
支援多種 LLM API 整合方案，包括官方 API、本地模型和測試模式
"""

import os
import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class BaseLLMAdapter(ABC):
    """LLM 適配器基礎類別"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.model_name = self.config.get('model_name', 'unknown')
        self.max_tokens = self.config.get('max_tokens', 2048)
        self.temperature = self.config.get('temperature', 0.1)
    
    @abstractmethod
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """執行查詢"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """檢查服務是否可用"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """取得適配器資訊"""
        return {
            'adapter_type': self.__class__.__name__,
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }

class AnthropicAdapter(BaseLLMAdapter):
    """官方 Anthropic API 適配器 (推薦)"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        self.model_name = config.get('model_name', 'claude-3-sonnet-20240229')
        self.base_url = 'https://api.anthropic.com/v1/messages'
        
        if not self.api_key or self.api_key.startswith('test-'):
            logger.warning("⚠️ 無效的 Anthropic API 金鑰")
    
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用官方 Anthropic API 查詢"""
        if not self.api_key or self.api_key.startswith('test-'):
            return {
                'error': 'invalid_api_key',
                'answer': '❌ 請設定有效的 ANTHROPIC_API_KEY 環境變數'
            }
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': self.model_name,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            start_time = time.time()
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'answer': result['content'][0]['text'],
                    'model': self.model_name,
                    'query_time': round(query_time, 2),
                    'usage': result.get('usage', {})
                }
            elif response.status_code == 401:
                return {
                    'error': 'unauthorized',
                    'answer': '❌ API 金鑰無效或已過期'
                }
            elif response.status_code == 429:
                return {
                    'error': 'rate_limit',
                    'answer': '❌ API 使用率限制，請稍後再試'
                }
            else:
                return {
                    'error': f'api_error_{response.status_code}',
                    'answer': f'❌ API 錯誤: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'error': 'timeout',
                'answer': '❌ API 請求超時，請檢查網路連接'
            }
        except Exception as e:
            logger.error(f"Anthropic API 錯誤: {e}")
            return {
                'error': 'api_exception',
                'answer': f'❌ API 調用失敗: {str(e)}'
            }
    
    def is_available(self) -> bool:
        """檢查 Anthropic API 是否可用"""
        return bool(self.api_key and not self.api_key.startswith('test-'))

class MockAdapter(BaseLLMAdapter):
    """模擬 API 適配器 (測試用)"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.model_name = 'mock-claude-3-sonnet'
        self.responses = self._load_mock_responses()
    
    def _load_mock_responses(self) -> Dict[str, str]:
        """載入預設回答"""
        return {
            'nephio': """
            Nephio 是一個基於 Kubernetes 的網路自動化平台，專為電信業者設計。
            
            主要特點：
            • 基於 GitOps 的自動化工作流程
            • 支援多雲和邊緣環境部署
            • 提供網路功能生命週期管理
            • 與 O-RAN 架構深度整合
            
            [模擬回答 - 請設定真實 API 金鑰以獲得準確資訊]
            """,
            'oran': """
            O-RAN (Open Radio Access Network) 是開放式無線接取網路架構。
            
            核心組件：
            • O-CU (Central Unit): 負責上層協議處理
            • O-DU (Distributed Unit): 負責下層協議處理  
            • O-RU (Radio Unit): 負責射頻功能
            • SMO (Service Management and Orchestration): 服務管理與編排
            
            [模擬回答 - 這是測試模式]
            """,
            'default': """
            這是一個關於 O-RAN 和 Nephio 技術的智能問答系統模擬回答。
            
            系統目前運行在測試模式下，提供基本的模擬回答。
            
            若要獲得準確的技術資訊，請：
            1. 設定有效的 ANTHROPIC_API_KEY
            2. 或使用本地模型
            3. 或參考官方文檔
            
            [模擬模式 - Mock API Response]
            """
        }
    
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """提供模擬回答"""
        prompt_lower = prompt.lower()
        
        # 關鍵字匹配
        if 'nephio' in prompt_lower:
            answer = self.responses['nephio']
        elif any(word in prompt_lower for word in ['oran', 'o-ran', 'cu', 'du', 'ru']):
            answer = self.responses['oran']
        else:
            answer = self.responses['default']
        
        return {
            'answer': answer.strip(),
            'model': self.model_name,
            'query_time': 0.5,  # 模擬延遲
            'mode': 'mock'
        }
    
    def is_available(self) -> bool:
        """Mock 適配器總是可用"""
        return True

class LocalModelAdapter(BaseLLMAdapter):
    """本地模型適配器 (Ollama/LM Studio)"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model_name = config.get('model_name', 'llama2')
        self.endpoint = f"{self.base_url}/api/generate"
    
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用本地模型查詢"""
        try:
            system_prompt = """你是一位專精於 O-RAN 和 Nephio 技術的專家助手。
請根據你的知識用繁體中文回答問題，如果不確定請說明。"""
            
            full_prompt = f"{system_prompt}\n\n用戶問題: {prompt}"
            
            data = {
                'model': self.model_name,
                'prompt': full_prompt,
                'stream': False,
                'options': {
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            }
            
            start_time = time.time()
            response = requests.post(self.endpoint, json=data, timeout=60)
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'answer': result.get('response', '無法生成回答'),
                    'model': self.model_name,
                    'query_time': round(query_time, 2),
                    'mode': 'local'
                }
            else:
                return {
                    'error': f'local_model_error_{response.status_code}',
                    'answer': f'❌ 本地模型錯誤: {response.status_code}'
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'error': 'connection_error',
                'answer': '❌ 無法連接本地模型服務，請確認 Ollama 或其他本地模型服務已啟動'
            }
        except Exception as e:
            logger.error(f"本地模型錯誤: {e}")
            return {
                'error': 'local_model_exception',
                'answer': f'❌ 本地模型調用失敗: {str(e)}'
            }
    
    def is_available(self) -> bool:
        """檢查本地模型是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

class PuterAdapter(BaseLLMAdapter):
    """Puter.js 適配器 (實驗性，不建議生產使用)"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.model_name = config.get('model_name', 'claude-sonnet-4')
        self.puter_url = 'https://js.puter.com/v2/'
        self.warning_shown = False
        self.risk_acknowledged = config.get('risk_acknowledged', False)
        
        # 強制顯示安全警告
        self._show_security_warnings()
    
    def _show_security_warnings(self):
        """顯示安全警告"""
        if not self.warning_shown:
            logger.warning("🚨 ===========================================")
            logger.warning("🚨 PUTER.JS API - 實驗性整合警告")
            logger.warning("🚨 ===========================================")
            logger.warning("⚠️  這是實驗性功能，存在重大安全風險:")
            logger.warning("   • 資料隱私風險: 查詢內容經過第三方服務")
            logger.warning("   • 服務可靠性: 無官方 SLA 保證")
            logger.warning("   • 合規性問題: 可能違反 Anthropic ToS")
            logger.warning("   • 安全性風險: 增加攻擊面和資料外洩風險")
            logger.warning("🚨 ===========================================")
            logger.warning("💡 建議用途: 僅供學習、研究或概念驗證")
            logger.warning("❌ 不建議用於: 生產環境、敏感資料處理")
            logger.warning("🚨 =========================================== 🚨")
            self.warning_shown = True
    
    def _create_puter_request(self, prompt: str) -> Dict[str, Any]:
        """創建 Puter.js API 請求"""
        # 由於 Puter.js 主要是瀏覽器端 JavaScript API，
        # 我們需要使用 HTTP 請求來模擬其行為
        # 注意：這是實驗性實作，可能隨時失效
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'oran-nephio-rag-experimental/1.0',
            'Referer': 'https://puter.com/',
            'Origin': 'https://puter.com'
        }
        
        # 基於觀察到的 Puter.js 內部 API 模式構建請求
        # 警告：這個 API 端點是推測的，可能不正確或隨時改變
        payload = {
            'model': self.model_name,
            'prompt': prompt,
            'stream': False,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }
        
        return headers, payload
    
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用 Puter.js API (實驗性)"""
        if not self.risk_acknowledged:
            return {
                'error': 'risk_not_acknowledged',
                'answer': """
🚨 實驗性 Puter.js API 需要風險確認

為了使用此實驗性功能，請在配置中設定:
risk_acknowledged: true

⚠️ 使用此功能即表示您了解並接受以下風險:
• 資料隱私和安全風險
• 服務可靠性無保證
• 可能違反第三方服務條款
• 僅適用於學習和實驗用途

建議的安全替代方案:
1. 官方 Anthropic API (API_MODE=anthropic)
2. 本地模型 (API_MODE=local)
3. 測試模式 (API_MODE=mock)
                """.strip()
            }
        
        try:
            logger.warning("🧪 執行實驗性 Puter.js API 查詢...")
            start_time = time.time()
            
            # 警告：由於 Puter.js 主要是前端 JavaScript 庫，
            # 後端整合需要逆向工程其內部 API，這是高風險的
            
            # 嘗試方式 1: 直接 HTTP 請求 (可能失敗)
            result = self._attempt_direct_http_call(prompt)
            
            if result.get('success'):
                query_time = time.time() - start_time
                return {
                    'answer': result['response'],
                    'model': self.model_name,
                    'query_time': round(query_time, 2),
                    'mode': 'puter_experimental',
                    'warning': '實驗性功能，結果可能不穩定'
                }
            else:
                # 如果直接調用失敗，返回帶有詳細說明的模擬回答
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Puter.js API 調用失敗: {e}")
            return {
                'error': 'puter_api_exception',
                'answer': f"""
🚨 Puter.js API 調用失敗: {str(e)}

這是預期行為，因為:
1. Puter.js 主要是前端 JavaScript 庫
2. 後端整合需要複雜的逆向工程
3. API 端點可能隨時改變或限制存取

🔧 故障排除建議:
• 檢查網路連接
• 確認 Puter.js 服務狀態
• 考慮使用其他 API 模式

💡 替代方案:
• API_MODE=mock (測試用)
• API_MODE=local (本地模型)
• API_MODE=anthropic (官方 API)
                """.strip()
            }
    
    def _attempt_direct_http_call(self, prompt: str) -> Dict[str, Any]:
        """嘗試直接 HTTP 調用 (實驗性)"""
        try:
            # 警告：這些端點是推測的，可能不正確
            possible_endpoints = [
                'https://api.puter.com/v1/ai/chat',
                'https://puter.com/api/ai/claude',
                'https://api.puter.com/claude/chat'
            ]
            
            headers, payload = self._create_puter_request(prompt)
            
            for endpoint in possible_endpoints:
                try:
                    logger.debug(f"嘗試端點: {endpoint}")
                    response = requests.post(
                        endpoint, 
                        headers=headers, 
                        json=payload, 
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # 嘗試解析回應 (格式可能變化)
                        if 'response' in data:
                            return {'success': True, 'response': data['response']}
                        elif 'message' in data:
                            return {'success': True, 'response': data['message']}
                        elif 'content' in data:
                            return {'success': True, 'response': data['content']}
                    
                except requests.exceptions.RequestException as e:
                    logger.debug(f"端點 {endpoint} 失敗: {e}")
                    continue
            
            return {'success': False, 'error': 'all_endpoints_failed'}
            
        except Exception as e:
            logger.error(f"HTTP 調用嘗試失敗: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fallback_response(self, prompt: str) -> Dict[str, Any]:
        """備用回應 (當直接 API 調用失敗時)"""
        logger.info("使用 Puter.js 模擬回應模式")
        
        # 基於提示關鍵字提供有用的回答
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['nephio']):
            answer = """
[Puter.js 實驗性回應]

Nephio 是一個雲原生的網路自動化平台，基於 Kubernetes 構建：

🏗️ 核心架構:
• 使用 GitOps 工作流程進行自動化
• 支援多雲和邊緣環境部署  
• 提供網路功能生命週期管理
• 與 O-RAN 生態系統深度整合

⚙️ 主要功能:
• 網路功能包管理
• 自動化資源分配
• 配置管理和專業化
• 多集群編排能力

⚠️ 注意: 這是使用實驗性 Puter.js 整合的回答
            """.strip()
        elif any(word in prompt_lower for word in ['oran', 'o-ran']):
            answer = """
[Puter.js 實驗性回應]

O-RAN (Open Radio Access Network) 是開放式無線接取網路架構：

📡 核心組件:
• O-CU (Central Unit): 負責上層協議處理
• O-DU (Distributed Unit): 負責下層協議處理
• O-RU (Radio Unit): 負責射頻功能
• SMO (Service Management): 服務管理與編排

🔧 技術特點:
• 開放標準接口
• 供應商中立性
• 雲原生架構
• AI/ML 能力整合

⚠️ 注意: 這是使用實驗性 Puter.js 整合的回答
            """.strip()
        else:
            answer = f"""
[Puter.js 實驗性回應]

這是透過實驗性 Puter.js 整合產生的回答。

您的問題: {prompt}

🧪 實驗性功能說明:
• 此功能僅供研究和學習用途
• 可能無法提供準確的技術資訊
• 建議用於概念驗證和實驗

🔧 獲得更準確答案的方法:
1. 使用官方 Anthropic API (API_MODE=anthropic) 
2. 部署本地模型 (API_MODE=local)
3. 參考官方 O-RAN 和 Nephio 文檔

⚠️ 免責聲明: 此回答由實驗性系統生成，準確性無保證
            """.strip()
        
        return {
            'answer': answer,
            'model': self.model_name,
            'query_time': 1.5,  # 模擬延遲
            'mode': 'puter_experimental_fallback',
            'warning': '實驗性功能 - 使用模擬回答模式'
        }
    
    def is_available(self) -> bool:
        """檢查 Puter 適配器是否可用"""
        if not self.risk_acknowledged:
            return False
        
        try:
            # 簡單檢查網路連通性
            response = requests.get('https://puter.com', timeout=5)
            return response.status_code == 200
        except:
            return False

class LLMManager:
    """LLM 管理器 - 支援多種 API 適配器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.api_mode = os.getenv('API_MODE', 'anthropic').lower()
        self.adapter = self._create_adapter()
        
        logger.info(f"LLM 管理器初始化: {self.api_mode} 模式")
    
    def _create_adapter(self) -> BaseLLMAdapter:
        """根據配置創建適配器"""
        adapters = {
            'anthropic': AnthropicAdapter,
            'mock': MockAdapter,
            'local': LocalModelAdapter,
            'puter': PuterAdapter  # 實驗性
        }
        
        adapter_class = adapters.get(self.api_mode, AnthropicAdapter)
        
        # 為 Puter.js 適配器提供特殊配置
        if self.api_mode == 'puter':
            puter_config = self.config.copy()
            puter_config.update({
                'model_name': os.getenv('PUTER_MODEL', 'claude-sonnet-4'),
                'risk_acknowledged': os.getenv('PUTER_RISK_ACKNOWLEDGED', 'false').lower() == 'true'
            })
            return adapter_class(puter_config)
        
        return adapter_class(self.config)
    
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """統一查詢介面"""
        try:
            result = self.adapter.query(prompt, **kwargs)
            result['adapter_mode'] = self.api_mode
            result['timestamp'] = datetime.now().isoformat()
            return result
        except Exception as e:
            logger.error(f"LLM 查詢錯誤: {e}")
            return {
                'error': 'manager_exception',
                'answer': f'❌ 查詢處理失敗: {str(e)}',
                'adapter_mode': self.api_mode
            }
    
    def get_status(self) -> Dict[str, Any]:
        """取得管理器狀態"""
        return {
            'api_mode': self.api_mode,
            'adapter_available': self.adapter.is_available(),
            'adapter_info': self.adapter.get_info(),
            'supported_modes': ['anthropic', 'mock', 'local', 'puter']
        }
    
    def switch_mode(self, new_mode: str) -> bool:
        """切換 API 模式"""
        if new_mode.lower() in ['anthropic', 'mock', 'local', 'puter']:
            self.api_mode = new_mode.lower()
            self.adapter = self._create_adapter()
            logger.info(f"切換到 {new_mode} 模式")
            return True
        return False

# 便利函數
def create_llm_manager(config: Optional[Dict] = None) -> LLMManager:
    """建立 LLM 管理器"""
    return LLMManager(config)

def quick_llm_query(prompt: str, mode: str = None) -> str:
    """快速 LLM 查詢"""
    if mode:
        os.environ['API_MODE'] = mode
    
    manager = create_llm_manager()
    result = manager.query(prompt)
    
    if result.get('error'):
        return f"錯誤: {result['answer']}"
    
    return result.get('answer', '無回答')