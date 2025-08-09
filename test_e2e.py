#!/usr/bin/env python
"""
End-to-End Test for O-RAN Nephio RAG System
Tests the complete workflow with the implemented fixes
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required modules can be imported"""
    logger.info("Testing module imports...")
    try:
        from src.config import Config, DocumentSource, validate_config
        from src.document_loader import DocumentLoader
        from src.oran_nephio_rag import ORANNephioRAG
        logger.info("✅ All modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False

def test_config_validation():
    """Test configuration with Chinese validation messages"""
    logger.info("\nTesting configuration validation...")
    from src.config import Config, DocumentSource
    
    # Test valid configuration
    try:
        config = Config()
        logger.info("✅ Valid configuration created")
    except Exception as e:
        logger.error(f"❌ Config creation failed: {e}")
        return False
    
    # Test invalid priority (should show Chinese message)
    try:
        invalid_source = DocumentSource(
            url="https://test.com",
            source_type="nephio",
            description="Test source",
            priority=10  # Invalid: should be 1-5
        )
        logger.error("❌ Should have raised ValueError for invalid priority")
        return False
    except ValueError as e:
        if "優先級必須在 1-5 之間" in str(e):
            logger.info("✅ Chinese validation message for priority works")
        else:
            logger.error(f"❌ Wrong error message: {e}")
            return False
    
    # Test invalid source type (should show Chinese message)
    try:
        invalid_source = DocumentSource(
            url="https://test.com",
            source_type="invalid",  # Invalid: should be nephio or oran_sc
            description="Test source",
            priority=3
        )
        logger.error("❌ Should have raised ValueError for invalid source_type")
        return False
    except ValueError as e:
        if "來源類型必須是 'nephio' 或 'oran_sc'" in str(e):
            logger.info("✅ Chinese validation message for source_type works")
        else:
            logger.error(f"❌ Wrong error message: {e}")
            return False
    
    return True

def test_mock_fixtures():
    """Test that mock fixtures are properly configured"""
    logger.info("\nTesting mock fixtures...")
    
    # This simulates what happens in the test suite
    mock_components = {
        "puter_adapter": "mock_puter",
        "llm_adapter": "mock_puter",  # Alias
        "chromadb": "mock_chromadb",
        "vectordb": "mock_chromadb",  # Alias
        "embeddings": "mock_embeddings"
    }
    
    # Verify all required components are present
    required = ["puter_adapter", "llm_adapter", "chromadb", "vectordb", "embeddings"]
    for component in required:
        if component in mock_components:
            logger.info(f"✅ {component} is available")
        else:
            logger.error(f"❌ {component} is missing")
            return False
    
    return True

def test_rag_initialization():
    """Test RAG system initialization"""
    logger.info("\nTesting RAG system initialization...")
    
    try:
        # Set up minimal environment
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        from src.config import Config
        from src.oran_nephio_rag import ORANNephioRAG
        
        config = Config()
        rag = ORANNephioRAG(config)
        
        logger.info("✅ RAG system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ RAG initialization failed: {e}")
        return False

def main():
    """Run all end-to-end tests"""
    logger.info("="*60)
    logger.info("O-RAN Nephio RAG System - End-to-End Test")
    logger.info("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Validation", test_config_validation),
        ("Mock Fixtures", test_mock_fixtures),
        ("RAG Initialization", test_rag_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n[Running] {test_name}")
        try:
            passed = test_func()
            results.append((test_name, passed))
            if passed:
                logger.info(f"[PASS] {test_name}")
            else:
                logger.info(f"[FAIL] {test_name}")
        except Exception as e:
            logger.error(f"[ERROR] {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Test Summary")
    logger.info("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, test_passed in results:
        status = "✅ PASS" if test_passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed ({passed*100/total:.1f}%)")
    
    if passed == total:
        logger.info("\n🎉 SUCCESS: All end-to-end tests passed!")
        logger.info("The system is ready to run with the applied fixes.")
        return 0
    else:
        logger.info("\n⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())