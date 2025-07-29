#!/usr/bin/env python3
"""
O-RAN x Nephio RAG System - API Mode Test Script
Test different API adapter modes to ensure they work properly
"""

import os
import sys
import time
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from api_adapters import LLMManager, create_llm_manager, quick_llm_query
    from config import Config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)

def test_api_mode(mode: str, test_query: str = "What is Nephio?") -> Dict[str, Any]:
    """Test specified API mode"""
    print(f"\nTesting {mode.upper()} mode")
    print("=" * 50)
    
    # Set environment variable
    os.environ['API_MODE'] = mode
    
    try:
        # Create manager
        manager = create_llm_manager()
        
        # Check status
        status = manager.get_status()
        print(f"Adapter status:")
        print(f"   - Mode: {status['api_mode']}")
        print(f"   - Available: {status['adapter_available']}")
        print(f"   - Adapter: {status['adapter_info']['adapter_type']}")
        print(f"   - Model: {status['adapter_info']['model_name']}")
        
        if not status['adapter_available']:
            print(f"Warning: {mode} mode not available")
            return {
                "mode": mode,
                "available": False,
                "error": "adapter_not_available"
            }
        
        # Execute test query
        print(f"\nTest query: {test_query}")
        start_time = time.time()
        result = manager.query(test_query)
        end_time = time.time()
        
        print(f"Query time: {end_time - start_time:.2f} seconds")
        
        if result.get('error'):
            print(f"Query failed: {result['error']}")
            print(f"Answer: {result['answer']}")
            return {
                "mode": mode,
                "available": True,
                "success": False,
                "error": result['error'],
                "query_time": end_time - start_time
            }
        else:
            print(f"Query successful")
            print(f"Answer: {result['answer'][:200]}...")
            return {
                "mode": mode,
                "available": True,
                "success": True,
                "query_time": end_time - start_time,
                "answer_length": len(result['answer'])
            }
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return {
            "mode": mode,
            "available": False,
            "success": False,
            "error": str(e)
        }

def test_config_validation():
    """Test configuration validation"""
    print("\nTesting configuration validation")
    print("=" * 50)
    
    try:
        # Test different API mode configurations
        test_modes = ['anthropic', 'mock', 'local']
        
        for mode in test_modes:
            print(f"\nTesting {mode} mode configuration...")
            os.environ['API_MODE'] = mode
            
            try:
                config = Config()
                summary = config.get_config_summary()
                print(f"Success: {mode} mode configuration valid")
                print(f"   - API mode: {summary['api_mode']}")
                
                # Mode-specific information
                if mode == 'anthropic':
                    api_available = summary.get('anthropic_api_available', False)
                    print(f"   - API available: {api_available}")
                elif mode == 'local':
                    print(f"   - Local model URL: {summary.get('local_model_url')}")
                    print(f"   - Local model name: {summary.get('local_model_name')}")
                    
            except Exception as e:
                print(f"Error: {mode} mode configuration error: {str(e)}")
                
    except Exception as e:
        print(f"Configuration validation failed: {str(e)}")

def test_mode_switching():
    """Test mode switching functionality"""
    print("\nTesting mode switching")
    print("=" * 50)
    
    try:
        # Create manager (default mode)
        manager = create_llm_manager()
        original_mode = manager.get_status()['api_mode']
        print(f"Original mode: {original_mode}")
        
        # Test switching to different modes
        test_modes = ['mock', 'anthropic']
        
        for target_mode in test_modes:
            if target_mode != original_mode:
                print(f"\nSwitching to {target_mode} mode...")
                success = manager.switch_mode(target_mode)
                
                if success:
                    current_status = manager.get_status()
                    print(f"Success: Switched to {current_status['api_mode']} mode")
                    print(f"   - Adapter: {current_status['adapter_info']['adapter_type']}")
                    print(f"   - Available: {current_status['adapter_available']}")
                else:
                    print(f"Failed: Could not switch to {target_mode} mode")
        
        # Switch back to original mode
        print(f"\nSwitching back to {original_mode} mode...")
        manager.switch_mode(original_mode)
        final_status = manager.get_status()
        print(f"Final mode: {final_status['api_mode']}")
        
    except Exception as e:
        print(f"Mode switching test failed: {str(e)}")

def main():
    """Main test function"""
    print("O-RAN x Nephio RAG - API Mode Test")
    print("=" * 60)
    
    # Store original environment variable
    original_api_mode = os.environ.get('API_MODE', 'anthropic')
    
    try:
        # 1. Test configuration validation
        test_config_validation()
        
        # 2. Test various API modes
        test_modes = ['mock', 'anthropic', 'local']
        results = []
        
        for mode in test_modes:
            result = test_api_mode(mode)
            results.append(result)
        
        # 3. Test mode switching
        test_mode_switching()
        
        # 4. Summarize test results
        print("\nTest Results Summary")
        print("=" * 50)
        
        for result in results:
            mode = result['mode']
            available = result.get('available', False)
            success = result.get('success', False)
            
            if available and success:
                query_time = result.get('query_time', 0)
                print(f"SUCCESS {mode.upper()} mode: Working normally (query time: {query_time:.2f}s)")
            elif available:
                error = result.get('error', 'unknown')
                print(f"WARNING {mode.upper()} mode: Available but query failed ({error})")
            else:
                print(f"ERROR {mode.upper()} mode: Not available")
        
        print(f"\nRecommended usage order:")
        print(f"   1. anthropic mode (requires valid API key)")
        print(f"   2. local mode (requires local model service)")
        print(f"   3. mock mode (for testing and development)")
        
    finally:
        # Restore original environment variable
        os.environ['API_MODE'] = original_api_mode
        print(f"\nRestored original API mode: {original_api_mode}")

if __name__ == "__main__":
    main()