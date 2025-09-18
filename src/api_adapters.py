"""
API 適配器模組 - Browser Mode Only
支援瀏覽器自動化的 AI 整合方案，完全符合約束要求
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

# Browser automation imports
try:
    from .puter_integration import PuterClaudeAdapter, PuterRAGManager, create_puter_rag_manager
except ImportError:
    from puter_integration import PuterClaudeAdapter

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """LLM 適配器基礎類別"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.model_name = self.config.get("model_name", "unknown")
        self.max_tokens = self.config.get("max_tokens", 2048)
        self.temperature = self.config.get("temperature", 0.1)

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
            "adapter_type": self.__class__.__name__,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


class PuterBrowserAdapter(BaseLLMAdapter):
    """
    瀏覽器自動化 AI 適配器 (主要實現)
    使用 Puter.js 進行 Claude 整合，完全符合約束要求
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.model_name = config.get("model_name", "claude-sonnet-4")
        self.headless = config.get("headless", True)

        # 初始化 Puter.js 適配器
        try:
            self.puter_adapter = PuterClaudeAdapter(model=self.model_name, headless=self.headless)
            logger.info(f"✅ Puter 瀏覽器適配器初始化成功 (模型: {self.model_name})")
        except Exception as e:
            logger.error(f"❌ Puter 適配器初始化失敗: {e}")
            self.puter_adapter = None

    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用瀏覽器自動化執行查詢"""
        if not self.puter_adapter:
            return {"success": False, "error": "Puter adapter not initialized", "answer": "瀏覽器適配器未初始化"}

        try:
            start_time = time.time()

            # 使用 Puter.js 查詢
            result = self.puter_adapter.query(
                prompt=prompt, stream=kwargs.get("stream", False), timeout=kwargs.get("timeout", 60)
            )

            end_time = time.time()

            if result.get("success"):
                return {
                    "success": True,
                    "answer": result.get("answer", ""),
                    "model": result.get("model"),
                    "query_time": round(end_time - start_time, 2),
                    "adapter_mode": "browser_automation",
                    "constraint_compliant": True,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "answer": f"查詢失敗: {result.get('error', '未知錯誤')}",
                }

        except Exception as e:
            logger.error(f"Puter 查詢失敗: {e}")
            return {"success": False, "error": str(e), "answer": f"瀏覽器查詢失敗: {str(e)}"}

    def is_available(self) -> bool:
        """檢查瀏覽器自動化服務是否可用"""
        if not self.puter_adapter:
            return False

        try:
            return self.puter_adapter.is_available()
        except Exception as e:
            logger.error(f"可用性檢查失敗: {e}")
            return False

    def get_info(self) -> Dict[str, Any]:
        """取得適配器資訊"""
        base_info = super().get_info()
        base_info.update(
            {
                "integration_method": "browser_automation",
                "puter_js_enabled": self.puter_adapter is not None,
                "headless_mode": self.headless,
                "constraint_compliant": True,
                "available_models": self.puter_adapter.get_available_models() if self.puter_adapter else [],
            }
        )
        return base_info


