#!/usr/bin/env python3
"""
Test building the vector database for O-RAN × Nephio RAG system
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_build_database():
    """Test building the vector database"""
    print("🔨 Testing vector database building...")

    try:
        from oran_nephio_rag import ORANNephioRAG

        # Initialize RAG system
        print("🚀 Initializing RAG system...")
        rag = ORANNephioRAG()

        # Try to build vector database
        print("📚 Building vector database...")
        print("⚠️ This may take several minutes as it downloads and processes documents...")

        success = rag.build_vector_database()

        if success:
            print("✅ Vector database built successfully!")

            # Test loading the database
            print("🔍 Testing database loading...")
            if rag.load_existing_database():
                print("✅ Database loading successful!")

                # Get system status
                status = rag.get_system_status()
                print("📊 System Status:")
                print(f"   - Vector DB Ready: {status.get('vectordb_ready', False)}")
                print(f"   - Total Sources: {status.get('total_sources', 0)}")
                print(f"   - Document Count: {status.get('vectordb_info', {}).get('document_count', 0)}")

                return True
            else:
                print("❌ Database loading failed")
                return False
        else:
            print("❌ Vector database building failed")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_mock_query():
    """Test a mock query without building database"""
    print("\n🎭 Testing mock query (no database needed)...")

    try:
        from oran_nephio_rag import ORANNephioRAG

        # Initialize RAG system
        rag = ORANNephioRAG()

        # Setup QA chain without database
        rag.setup_qa_chain()

        # Test query with mock mode
        result = rag.query("What is Nephio?")

        if result and not result.get("error"):
            print("✅ Mock query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')[:100]}...")
            return True
        else:
            print(f"❌ Mock query failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Mock query test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 O-RAN × Nephio RAG System - Database Build Test")
    print("=" * 60)

    # First test mock query (quick)
    mock_success = test_mock_query()

    print("\n" + "=" * 60)

    if mock_success:
        print("✅ Mock mode working! System is functional.")
        print("\nOptions:")
        print("1. Continue with database building (takes time)")
        print("2. Skip database building for now")

        choice = input("\nBuild database now? (y/N): ").strip().lower()

        if choice in ["y", "yes"]:
            db_success = test_build_database()

            if db_success:
                print("\n🎉 Full system is ready!")
                print("You can now run: python main.py")
            else:
                print("\n⚠️ Database building failed, but mock mode works")
        else:
            print("\n✅ System ready in mock mode!")
            print("Run: python main.py (will use mock responses)")
    else:
        print("❌ System has issues. Check the errors above.")

    print("=" * 60)
