#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Program Startup Test Script
"""
import sys
import os
from datetime import datetime

def test_main_import():
    """Test main program import"""
    print("=== Main Program Import Test ===")
    
    try:
        # Try to import main module functions
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Import the main module
        import main
        print("[OK] main module import successful")
        
        # Test if key functions exist
        if hasattr(main, 'setup_logging'):
            print("[OK] setup_logging function available")
        else:
            print("[WARNING] setup_logging function not found")
            
        return True
    except Exception as e:
        print(f"[FAIL] main module import failed: {e}")
        return False

def test_main_dependencies():
    """Test main program dependencies"""
    print("\n=== Main Program Dependencies Test ===")
    
    try:
        # Set up path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test if we can import the core components main.py needs
        from oran_nephio_rag import ORANNephioRAG
        print("[OK] ORANNephioRAG import successful")
        
        from config import Config, validate_config
        print("[OK] Config and validate_config import successful")
        
        return True
    except Exception as e:
        print(f"[FAIL] main program dependencies test failed: {e}")
        return False

def test_logging_setup():
    """Test logging setup functionality"""
    print("\n=== Logging Setup Test ===")
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import main
        
        # Try to setup logging
        main.setup_logging()
        print("[OK] logging setup successful")
        
        # Check if log directory was created
        from config import Config
        config = Config()
        log_dir = os.path.dirname(config.LOG_FILE)
        if os.path.exists(log_dir):
            print("[OK] log directory created successfully")
        else:
            print("[WARNING] log directory not found")
            
        return True
    except Exception as e:
        print(f"[FAIL] logging setup test failed: {e}")
        return False

def test_basic_startup():
    """Test basic program startup without full execution"""
    print("\n=== Basic Startup Test ===")
    
    try:
        # Test that we can at least load the main components
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from config import Config
        config = Config()
        print("[OK] configuration loaded")
        
        from oran_nephio_rag import ORANNephioRAG
        print("[OK] main RAG class available")
        
        # Test config summary
        summary = config.get_config_summary()
        print(f"[OK] config summary available: {len(summary)} settings")
        
        return True
    except Exception as e:
        print(f"[FAIL] basic startup test failed: {e}")
        return False

def main():
    """Main test function"""
    print("O-RAN x Nephio RAG Main Program Startup Test")
    print("=" * 50)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run startup tests
    test_results.append(("Main Import", test_main_import()))
    test_results.append(("Main Dependencies", test_main_dependencies()))
    test_results.append(("Logging Setup", test_logging_setup()))
    test_results.append(("Basic Startup", test_basic_startup()))
    
    # Calculate results
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n=== Main Program Startup Test Results ===")
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
        with open("logs/main_startup_test_report.txt", "w", encoding="utf-8") as f:
            f.write(f"O-RAN x Nephio RAG Main Program Startup Test Report\n")
            f.write(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Test Results:\n")
            for test_name, result in test_results:
                status = "PASS" if result else "FAIL"  
                f.write(f"- {test_name}: {status}\n")
            f.write(f"\nSuccess rate: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)\n")
        
        print(f"\nMain startup test report saved to: logs/main_startup_test_report.txt")
    except Exception as e:
        print(f"Failed to save main startup test report: {e}")
    
    # Return overall result
    if passed_tests >= total_tests * 0.75:
        print(f"\n[SUCCESS] Main program startup test passed!")
        return 0
    else:
        print(f"\n[WARNING] Main program startup test found issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())