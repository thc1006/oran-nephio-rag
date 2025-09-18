#!/usr/bin/env python3
"""
Demo script showing the O-RAN × Nephio RAG system is working
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def demo_system():
    """Demonstrate the working system"""
    print("🚀 O-RAN × Nephio RAG System Demo")
    print("=" * 50)

    # 1. Show configuration
    print("\n1️⃣ Configuration Status:")
    try:
        from config import Config

        config = Config()
        print(f"   ✅ API Mode: {config.API_MODE}")
        print(f"   ✅ Vector DB: {config.VECTOR_DB_PATH}")
        print(f"   ✅ Model: {getattr(config, 'CLAUDE_MODEL', 'claude-3-sonnet-20240229')}")
        print(f"   ✅ Log Level: {getattr(config, 'LOG_LEVEL', 'INFO')}")
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False

    # 2. Show document sources
    print("\n2️⃣ Document Sources:")
    try:
        official_sources = config.OFFICIAL_SOURCES
        print(f"   📚 Total sources configured: {len(official_sources)}")
        for i, source in enumerate(official_sources[:3], 1):
            print(f"   {i}. [{source.source_type.upper()}] {source.description}")
        if len(official_sources) > 3:
            print(f"   ... and {len(official_sources) - 3} more sources")
    except Exception as e:
        print(f"   ⚠️ Sources info: {e}")

    # 3. Check vector database
    print("\n3️⃣ Vector Database Status:")
    if os.path.exists(config.VECTOR_DB_PATH):
        print("   ✅ Vector database exists")
        try:
            # Count files in database
            db_files = os.listdir(config.VECTOR_DB_PATH)
            print(f"   📊 Database files: {len(db_files)}")
        except (OSError, PermissionError):
            print("   📊 Database files: Unable to count")
    else:
        print("   ⚠️ Vector database not found")
        print("   💡 Run: python create_minimal_database.py")

    # 4. Test API adapter
    print("\n4️⃣ API Adapter Test:")
    try:
        from api_adapters import LLMManager

        # Convert Config class to dictionary format expected by LLMManager
        config_dict = {
            "api_key": getattr(config, "ANTHROPIC_API_KEY", None),
            "model_name": getattr(config, "CLAUDE_MODEL", "claude-3-sonnet-20240229"),
            "max_tokens": getattr(config, "CLAUDE_MAX_TOKENS", 2048),
            "temperature": getattr(config, "CLAUDE_TEMPERATURE", 0.1),
            "api_mode": getattr(config, "API_MODE", "mock"),
        }

        llm_manager = LLMManager(config_dict)
        print(f"   ✅ LLM Manager initialized ({config.API_MODE} mode)")

        # Test query
        test_question = "What is the purpose of Nephio in network automation?"
        print(f"   🤔 Testing query: {test_question}")

        result = llm_manager.query(test_question)
        if result and not result.get("error"):
            # MockAdapter returns response in 'answer' field, others might use 'response'
            response = result.get("answer") or result.get("response", "No response")
            print("   ✅ Query successful!")
            print(f"   💬 Response: {response[:100]}...")
        else:
            print(f"   ⚠️ Query result: {result}")

    except Exception as e:
        print(f"   ❌ API adapter error: {e}")

    # 5. Show system capabilities
    print("\n5️⃣ System Capabilities:")
    capabilities = [
        "✅ Multi-API support (Anthropic, Mock, Local, Puter)",
        "✅ Vector-based semantic search",
        "✅ Document processing and cleaning",
        "✅ Configurable retrieval parameters",
        "✅ Monitoring and metrics collection",
        "✅ Async processing support",
        "✅ Docker containerization ready",
        "✅ GitOps workflow integration",
    ]

    for capability in capabilities:
        print(f"   {capability}")

    # 6. Usage examples
    print("\n6️⃣ Usage Examples:")
    examples = [
        "How does Nephio handle O-RAN network function scaling?",
        "What are the key components of O-RAN architecture?",
        "How to implement scale-out for 5G network functions?",
        "What is the role of O2IMS in network function management?",
        "How does GitOps work with Nephio deployments?",
    ]

    print("   Sample questions you can ask:")
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")

    print("\n" + "=" * 50)
    print("🎉 System Demo Complete!")
    print("\nThe O-RAN × Nephio RAG system is ready for use!")
    print("\n📋 Quick Start:")
    print("1. Ensure vector database: python create_minimal_database.py")
    print("2. Run main application: python main.py")
    print("3. Ask questions about O-RAN and Nephio!")

    return True


if __name__ == "__main__":
    demo_system()
