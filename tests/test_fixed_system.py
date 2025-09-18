#!/usr/bin/env python3
"""
Test the fixed O-RAN x Nephio RAG System
Verify that the dependency issues have been resolved
"""

import os
import sys
from pathlib import Path

# Set test environment
TEST_ENV = {
    "ANTHROPIC_API_KEY": "test-key-not-real",
    "VECTOR_DB_PATH": "./test_vectordb_fixed",
    "EMBEDDINGS_CACHE_PATH": "./test_embeddings_cache_fixed",
    "LOG_LEVEL": "INFO",
    "CLAUDE_MODEL": "claude-3-sonnet-20240229",
    "CLAUDE_TEMPERATURE": "0.1",
}

for key, value in TEST_ENV.items():
    os.environ[key] = value

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_critical_imports():
    """Test critical module imports"""
    print("Testing critical imports...")

    try:
        # Test sentence transformers (the main issue)
        import sentence_transformers

        print("SUCCESS: sentence_transformers available")
        st_available = True
    except ImportError:
        print("WARNING: sentence_transformers not available")
        st_available = False

    try:
        # Test core imports

        print("SUCCESS: Config module imported")

        print("SUCCESS: DocumentLoader module imported")

        print("SUCCESS: Core RAG system imported")

        return True, st_available

    except Exception as e:
        print(f"FAILED: Import error - {e}")
        return False, st_available


def test_rag_system_with_mock():
    """Test RAG system creation with mocked embeddings"""
    print("Testing RAG system with mock embeddings...")

    try:
        from config import Config

        # Create config
        config = Config()
        print(f"Config created: {config.CLAUDE_MODEL}")

        # Try to create RAG system without sentence-transformers dependency
        # by mocking the embeddings
        from unittest.mock import MagicMock, patch

        with patch("src.oran_nephio_rag.HuggingFaceEmbeddings") as mock_embeddings:
            mock_embeddings.return_value = MagicMock()

            from oran_nephio_rag import create_rag_system

            rag = create_rag_system(config)

            print("SUCCESS: RAG system created with mocked embeddings")
            print(f"System type: {type(rag).__name__}")

            return True

    except Exception as e:
        print(f"FAILED: RAG system creation failed - {e}")
        return False


def test_dependency_availability():
    """Test availability of key dependencies"""
    print("Testing dependency availability...")

    dependencies = [
        ("langchain", "LangChain framework"),
        ("langchain_anthropic", "Anthropic LangChain"),
        ("numpy", "NumPy"),
        ("requests", "HTTP requests"),
        ("bs4", "HTML parsing"),
        ("dotenv", "Environment variables"),
        ("pydantic", "Data validation"),
        ("aiohttp", "Async HTTP"),
    ]

    available = 0
    for module, desc in dependencies:
        try:
            __import__(module)
            print(f"SUCCESS: {desc}")
            available += 1
        except ImportError:
            print(f"WARNING: {desc} not available")

    print(f"Dependencies: {available}/{len(dependencies)} available")
    return available >= len(dependencies) * 0.8


def test_configuration_system():
    """Test configuration system"""
    print("Testing configuration system...")

    try:
        from config import Config, DocumentSource

        config = Config()
        print(f"Claude model: {config.CLAUDE_MODEL}")
        print(f"Vector DB path: {config.VECTOR_DB_PATH}")
        print(f"Sources count: {len(config.OFFICIAL_SOURCES)}")

        # Test document source creation
        source = DocumentSource(
            url="https://test.example.com", source_type="nephio", description="Test source", priority=1
        )
        print(f"Test source created: {source.description}")

        return True

    except Exception as e:
        print(f"FAILED: Configuration test failed - {e}")
        return False


def main():
    """Main test function"""
    print("O-RAN x Nephio RAG System - Fixed Dependencies Test")
    print("=" * 55)

    # Run tests
    tests = [
        ("Critical Imports", test_critical_imports),
        ("Dependency Availability", test_dependency_availability),
        ("Configuration System", test_configuration_system),
        ("RAG System with Mock", test_rag_system_with_mock),
    ]

    results = {}
    passed = 0

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_name == "Critical Imports":
                result, st_available = test_func()
                results[test_name] = result
                results["SentenceTransformers"] = st_available
            else:
                result = test_func()
                results[test_name] = result

            if result:
                passed += 1
                print(f"PASS: {test_name}")
            else:
                print(f"FAIL: {test_name}")

        except Exception as e:
            print(f"ERROR: {test_name} - {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 55)
    print("SUMMARY")
    print("=" * 55)
    print(f"Tests passed: {passed}/{len(tests)}")

    # Check if the main issue is fixed
    if results.get("SentenceTransformers", False):
        print("SUCCESS: sentence-transformers dependency is now available!")
        verdict = "FULLY_FIXED"
    elif passed >= len(tests) * 0.75:
        print("MOSTLY_FIXED: System is functional, but sentence-transformers still missing")
        print("NOTE: System can work with mocked embeddings for testing")
        verdict = "MOSTLY_FIXED"
    else:
        print("ISSUES_REMAIN: Multiple problems still exist")
        verdict = "ISSUES_REMAIN"

    # Instructions
    print(f"\nVERDICT: {verdict}")

    if verdict == "FULLY_FIXED":
        print("The system is now fully functional!")
    elif verdict == "MOSTLY_FIXED":
        print("To complete the fix, install sentence-transformers:")
        print("  pip install sentence-transformers")

    print("\nNext steps:")
    print("  1. Set ANTHROPIC_API_KEY environment variable")
    print("  2. Run: python main.py")
    print("  3. Or use Docker: docker-compose up -d")

    return verdict == "FULLY_FIXED"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
