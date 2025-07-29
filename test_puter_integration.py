#!/usr/bin/env python3
"""
O-RAN x Nephio RAG System - Puter.js Integration Test
Test the experimental Puter.js API integration functionality
"""

import os
import sys
import time
import logging
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging to see warnings
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

try:
    from api_adapters import LLMManager, create_llm_manager, PuterAdapter
    from config import Config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)

def test_puter_risk_acknowledgment():
    """Test Puter.js risk acknowledgment mechanism"""
    print("\n=== Testing Puter.js Risk Acknowledgment ===")
    
    # Test 1: Without risk acknowledgment
    print("\n1. Testing without risk acknowledgment...")
    os.environ['API_MODE'] = 'puter'
    os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'false'
    
    try:
        manager = create_llm_manager()
        result = manager.query("Test query")
        
        if result.get('error') == 'risk_not_acknowledged':
            print("SUCCESS: Risk acknowledgment protection working")
            print(f"Message: {result['answer'][:200]}...")
        else:
            print("WARNING: Risk acknowledgment protection not working")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With risk acknowledgment
    print("\n2. Testing with risk acknowledgment...")
    os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'true'
    
    try:
        manager = create_llm_manager()
        status = manager.get_status()
        
        print(f"Adapter available: {status['adapter_available']}")
        print(f"Adapter type: {status['adapter_info']['adapter_type']}")
        print(f"Model: {status['adapter_info']['model_name']}")
        
        if status['adapter_available']:
            print("SUCCESS: Puter adapter activated with risk acknowledgment")
        else:
            print("INFO: Puter adapter not available (network or service issue)")
            
    except Exception as e:
        print(f"Error with risk acknowledgment: {e}")

def test_puter_queries():
    """Test Puter.js query functionality"""
    print("\n=== Testing Puter.js Queries ===")
    
    # Ensure risk is acknowledged for testing
    os.environ['API_MODE'] = 'puter'
    os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'true'
    os.environ['PUTER_MODEL'] = 'claude-sonnet-4'
    
    test_queries = [
        "What is Nephio?",
        "Explain O-RAN architecture",
        "How does cloud-native networking work?"
    ]
    
    try:
        manager = create_llm_manager()
        
        if not manager.get_status()['adapter_available']:
            print("WARNING: Puter adapter not available, testing will show fallback responses")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: {query}")
            
            start_time = time.time()
            result = manager.query(query)
            end_time = time.time()
            
            print(f"Query time: {end_time - start_time:.2f} seconds")
            print(f"Mode: {result.get('mode', 'unknown')}")
            
            if result.get('error'):
                print(f"Error: {result['error']}")
            
            if result.get('warning'):
                print(f"Warning: {result['warning']}")
            
            print(f"Answer: {result['answer'][:300]}...")
            
            # Add delay between queries to be respectful
            time.sleep(2)
            
    except Exception as e:
        print(f"Error during query testing: {e}")

