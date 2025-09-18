#!/usr/bin/env python3
"""
Basic import test for O-RAN × Nephio RAG system
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_basic_imports():
    """Test basic imports without external dependencies"""
    print("🔍 Testing basic Python imports...")

    # Test standard library imports
    try:
        import logging
        import pathlib
        from datetime import datetime
        from typing import Any, Dict, List, Optional

        print("✅ Standard library imports successful")
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
        return False

    # Test if we can at least read the config file
    try:
        config_path = os.path.join("src", "config.py")
        if os.path.exists(config_path):
            print("✅ Config file exists")
        else:
            print("❌ Config file missing")
            return False
    except Exception as e:
        print(f"❌ Config file check failed: {e}")
        return False

    # Test if main.py exists and is readable
    try:
        if os.path.exists("main.py"):
            print("✅ Main.py exists")
        else:
            print("❌ Main.py missing")
            return False
    except Exception as e:
        print(f"❌ Main.py check failed: {e}")
        return False

    # Test if requirements.txt exists
    try:
        if os.path.exists("requirements.txt"):
            print("✅ Requirements.txt exists")
            with open("requirements.txt", "r") as f:
                lines = f.readlines()
                print(f"📦 Found {len(lines)} dependency lines")
        else:
            print("❌ Requirements.txt missing")
            return False
    except Exception as e:
        print(f"❌ Requirements.txt check failed: {e}")
        return False

    return True


def check_environment():
    """Check environment setup"""
    print("\n🌍 Checking environment...")

    # Check Python version
    print(f"🐍 Python version: {sys.version}")

    # Check if .env.example exists
    if os.path.exists(".env.example"):
        print("✅ .env.example exists")
    else:
        print("❌ .env.example missing")

    # Check if .env exists
    if os.path.exists(".env"):
        print("✅ .env exists")
    else:
        print("⚠️ .env not found (copy from .env.example)")

    # Check directory structure
    required_dirs = ["src", "tests", "logs"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️ {dir_name}/ directory missing")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 O-RAN × Nephio RAG System - Basic Test")
    print("=" * 60)

    success = test_basic_imports()
    check_environment()

    print("\n" + "=" * 60)
    if success:
        print("✅ Basic tests passed! Ready for dependency installation.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and configure API keys")
        print("3. Run: python main.py")
    else:
        print("❌ Basic tests failed! Check the issues above.")
    print("=" * 60)
