#!/usr/bin/env python3
"""
Basic system test for O-RAN × Nephio RAG system
Tests core functionality without requiring API keys
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_config_loading():
    """Test configuration loading"""
    print("🔧 Testing configuration loading...")
    
    try:
        from config import Config, DocumentSource
        config = Config()
        print(f"✅ Config loaded successfully")
        print(f"   - API Mode: {config.API_MODE}")
        print(f"   - Vector DB Path: {config.VECTOR_DB_PATH}")
        print(f"   - Log Level: {config.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_document_loader():
    """Test document loader initialization"""
    print("\n📄 Testing document loader...")
    
    try:
        from document_loader import DocumentLoader, DocumentContentCleaner
        from config import Config
        
        config = Config()
        loader = DocumentLoader(config)
        cleaner = DocumentContentCleaner(config)
        
        print("✅ DocumentLoader initialized successfully")
        print("✅ DocumentContentCleaner initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Document loader test failed: {e}")
        return False

def test_mock_mode():
    """Test if we can run in mock mode"""
    print("\n🎭 Testing mock mode...")
    
    try:
        # Set mock mode
        os.environ['API_MODE'] = 'mock'
        
        from config import Config
        config = Config()
        
        if config.API_MODE == 'mock':
            print("✅ Mock mode configured successfully")
            return True
        else:
            print(f"❌ Mock mode not set correctly: {config.API_MODE}")
            return False
    except Exception as e:
        print(f"❌ Mock mode test failed: {e}")
        return False

def test_directory_structure():
    """Test required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'src',
        'tests', 
        'logs',
        'examples',
        'monitoring'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ exists")
        else:
            print(f"⚠️ {dir_name}/ missing")
            all_good = False
    
    return all_good

def test_environment_file():
    """Test environment configuration"""
    print("\n🌍 Testing environment configuration...")
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
        
        # Check if it has basic structure
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'API_MODE' in content:
                    print("✅ .env contains API_MODE")
                else:
                    print("⚠️ .env missing API_MODE")
                
                if 'ANTHROPIC_API_KEY' in content:
                    print("✅ .env contains ANTHROPIC_API_KEY placeholder")
                else:
                    print("⚠️ .env missing ANTHROPIC_API_KEY")
                    
                return True
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
            return False
    else:
        print("❌ .env file missing")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 O-RAN × Nephio RAG System - Basic System Test")
    print("=" * 60)
    
    tests = [
        test_config_loading,
        test_document_loader,
        test_mock_mode,
        test_directory_structure,
        test_environment_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\nNext steps to make it fully functional:")
        print("1. Install remaining dependencies:")
        print("   pip install langchain-anthropic sentence-transformers chromadb")
        print("2. Set up API key in .env file:")
        print("   ANTHROPIC_API_KEY=your-actual-api-key")
        print("3. Try running: python main.py")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    print("=" * 60)