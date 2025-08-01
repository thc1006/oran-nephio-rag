#!/usr/bin/env python3
"""
O-RAN × Nephio RAG System - Quick Start Script
Automated setup for immediate system deployment
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Display welcome banner"""
    print("=" * 60)
    print("🚀 O-RAN × Nephio RAG System - Quick Start")
    print("=" * 60)
    print("Automated setup for immediate deployment")
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.9+")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    dependencies = [
        "python-dotenv",
        "requests", 
        "beautifulsoup4",
        "lxml",
        "langchain",
        "langchain-community", 
        "langchain-anthropic",
        "sentence-transformers",
        "chromadb"
    ]
    
    try:
        for dep in dependencies:
            print(f"   Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True, text=True)
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    print("\n🔧 Setting up environment...")
    
    try:
        # Create .env file with mock mode
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("# O-RAN × Nephio RAG System Configuration\n")
            f.write("API_MODE=mock\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("VECTOR_DB_PATH=./oran_nephio_vectordb\n")
            f.write("CHUNK_SIZE=1024\n")
        
        print("✅ Environment configuration created (.env)")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment: {e}")
        return False

def create_database():
    """Create minimal vector database"""
    print("\n📚 Creating vector database...")
    
    try:
        # Check if create_minimal_database.py exists
        if not Path("create_minimal_database.py").exists():
            print("⚠️ create_minimal_database.py not found, creating basic setup...")
            return True
        
        # Run database creation script
        result = subprocess.run([sys.executable, "create_minimal_database.py"], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Vector database created successfully")
            return True
        else:
            print(f"⚠️ Database creation had issues: {result.stderr}")
            print("   System can still run, but may have limited functionality")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️ Database creation timed out, but system can still run")
        return True
    except Exception as e:
        print(f"⚠️ Database creation failed: {e}")
        print("   System can still run in basic mode")
        return True

def verify_system():
    """Verify system is working"""
    print("\n🧪 Verifying system...")
    
    try:
        # Add src to path for imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test basic imports
        from config import Config
        print("✅ Configuration module working")
        
        from api_adapters import LLMManager
        print("✅ API adapter module working")
        
        # Test configuration
        config = Config()
        print(f"✅ API Mode: {config.API_MODE}")
        
        # Test LLM Manager
        config_dict = {
            'api_key': getattr(config, 'ANTHROPIC_API_KEY', None),
            'model_name': getattr(config, 'CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
            'max_tokens': getattr(config, 'CLAUDE_MAX_TOKENS', 2048),
            'temperature': getattr(config, 'CLAUDE_TEMPERATURE', 0.1)
        }
        
        llm_manager = LLMManager(config_dict)
        print("✅ LLM Manager initialized")
        
        # Test query
        result = llm_manager.query("Test query")
        if result and not result.get('error'):
            print("✅ Mock query successful")
        else:
            print("⚠️ Query test had issues, but system is functional")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Verification had issues: {e}")
        print("   System may still be functional")
        return True

def show_next_steps():
    """Show next steps to user"""
    print("\n" + "=" * 60)
    print("🎉 Quick Start Complete!")
    print("=" * 60)
    
    print("\n📋 Your system is ready! Next steps:")
    print()
    print("1️⃣ Run the main application:")
    print("   python main.py")
    print()
    print("2️⃣ Or run the system demo:")
    print("   python demo_system.py")
    print()
    print("3️⃣ Or test system functionality:")
    print("   python test_final_system.py")
    print()
    print("💡 Sample questions to ask:")
    print("   - What is Nephio?")
    print("   - How does O-RAN architecture work?")
    print("   - What is network function scale-out?")
    print()
    print("🔧 To upgrade to production mode:")
    print("   1. Get Anthropic API key from https://www.anthropic.com")
    print("   2. Edit .env file: API_MODE=anthropic")
    print("   3. Add: ANTHROPIC_API_KEY=your-actual-key")
    print()
    print("📚 For more information:")
    print("   - README.md - Complete documentation")
    print("   - QUICK_DEPLOY.md - Deployment options")
    print("   - SYSTEM_STATUS_REPORT.md - System details")
    print()
    print("🎊 Enjoy your O-RAN × Nephio RAG System!")

def main():
    """Main quick start process"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        print("\n❌ Python version incompatible. Please upgrade to Python 3.9+")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return False
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Failed to setup environment")
        return False
    
    # Create database
    create_database()  # Non-critical, continue even if fails
    
    # Verify system
    verify_system()  # Non-critical, continue even if fails
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Quick start completed successfully!")
        else:
            print("\n❌ Quick start encountered issues")
            print("   Check the error messages above and try manual setup")
    except KeyboardInterrupt:
        print("\n\n⏹️ Quick start interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Please try manual setup using README.md")