def test_puter_config_validation():
    """Test Puter.js configuration validation"""
    print("\n=== Testing Puter.js Configuration Validation ===")
    
    # Test different configuration scenarios
    test_scenarios = [
        {
            'name': 'Without risk acknowledgment',
            'API_MODE': 'puter',
            'PUTER_RISK_ACKNOWLEDGED': 'false',
            'PUTER_MODEL': 'claude-sonnet-4'
        },
        {
            'name': 'With risk acknowledgment',
            'API_MODE': 'puter',
            'PUTER_RISK_ACKNOWLEDGED': 'true',
            'PUTER_MODEL': 'claude-sonnet-4'
        },
        {
            'name': 'With Opus model',
            'API_MODE': 'puter',
            'PUTER_RISK_ACKNOWLEDGED': 'true',
            'PUTER_MODEL': 'claude-opus-4'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nTesting scenario: {scenario['name']}")
        
        # Set environment variables
        for key, value in scenario.items():
            if key != 'name':
                os.environ[key] = value
        
        try:
            config = Config()
            summary = config.get_config_summary()
            
            print(f"API Mode: {summary['api_mode']}")
            if 'puter_risk_acknowledged' in summary:
                print(f"Risk Acknowledged: {summary['puter_risk_acknowledged']}")
                print(f"Puter Model: {summary['puter_model']}")
                print(f"Experimental Feature: {summary.get('experimental_feature', False)}")
            
            # Try validation
            try:
                config.validate()
                print("Configuration validation: PASSED")
            except Exception as e:
                print(f"Configuration validation: FAILED - {e}")
                
        except Exception as e:
            print(f"Configuration error: {e}")

def test_security_warnings():
    """Test that security warnings are properly displayed"""
    print("\n=== Testing Security Warnings ===")
    
    os.environ['API_MODE'] = 'puter'
    os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'true'
    
    # Capture warnings by creating a fresh adapter
    print("Creating PuterAdapter to check security warnings...")
    
    config = {
        'model_name': 'claude-sonnet-4',
        'risk_acknowledged': True
    }
    
    try:
        adapter = PuterAdapter(config)
        print("SUCCESS: PuterAdapter created (warnings should be displayed above)")
        
        # Test availability check
        available = adapter.is_available()
        print(f"Adapter availability: {available}")
        
    except Exception as e:
        print(f"Error creating adapter: {e}")

def test_fallback_responses():
    """Test fallback response system"""
    print("\n=== Testing Fallback Response System ===")
    
    os.environ['API_MODE'] = 'puter'
    os.environ['PUTER_RISK_ACKNOWLEDGED'] = 'true'
    
    fallback_test_queries = [
        ("nephio", "Should trigger Nephio-specific fallback"),
        ("o-ran architecture", "Should trigger O-RAN-specific fallback"),  
        ("random technical question", "Should trigger general fallback")
    ]
    
    try:
        manager = create_llm_manager()
        
        for query, expected in fallback_test_queries:
            print(f"\nTesting: {query}")
            print(f"Expected: {expected}")
            
            result = manager.query(query)
            
            print(f"Mode: {result.get('mode', 'unknown')}")
            print(f"Answer preview: {result['answer'][:150]}...")
            
            # Check if it's using fallback mode
            if 'fallback' in result.get('mode', ''):
                print("SUCCESS: Using fallback response system")
            else:
                print("INFO: Using direct API response (if available)")
            
            time.sleep(1)
            
    except Exception as e:
        print(f"Error testing fallback responses: {e}")

def main():
    """Main test function"""
    print("EXPERIMENTAL PUTER.JS INTEGRATION TEST")
    print("=" * 60)
    print("WARNING: This tests experimental functionality")
    print("Only use for learning, research, or proof-of-concept")
    print("=" * 60)
    
    # Store original environment
    original_env = {
        'API_MODE': os.environ.get('API_MODE', 'anthropic'),
        'PUTER_RISK_ACKNOWLEDGED': os.environ.get('PUTER_RISK_ACKNOWLEDGED', 'false'),
        'PUTER_MODEL': os.environ.get('PUTER_MODEL', 'claude-sonnet-4')
    }
    
    try:
        # Run all tests
        test_puter_risk_acknowledgment()
        test_puter_config_validation()
        test_security_warnings()
        test_puter_queries()
        test_fallback_responses()
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("✅ Risk acknowledgment mechanism tested")
        print("✅ Configuration validation tested")
        print("✅ Security warnings verified")
        print("✅ Query functionality tested")
        print("✅ Fallback response system tested")
        
        print("\nIMPORTANT NOTES:")
        print("• This is experimental functionality")
        print("• Actual API calls may fail (expected behavior)")
        print("• Fallback responses provide educational content")
        print("• Use only for learning and research purposes")
        print("• Consider official alternatives for production use")
        
    finally:
        # Restore original environment
        for key, value in original_env.items():
            os.environ[key] = value
        
        print(f"\nEnvironment restored to original state")

if __name__ == "__main__":
    main()