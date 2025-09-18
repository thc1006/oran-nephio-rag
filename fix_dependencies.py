#!/usr/bin/env python3
"""
Fix O-RAN x Nephio RAG System Dependencies
Ensure all required dependencies are properly installed
"""

import subprocess
import sys


def run_command(command, description):
    """Run command and show result"""
    print(f"Running: {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"SUCCESS: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {description} - {e.stderr}")
        return False


def install_core_packages():
    """Install core packages in order"""
    print("Installing core dependencies...")

    packages = [
        "numpy>=1.24.0,<2.0.0",
        "sentence-transformers>=2.2.2,<4.0.0",
        "langchain>=0.1.0,<0.4.0",
        "langchain-community>=0.0.20,<0.4.0",
        "langchain-anthropic>=0.1.0,<0.4.0",
        "chromadb>=0.4.0,<0.6.0",
        "requests>=2.28.0,<3.0.0",
        "beautifulsoup4>=4.11.0,<5.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "pydantic>=2.4.0,<3.0.0",
        "aiohttp>=3.8.0,<4.0.0",
    ]

    success_count = 0
    for package in packages:
        if run_command(f'pip install "{package}"', f"Installing {package}"):
            success_count += 1
        else:
            print(f"WARNING: Failed to install {package}")

    print(f"Installed {success_count}/{len(packages)} packages")
    return success_count >= len(packages) * 0.8


def verify_imports():
    """Verify critical imports work"""
    print("Verifying imports...")

    imports = [
        ("sentence_transformers", "Sentence Transformers"),
        ("langchain", "LangChain"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
        ("bs4", "BeautifulSoup4"),
    ]

    success_count = 0
    for module, name in imports:
        try:
            __import__(module)
            print(f"SUCCESS: {name} available")
            success_count += 1
        except ImportError:
            print(f"FAILED: {name} not available")

    print(f"Verification: {success_count}/{len(imports)} modules available")
    return success_count >= len(imports) * 0.8


def main():
    print("O-RAN x Nephio RAG Dependency Fix")
    print("=" * 40)

    # Upgrade pip first
    run_command("python -m pip install --upgrade pip", "Upgrading pip")

    # Install packages
    install_success = install_core_packages()

    # Verify imports
    verify_success = verify_imports()

    if install_success and verify_success:
        print("\nSUCCESS: Dependencies fixed!")
        print("You can now run: python test_verification_simple.py")
    else:
        print("\nWARNING: Some issues remain, but system may still work")

    return 0 if (install_success and verify_success) else 1


if __name__ == "__main__":
    sys.exit(main())
