#!/usr/bin/env python3
"""
O-RAN × Nephio RAG System - System Verification
Quick health check and status verification
"""
import os
import sys
from pathlib import Path


def print_header():
    """Print verification header"""
    print("🔍 O-RAN × Nephio RAG System Verification")
    print("=" * 50)


def check_files():
    """Check required files exist"""
    print("\n📁 File Structure Check:")

    required_files = [
        "main.py",
        "src/config.py",
        "src/oran_nephio_rag.py",
        "src/api_adapters.py",
        "src/document_loader.py",
        ".env",
        "requirements.txt",
    ]

    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_good = False

    return all_good


def check_environment():
    """Check environment configuration"""
    print("\n🌍 Environment Check:")

    if not Path(".env").exists():
        print("   ❌ .env file missing")
        return False

    try:
        with open(".env", "r") as f:
            content = f.read()

        if "API_MODE" in content:
            print("   ✅ API_MODE configured")
        else:
            print("   ⚠️ API_MODE not found")

        # Extract API mode
        for line in content.split("\n"):
            if line.startswith("API_MODE="):
                mode = line.split("=")[1].strip()
                print(f"   📋 Current mode: {mode}")
                break

        return True
    except Exception as e:
        print(f"   ❌ Error reading .env: {e}")
        return False


def check_imports():
    """Check if core modules can be imported"""
    print("\n📦 Import Check:")

    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

    modules = [("config", "Config"), ("api_adapters", "LLMManager"), ("document_loader", "DocumentLoader")]

    all_good = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}.{class_name} - Import Error: {e}")
            all_good = False
        except AttributeError as e:
            print(f"   ❌ {module_name}.{class_name} - Attribute Error: {e}")
            all_good = False
        except Exception as e:
            print(f"   ❌ {module_name}.{class_name} - Error: {e}")
            all_good = False

    return all_good


def check_database():
    """Check vector database status"""
    print("\n🗄️ Database Check:")

    db_path = Path("oran_nephio_vectordb")
    if db_path.exists():
        print("   ✅ Vector database directory exists")

        # Count files in database
        try:
            files = list(db_path.iterdir())
            print(f"   📊 Database files: {len(files)}")
            return True
        except Exception as e:
            print(f"   ⚠️ Could not read database: {e}")
            return True
    else:
        print("   ⚠️ Vector database not found")
        print("   💡 Run: python create_minimal_database.py")
        return False


def test_basic_functionality():
    """Test basic system functionality"""
    print("\n🧪 Functionality Test:")

    try:
        # Import required modules
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        from api_adapters import LLMManager
        from config import Config

        # Test configuration
        config = Config()
        print(f"   ✅ Configuration loaded (Mode: {config.API_MODE})")

        # Test LLM Manager
        config_dict = {
            "api_key": getattr(config, "ANTHROPIC_API_KEY", None),
            "model_name": getattr(config, "CLAUDE_MODEL", "claude-3-sonnet-20240229"),
            "max_tokens": getattr(config, "CLAUDE_MAX_TOKENS", 2048),
            "temperature": getattr(config, "CLAUDE_TEMPERATURE", 0.1),
        }

        llm_manager = LLMManager(config_dict)
        print("   ✅ LLM Manager initialized")

        # Test query
        result = llm_manager.query("System test query")
        if result and not result.get("error"):
            print("   ✅ Query functionality working")
            return True
        else:
            print(f"   ⚠️ Query test issue: {result.get('error', 'Unknown')}")
            return False

    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False


def show_recommendations():
    """Show recommendations based on verification results"""
    print("\n💡 Recommendations:")

    # Check if main components are working
    if Path("main.py").exists() and Path(".env").exists():
        print("   🚀 Ready to run: python main.py")

    if Path("demo_system.py").exists():
        print("   🎭 Try demo: python demo_system.py")

    if Path("test_final_system.py").exists():
        print("   🧪 Run tests: python test_final_system.py")

    if not Path("oran_nephio_vectordb").exists():
        print("   📚 Create database: python create_minimal_database.py")

    print("   📖 Read documentation: README.md")


def main():
    """Main verification process"""
    print_header()

    # Run all checks
    checks = [
        ("File Structure", check_files),
        ("Environment", check_environment),
        ("Imports", check_imports),
        ("Database", check_database),
        ("Functionality", test_basic_functionality),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   ❌ {check_name} check failed: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Verification Summary:")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {check_name:<15} {status}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 System verification PASSED! Ready to use.")
    elif passed >= total - 1:
        print("⚠️ System mostly functional with minor issues.")
    else:
        print("❌ System has significant issues. Check errors above.")

    show_recommendations()

    return passed >= total - 1


if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
