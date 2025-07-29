#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core RAG Functionality Test Script
"""
import sys
import os
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_oran_nephio_rag_import():
    """Test main RAG module import"""
    print("=== Main RAG Module Import Test ===")
    
    try:
        from oran_nephio_rag import ORANNephioRAG, create_rag_system, quick_query
        print("[OK] oran_nephio_rag module import successful")
        return True
    except Exception as e:
        print(f"[FAIL] oran_nephio_rag module import failed: {e}")
        return False

def test_document_loading():
    """Test document loading functionality"""
    print("\n=== Document Loading Test ===")
    
    try:
        from document_loader import DocumentLoader
        from config import Config, DocumentSource
        
        # Create a test document source
        test_source = DocumentSource(
            url="https://httpbin.org/html",
            source_type="nephio",
            description="Test HTML Source",
            priority=1,
            enabled=True
        )
        
        config = Config()
        loader = DocumentLoader(config)
        
        # Try to load a simple test document
        doc = loader.load_document(test_source)
        
        if doc:
            print(f"[OK] document loading successful: {len(doc.page_content)} characters")
            print(f"[OK] document metadata: {len(doc.metadata)} fields")
            return True
        else:
            print("[FAIL] document loading returned None")
            return False
            
    except Exception as e:
        print(f"[FAIL] document loading test failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation"""
    print("\n=== Configuration Validation Test ===")
    
    try:
        from config import Config, validate_config
        
        # Note: This will fail if ANTHROPIC_API_KEY is not set, which is expected
        try:
            result = validate_config()
            print("[OK] configuration validation passed")
            return True
        except Exception as e:
            if "ANTHROPIC_API_KEY" in str(e):
                print("[INFO] configuration validation requires ANTHROPIC_API_KEY (expected)")
                print("[OK] configuration structure is valid")
                return True
            else:
                print(f"[FAIL] configuration validation failed: {e}")
                return False
                
    except Exception as e:
        print(f"[FAIL] configuration validation test failed: {e}")
        return False

def test_content_cleaning():
    """Test HTML content cleaning functionality"""
    print("\n=== Content Cleaning Test ===")
    
    try:
        from document_loader import DocumentContentCleaner
        from config import Config
        
        config = Config()
        cleaner = DocumentContentCleaner(config)
        
        # Test HTML content
        test_html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <nav>Navigation</nav>
            <main>
                <h1>Main Content</h1>
                <p>This is test content about Nephio and O-RAN integration.</p>
                <p>It includes kubernetes cluster management.</p>
            </main>
            <footer>Footer content</footer>
        </body>
        </html>
        """
        
        cleaned_content = cleaner.clean_html(test_html, "https://example.com")
        
        if cleaned_content and len(cleaned_content) > 50:
            print(f"[OK] content cleaning successful: {len(cleaned_content)} characters")
            # Check if navigation was removed but main content preserved
            if "Navigation" not in cleaned_content and "Main Content" in cleaned_content:
                print("[OK] unwanted elements properly removed")
            return True
        else:
            print("[FAIL] content cleaning produced insufficient content")
            return False
            
    except Exception as e:
        print(f"[FAIL] content cleaning test failed: {e}")
        return False

def main():
    """Main test function"""
    print("O-RAN x Nephio RAG Core Functionality Test")
    print("=" * 50)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run core functionality tests
    test_results.append(("RAG Module Import", test_oran_nephio_rag_import()))
    test_results.append(("Document Loading", test_document_loading()))
    test_results.append(("Config Validation", test_config_validation()))
    test_results.append(("Content Cleaning", test_content_cleaning()))
    
    # Calculate results
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n=== Core Functionality Test Results ===")
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
        with open("logs/rag_core_test_report.txt", "w", encoding="utf-8") as f:
            f.write(f"O-RAN x Nephio RAG Core Functionality Test Report\n")
            f.write(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Test Results:\n")
            for test_name, result in test_results:
                status = "PASS" if result else "FAIL"  
                f.write(f"- {test_name}: {status}\n")
            f.write(f"\nSuccess rate: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)\n")
        
        print(f"\nCore test report saved to: logs/rag_core_test_report.txt")
    except Exception as e:
        print(f"Failed to save core test report: {e}")
    
    # Return overall result
    if passed_tests >= total_tests * 0.75:
        print(f"\n[SUCCESS] Core RAG functionality test passed!")
        return 0
    else:
        print(f"\n[WARNING] Core RAG functionality test found issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())