class MockAdapter(BaseLLMAdapter):
    """模擬適配器，用於測試和開發"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.model_name = "mock-model"
        self.response_delay = config.get("response_delay", 1.0) if config else 1.0

    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """模擬查詢回應"""
        # 模擬處理時間
        time.sleep(self.response_delay)

        mock_responses = [
            "這是一個模擬回應。在實際部署中，這將由瀏覽器自動化系統處理。",
            "O-RAN 是一個開放的無線接取網路架構，旨在促進供應商間的互通性。",
            "Nephio 是一個用於網路功能自動化部署和管理的 Kubernetes 原生專案。",
            "此模擬器展示了 RAG 系統的基本功能。實際系統將使用瀏覽器整合提供真實回答。",
        ]

        # 基於提示選擇回應
        response_idx = len(prompt) % len(mock_responses)
        answer = mock_responses[response_idx]

        return {
            "success": True,
            "answer": answer,
            "model": self.model_name,
            "adapter_mode": "mock",
            "query_time": self.response_delay,
            "constraint_compliant": True,
        }

    def is_available(self) -> bool:
        """模擬適配器始終可用"""
        return True

    def get_info(self) -> Dict[str, Any]:
        """取得模擬適配器資訊"""
        base_info = super().get_info()
        base_info.update(
            {"integration_method": "mock", "response_delay": self.response_delay, "constraint_compliant": True}
        )
        return base_info


class LLMAdapterManager:
    """
    LLM 適配器管理器 - Browser Only Version
    只支援瀏覽器自動化模式，確保約束合規
    """

    SUPPORTED_ADAPTERS = {"browser": PuterBrowserAdapter, "mock": MockAdapter}

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.current_adapter = None
        self.adapter_type = None
        self._initialize_adapter()

    def _initialize_adapter(self):
        """初始化適配器"""
        # 只支援瀏覽器模式和模擬模式
        adapter_type = self.config.get("adapter_type", "browser")

        if adapter_type not in self.SUPPORTED_ADAPTERS:
            logger.warning(f"不支援的適配器類型: {adapter_type}，使用瀏覽器模式")
            adapter_type = "browser"

        try:
            adapter_class = self.SUPPORTED_ADAPTERS[adapter_type]
            self.current_adapter = adapter_class(self.config)
            self.adapter_type = adapter_type
            logger.info(f"✅ {adapter_type} 適配器初始化成功")
        except Exception as e:
            logger.error(f"❌ 適配器初始化失敗: {e}")
            # 回退到模擬模式
            try:
                self.current_adapter = MockAdapter(self.config)
                self.adapter_type = "mock"
                logger.info("🔄 回退到模擬適配器")
            except Exception as fallback_error:
                logger.error(f"❌ 模擬適配器也初始化失敗: {fallback_error}")
                self.current_adapter = None

    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """執行查詢"""
        if not self.current_adapter:
            return {"success": False, "error": "no_adapter_available", "answer": "沒有可用的適配器"}

        try:
            result = self.current_adapter.query(prompt, **kwargs)
            result["manager_info"] = {"adapter_type": self.adapter_type, "constraint_compliant": True}
            return result
        except Exception as e:
            logger.error(f"查詢執行失敗: {e}")
            return {"success": False, "error": str(e), "answer": f"查詢執行失敗: {str(e)}"}

    def is_available(self) -> bool:
        """檢查當前適配器是否可用"""
        if not self.current_adapter:
            return False
        return self.current_adapter.is_available()

    def get_current_adapter_info(self) -> Dict[str, Any]:
        """取得當前適配器資訊"""
        if not self.current_adapter:
            return {"error": "no_adapter_available"}

        info = self.current_adapter.get_info()
        info["manager_adapter_type"] = self.adapter_type
        info["constraint_compliant"] = True
        return info

    def get_available_llms(self) -> List[str]:
        """取得可用的 LLM 模型列表 (測試相容函數)"""
        if not self.current_adapter:
            return []

        if hasattr(self.current_adapter, "puter_adapter") and self.current_adapter.puter_adapter:
            try:
                return self.current_adapter.puter_adapter.get_available_models()
            except Exception:
                pass

        # 回退到預設模型列表
        return ["claude-sonnet-4", "claude-opus-4", "claude-sonnet-3.5", "mock-model"]

    def get_llm_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """取得指定 LLM 的詳細資訊 (測試相容函數)"""
        if not model_name and self.current_adapter:
            model_name = self.current_adapter.model_name

        # 提供 O-RAN/Nephio 部署中常見的模型資訊
        model_info = {
            "claude-sonnet-4": {
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "context_length": 200000,
                "supported_tasks": ["text_generation", "code_analysis", "oran_questions"],
                "deployment_ready": True,
            },
            "claude-opus-4": {
                "name": "Claude Opus 4",
                "provider": "Anthropic",
                "context_length": 200000,
                "supported_tasks": ["complex_reasoning", "architectural_analysis", "nephio_planning"],
                "deployment_ready": True,
            },
            "claude-sonnet-3.5": {
                "name": "Claude Sonnet 3.5",
                "provider": "Anthropic",
                "context_length": 200000,
                "supported_tasks": ["text_generation", "document_analysis"],
                "deployment_ready": True,
            },
            "mock-model": {
                "name": "Mock Test Model",
                "provider": "Test",
                "context_length": 4000,
                "supported_tasks": ["testing", "development"],
                "deployment_ready": False,
            },
        }

        if model_name in model_info:
            info = model_info[model_name].copy()
            info["current_adapter"] = self.adapter_type if self.current_adapter else None
            info["available"] = self.is_available()
            return info
        else:
            return {
                "name": model_name or "Unknown",
                "provider": "Unknown",
                "context_length": 0,
                "supported_tasks": [],
                "deployment_ready": False,
                "current_adapter": self.adapter_type,
                "available": False,
            }

    def switch_adapter(self, new_adapter_type: str) -> bool:
        """切換適配器"""
        if new_adapter_type not in self.SUPPORTED_ADAPTERS:
            logger.error(f"不支援的適配器類型: {new_adapter_type}")
            return False

        try:
            adapter_class = self.SUPPORTED_ADAPTERS[new_adapter_type]
            new_adapter = adapter_class(self.config)

            if new_adapter.is_available():
                self.current_adapter = new_adapter
                self.adapter_type = new_adapter_type
                logger.info(f"✅ 成功切換到 {new_adapter_type} 適配器")
                return True
            else:
                logger.error(f"❌ 新適配器 {new_adapter_type} 不可用")
                return False

        except Exception as e:
            logger.error(f"❌ 適配器切換失敗: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """取得管理器狀態"""
        return {
            "current_adapter": self.adapter_type,
            "available_adapters": list(self.SUPPORTED_ADAPTERS.keys()),
            "available_llms": self.get_available_llms(),
            "adapter_available": self.is_available(),
            "adapter_info": self.get_current_adapter_info(),
            "constraint_compliant": True,
            "last_check": datetime.now().isoformat(),
        }


# 工廠函數
def create_llm_adapter_manager(config: Optional[Dict] = None) -> LLMAdapterManager:
    """建立 LLM 適配器管理器"""
    return LLMAdapterManager(config)


def create_browser_adapter(model: str = "claude-sonnet-4", headless: bool = True) -> PuterBrowserAdapter:
    """建立瀏覽器適配器"""
    config = {"model_name": model, "headless": headless}
    return PuterBrowserAdapter(config)


# 向後相容的別名和函數
BrowserLLMAdapter = PuterBrowserAdapter
LLMManager = LLMAdapterManager


# Test compatibility functions (for legacy test suites)
def get_available_llms() -> List[str]:
    """取得可用 LLM 列表的全域函數 (測試相容)"""
    manager = LLMManager()
    return manager.get_available_llms()


def get_llm_info(model_name: str) -> Dict[str, Any]:
    """取得 LLM 資訊的全域函數 (測試相容)"""
    manager = LLMManager()
    return manager.get_llm_info(model_name)
