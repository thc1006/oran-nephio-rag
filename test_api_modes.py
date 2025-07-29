#!/usr/bin/env python3
"""
O-RAN × Nephio RAG 系統 - API 模式測試腳本
測試不同的 API 適配器模式是否正常運作
"""

import os
import sys
import time
from typing import Dict, Any

# 確保可以導入本地模組
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from api_adapters import LLMManager, create_llm_manager, quick_llm_query
    from config import Config
except ImportError as e:
    print(f"❌ 無法導入必要模組: {e}")
    print("請確認已安裝所有依賴套件")
    sys.exit(1)

def test_api_mode(mode: str, test_query: str = "什麼是 Nephio？") -> Dict[str, Any]:
    """測試指定的 API 模式"""
    print(f"\n🔍 測試 {mode.upper()} 模式")
    print("=" * 50)
    
    # 設定環境變數
    os.environ['API_MODE'] = mode
    
    try:
        # 創建管理器
        manager = create_llm_manager()
        
        # 檢查狀態
        status = manager.get_status()
        print(f"📊 適配器狀態:")
        print(f"   - 模式: {status['api_mode']}")
        print(f"   - 可用: {status['adapter_available']}")
        print(f"   - 適配器: {status['adapter_info']['adapter_type']}")
        print(f"   - 模型: {status['adapter_info']['model_name']}")
        
        if not status['adapter_available']:
            print(f"⚠️  {mode} 模式不可用")
            return {
                "mode": mode,
                "available": False,
                "error": "adapter_not_available"
            }
        
        # 執行測試查詢
        print(f"\n💬 測試查詢: {test_query}")
        start_time = time.time()
        result = manager.query(test_query)
        end_time = time.time()
        
        print(f"⏱️  查詢時間: {end_time - start_time:.2f} 秒")
        
        if result.get('error'):
            print(f"❌ 查詢失敗: {result['error']}")
            print(f"💬 回答: {result['answer']}")
            return {
                "mode": mode,
                "available": True,
                "success": False,
                "error": result['error'],
                "query_time": end_time - start_time
            }
        else:
            print(f"✅ 查詢成功")
            print(f"💬 回答: {result['answer'][:200]}...")
            return {
                "mode": mode,
                "available": True,
                "success": True,
                "query_time": end_time - start_time,
                "answer_length": len(result['answer'])
            }
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return {
            "mode": mode,
            "available": False,
            "success": False,
            "error": str(e)
        }

def test_config_validation():
    """測試配置驗證"""
    print("\n🔧 測試配置驗證")
    print("=" * 50)
    
    try:
        # 測試不同的 API 模式配置
        test_modes = ['anthropic', 'mock', 'local']
        
        for mode in test_modes:
            print(f"\n測試 {mode} 模式配置...")
            os.environ['API_MODE'] = mode
            
            try:
                config = Config()
                summary = config.get_config_summary()
                print(f"✅ {mode} 模式配置有效")
                print(f"   - API 模式: {summary['api_mode']}")
                
                # 模式特定資訊
                if mode == 'anthropic':
                    api_available = summary.get('anthropic_api_available', False)
                    print(f"   - API 可用: {api_available}")
                elif mode == 'local':
                    print(f"   - 本地模型 URL: {summary.get('local_model_url')}")
                    print(f"   - 本地模型名稱: {summary.get('local_model_name')}")
                    
            except Exception as e:
                print(f"❌ {mode} 模式配置錯誤: {str(e)}")
                
    except Exception as e:
        print(f"❌ 配置驗證失敗: {str(e)}")

def test_mode_switching():
    """測試模式切換功能"""
    print("\n🔄 測試模式切換")
    print("=" * 50)
    
    try:
        # 創建管理器 (預設模式)
        manager = create_llm_manager()
        original_mode = manager.get_status()['api_mode']
        print(f"🎯 原始模式: {original_mode}")
        
        # 測試切換到不同模式
        test_modes = ['mock', 'anthropic']
        
        for target_mode in test_modes:
            if target_mode != original_mode:
                print(f"\n切換到 {target_mode} 模式...")
                success = manager.switch_mode(target_mode)
                
                if success:
                    current_status = manager.get_status()
                    print(f"✅ 成功切換到 {current_status['api_mode']} 模式")
                    print(f"   - 適配器: {current_status['adapter_info']['adapter_type']}")
                    print(f"   - 可用: {current_status['adapter_available']}")
                else:
                    print(f"❌ 切換到 {target_mode} 模式失敗")
        
        # 切換回原始模式
        print(f"\n切換回 {original_mode} 模式...")
        manager.switch_mode(original_mode)
        final_status = manager.get_status()
        print(f"🎯 最終模式: {final_status['api_mode']}")
        
    except Exception as e:
        print(f"❌ 模式切換測試失敗: {str(e)}")

def test_quick_query_function():
    """測試快速查詢函數"""
    print("\n⚡ 測試快速查詢函數")
    print("=" * 50)
    
    test_query = "簡單說明 O-RAN 架構"
    
    # 測試不同模式的快速查詢
    modes = ['mock', 'anthropic']
    
    for mode in modes:
        print(f"\n測試 {mode} 模式快速查詢...")
        try:
            result = quick_llm_query(test_query, mode=mode)
            print(f"✅ {mode} 模式查詢成功")
            print(f"💬 回答: {result[:150]}...")
        except Exception as e:
            print(f"❌ {mode} 模式查詢失敗: {str(e)}")

def main():
    """主測試函數"""
    print("🚀 O-RAN × Nephio RAG - API 模式測試")
    print("=" * 60)
    
    # 儲存原始環境變數
    original_api_mode = os.environ.get('API_MODE', 'anthropic')
    
    try:
        # 1. 測試配置驗證
        test_config_validation()
        
        # 2. 測試各種 API 模式
        test_modes = ['mock', 'anthropic', 'local']
        results = []
        
        for mode in test_modes:
            result = test_api_mode(mode)
            results.append(result)
        
        # 3. 測試模式切換
        test_mode_switching()
        
        # 4. 測試快速查詢函數
        test_quick_query_function()
        
        # 5. 總結測試結果
        print("\n📊 測試結果總結")
        print("=" * 50)
        
        for result in results:
            mode = result['mode']
            available = result.get('available', False)
            success = result.get('success', False)
            
            status_icon = "✅" if (available and success) else "⚠️" if available else "❌"
            print(f"{status_icon} {mode.upper()} 模式: ", end="")
            
            if available and success:
                query_time = result.get('query_time', 0)
                print(f"正常運作 (查詢時間: {query_time:.2f}s)")
            elif available:
                error = result.get('error', 'unknown')
                print(f"可用但查詢失敗 ({error})")
            else:
                print("不可用")
        
        print(f"\n🎯 推薦使用順序:")
        print(f"   1. anthropic 模式 (需要有效 API 金鑰)")
        print(f"   2. local 模式 (需要本地模型服務)")
        print(f"   3. mock 模式 (測試和開發用)")
        
    finally:
        # 恢復原始環境變數
        os.environ['API_MODE'] = original_api_mode
        print(f"\n✅ 已恢復原始 API 模式: {original_api_mode}")

if __name__ == "__main__":
    main()