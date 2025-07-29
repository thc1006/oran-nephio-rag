#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple System Test Script for O-RAN x Nephio RAG System
"""
import sys
import os
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic module imports"""
    print("=== Basic Module Import Test ===")
    results = []
    
    modules = ['requests', 'bs4', 'langchain']
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"[OK] {module_name} import successful")
            results.append(True)
        except ImportError as e:
            print(f"[FAIL] {module_name} import failed: {e}")
            results.append(False)
    
    return all(results)

def test_config_module():
    """Test config module"""
    print("\n=== Config Module Test ===")
    
    try:
        from config import Config, DocumentSource
        print("[OK] config module import successful")
        
        # Test config summary
        summary = Config.get_config_summary()
        print(f"[OK] config summary retrieved: {len(summary)} settings")
        
        # Test document sources
        sources = Config.get_enabled_sources()
        print(f"[OK] enabled document sources: {len(sources)} sources")
        
        return True
    except Exception as e:
        print(f"[FAIL] config module test failed: {e}")
        return False

def test_document_loader():
    """Test document loader"""
    print("\n=== Document Loader Test ===")
    
    try:
        from document_loader import DocumentLoader, create_document_loader
        from config import Config
        
        print("[OK] document_loader module import successful")
        
        # Create test config
        config = Config()
        loader = create_document_loader(config)
        print("[OK] document loader created successfully")
        
        # Test statistics
        stats = loader.get_load_statistics()
        print(f"[OK] load statistics working: {stats}")
        
        return True
    except Exception as e:
        print(f"[FAIL] document_loader module test failed: {e}")
        return False

def test_network_request():
    """Test simple network request"""
    print("\n=== Network Request Test ===")
    
    try:
        import requests
        
        # Test basic request
        response = requests.get('https://httpbin.org/get', timeout=10)
        response.raise_for_status()
        print("[OK] basic network request working")
        
        return True
    except Exception as e:
        print(f"[FAIL] network request test failed: {e}")
        return False

def main():
    """Main test function"""
    print("O-RAN x Nephio RAG System Test")
    print("=" * 50)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print()
    
    test_results = []
    
    # Run tests
    test_results.append(("Basic Module Import", test_basic_imports()))
    test_results.append(("Config Module", test_config_module()))
    test_results.append(("Document Loader", test_document_loader()))
    test_results.append(("Network Request", test_network_request()))
    
    # Calculate results
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n=== Test Results Summary ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Failed tests: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
    
    print(f"\n=== Detailed Results ===")
    for test_name, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
    
    # Save results
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/system_test_report.txt", "w", encoding="utf-8") as f:
            f.write(f"O-RAN x Nephio RAG System Test Report\n")
            f.write(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python version: {sys.version}\n\n")
            f.write(f"Test Results:\n")
            for test_name, result in test_results:
                status = "PASS" if result else "FAIL"  
                f.write(f"- {test_name}: {status}\n")
            f.write(f"\nSuccess rate: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)\n")
        
        print(f"\nTest report saved to: logs/system_test_report.txt")
    except Exception as e:
        print(f"Failed to save test report: {e}")
    
    # Return overall result
    if passed_tests >= total_tests * 0.8:
        print(f"\n[SUCCESS] System test basically passed!")
        return 0
    else:
        print(f"\n[WARNING] System test found issues, needs further investigation")
        return 1

if __name__ == "__main__":
    sys.exit(main())