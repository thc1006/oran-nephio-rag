#!/usr/bin/env python3
"""
O-RAN × Nephio RAG 系統依賴安裝腳本
確保所有必要的依賴都能正確安裝
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """執行命令並顯示結果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e.stderr}")
        return False

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本不符合要求: {version.major}.{version.minor}.{version.micro} (需要 3.9+)")
        return False

def install_core_dependencies():
    """安裝核心依賴"""
    print("📦 安裝核心依賴套件...")
    
    # 核心依賴列表 (按順序安裝以避免相依性問題)
    core_packages = [
        "numpy>=1.24.0,<2.0.0",
        "torch",  # sentence-transformers 需要
        "sentence-transformers>=2.2.2,<4.0.0",
        "langchain>=0.1.0,<0.4.0",
        "langchain-community>=0.0.20,<0.4.0",
        "langchain-anthropic>=0.1.0,<0.4.0",
    ]
    
    # 嘗試安裝 langchain-huggingface
    try:
        success = run_command("pip install langchain-huggingface", "安裝 langchain-huggingface")
        if not success:
            print("⚠️ langchain-huggingface 安裝失敗，將使用 langchain-community 作為後援")
    except:
        print("⚠️ langchain-huggingface 不可用，將使用 langchain-community")
    
    # 安裝核心套件
    for package in core_packages:
        success = run_command(f"pip install '{package}'", f"安裝 {package}")
        if not success:
            return False
    
    return True

def install_optional_dependencies():
    """安裝可選依賴"""
    print("📦 安裝可選依賴套件...")
    
    optional_packages = [
        "chromadb>=0.4.0,<0.6.0",
        "requests>=2.28.0,<3.0.0",
        "beautifulsoup4>=4.11.0,<5.0.0",
        "lxml>=4.9.0,<5.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "pydantic>=2.4.0,<3.0.0",
        "aiohttp>=3.8.0,<4.0.0",
    ]
    
    for package in optional_packages:
        success = run_command(f"pip install '{package}'", f"安裝 {package}")
        if not success:
            print(f"⚠️ {package} 安裝失敗，但系統仍可運行")
    
    return True

def install_from_requirements():
    """從 requirements.txt 安裝所有依賴"""
    print("📦 從 requirements.txt 安裝完整依賴...")
    
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        success = run_command(f"pip install -r {req_file}", "安裝 requirements.txt")
        return success
    else:
        print("❌ requirements.txt 檔案不存在")
        return False

def verify_installation():
    """驗證安裝結果"""
    print("🔍 驗證安裝結果...")
    
    test_imports = [
        ("langchain", "LangChain 框架"),
        ("langchain_anthropic", "Anthropic LangChain"),
        ("sentence_transformers", "Sentence Transformers"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
        ("bs4", "BeautifulSoup4"),
        ("dotenv", "Python-dotenv"),
        ("pydantic", "Pydantic"),
        ("aiohttp", "AioHTTP"),
    ]
    
    success_count = 0
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {description} 不可用")
    
    print(f"\n📊 驗證結果: {success_count}/{len(test_imports)} 套件可用")
    return success_count >= len(test_imports) * 0.8  # 80% 以上成功

def main():
    """主函數"""
    print("🚀 O-RAN × Nephio RAG 系統依賴安裝")
    print("=" * 50)
    
    # 檢查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 升級 pip
    print("🔧 升級 pip...")
    run_command("python -m pip install --upgrade pip", "升級 pip")
    
    # 選擇安裝方式
    print("\n選擇安裝方式:")
    print("1. 完整安裝 (推薦) - 從 requirements.txt")
    print("2. 核心安裝 - 只安裝必要套件")
    print("3. 分步安裝 - 先核心再可選")
    
    choice = input("\n請選擇 (1-3，預設 1): ").strip() or "1"
    
    success = False
    
    if choice == "1":
        success = install_from_requirements()
    elif choice == "2":
        success = install_core_dependencies()
    elif choice == "3":
        success = install_core_dependencies()
        if success:
            install_optional_dependencies()
    else:
        print("❌ 無效選擇")
        sys.exit(1)
    
    # 驗證安裝
    verification_success = verify_installation()
    
    if success and verification_success:
        print("\n🎉 依賴安裝完成！")
        print("現在可以運行以下命令測試系統:")
        print("  python test_verification_simple.py")
        print("  python main.py")
    else:
        print("\n⚠️ 安裝過程中遇到一些問題，但系統可能仍可運行")
        print("請檢查上述錯誤訊息並手動安裝缺失的套件")
    
    return 0 if (success and verification_success) else 1

if __name__ == "__main__":
    sys.exit(main())