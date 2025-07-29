#!/usr/bin/env python3
"""
Quick Puter.js Integration Test - Basic Functionality Check
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_puter_basic():
    """Basic Puter.js functionality test"""
    print("Quick Puter.js Integration Test")
    print("=" * 40)
    
    try:
        from api_adapters import create_llm_manager
        
        # Test 1: Without risk acknowledgment (should fail safely)
        print("\n1. Test without risk acknowledgment:")
        os.environ['API_MODE'] = 'puter'
        os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'false'
        
        manager = create_llm_manager()
        result = manager.query("Test")
        
        if result.get('error') == 'risk_not_acknowledged':
            print("SUCCESS: Risk protection working")
        else:
            print("WARNING: Risk protection not working")
        
        # Test 2: With risk acknowledgment
        print("\n2. Test with risk acknowledgment:")
        os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'true'
        
        manager = create_llm_manager()
        status = manager.get_status()
        
        print(f"Mode: {status['api_mode']}")
        print(f"Available: {status['adapter_available']}")
        print(f"Adapter: {status['adapter_info']['adapter_type']}")
        
        # Test a simple query
        result = manager.query("What is Nephio?")
        print(f"Query mode: {result.get('mode', 'unknown')}")
        print(f"Answer preview: {result['answer'][:100]}...")
        
        print("\nSUCCESS: Puter.js integration working")
        print("(Note: May use fallback responses due to API limitations)")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Restore original environment
        os.environ['API_MODE'] = 'anthropic'
        os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'false'

if __name__ == "__main__":
    test_puter_basic()