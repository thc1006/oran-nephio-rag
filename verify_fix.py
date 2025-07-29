#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復驗證工具
用於驗證 O-RAN × Nephio RAG 系統的修復狀態
"""
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any

# 確保可以導入 src 模組
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """設定日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def verify_file_structure() -> Tuple[bool, List[str]]:
    """驗證檔案結構完整性"""
    required_files = [
        "src/oran_nephio_rag.py",
        "src/document_loader.py", 
        "src/config.py",
        "main.py",
        "requirements.txt",
        "README.md",
        "LICENSE"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def verify_config_consistency() -> Tuple[bool, List[str]]:
    """驗證配置一致性"""
    issues = []
    
    # 檢查是否存在重複的配置檔案
    duplicate_config = "config.py"  # 根目錄的配置檔案
    if os.path.exists(duplicate_config):
        issues.append("發現重複的配置檔案：config.py")
    
    # 檢查環境變數範例檔案
    if not os.path.exists(".env.example"):
        issues.append("缺少環境變數範例檔案：.env.example")
    
    return len(issues) == 0, issues

def verify_module_imports() -> Tuple[bool, List[str]]:
    """驗證模組導入功能"""
    import_errors = []
    
    try:
        from src.config import Config, DocumentSource, validate_config
        logging.info("config 模組導入成功")
    except ImportError as e:
        import_errors.append(f"config 模組導入失敗: {e}")
    
    try:
        from src.document_loader import DocumentLoader, create_document_loader
        logging.info("document_loader 模組導入成功")
    except ImportError as e:
        import_errors.append(f"document_loader 模組導入失敗: {e}")
    
    try:
        from src.oran_nephio_rag import ORANNephioRAG, create_rag_system, quick_query
        logging.info("oran_nephio_rag 模組導入成功")
    except ImportError as e:
        import_errors.append(f"oran_nephio_rag 模組導入失敗: {e}")
    
    return len(import_errors) == 0, import_errors

def verify_code_quality() -> Tuple[bool, List[str]]:
    """驗證程式碼品質"""
    quality_issues = []
    
    # 檢查是否有空檔案
    empty_files = []
    python_files = [
        "src/oran_nephio_rag.py",
        "src/document_loader.py", 
        "src/config.py",
        "main.py"
    ]
    
    for file_path in python_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if len(content) < 100:  # 檔案內容太少
                    empty_files.append(file_path)
    
    if empty_files:
        quality_issues.append(f"發現內容過少的檔案: {empty_files}")
    
    return len(quality_issues) == 0, quality_issues

def verify_dependencies() -> Tuple[bool, List[str]]:
    """驗證依賴套件"""
    dependency_issues = []
    
    # 檢查 requirements.txt
    if not os.path.exists("requirements.txt"):
        dependency_issues.append("缺少 requirements.txt 檔案")
        return False, dependency_issues
    
    with open("requirements.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否包含錯誤的依賴
    problematic_deps = ["asyncio==3.4.3", "threading2==0.1.1"]
    for dep in problematic_deps:
        if dep in content:
            dependency_issues.append(f"包含問題依賴: {dep}")
    
    # 檢查必要依賴
    required_deps = ["langchain", "chromadb", "sentence-transformers", "requests", "beautifulsoup4"]
    for dep in required_deps:
        if dep not in content:
            dependency_issues.append(f"缺少必要依賴: {dep}")
    
    return len(dependency_issues) == 0, dependency_issues

def verify_security_settings() -> Tuple[bool, List[str]]:
    """驗證安全性設定"""
    security_issues = []
    
    # 檢查 .gitignore
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        if ".env" not in gitignore_content:
            security_issues.append(".gitignore 未排除 .env 檔案")
        
        if "*.log" not in gitignore_content:
            security_issues.append(".gitignore 未排除日誌檔案")
    else:
        security_issues.append("缺少 .gitignore 檔案")
    
    # 檢查是否意外提交了 .env 檔案
    if os.path.exists(".env"):
        security_issues.append("警告：發現 .env 檔案，請確保未提交到版本控制")
    
    return len(security_issues) == 0, security_issues

def generate_verification_report(results: Dict[str, Tuple[bool, List[str]]]) -> str:
    """生成驗證報告"""
    report = []
    report.append("=" * 70)
    report.append("O-RAN × Nephio RAG 系統修復驗證報告")
    report.append("=" * 70)
    report.append(f"驗證時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    total_checks = len(results)
    passed_checks = sum(1 for success, _ in results.values() if success)
    
    for check_name, (success, issues) in results.items():
        status = "通過" if success else "失敗"
        report.append(f"{check_name}: {status}")
        
        if not success and issues:
            for issue in issues:
                report.append(f"  - {issue}")
        report.append("")
    
    report.append(f"總體結果: {passed_checks}/{total_checks} 項檢查通過")
    
    if passed_checks == total_checks:
        report.append("所有檢查都通過！系統修復成功！")
    elif passed_checks >= total_checks * 0.8:
        report.append("大部分檢查通過，但仍有少數問題需要解決")
    else:
        report.append("多數檢查失敗，需要進一步修復")
    
    report.append("=" * 70)
    return "\n".join(report)

def main():
    """主函數"""
    setup_logging()
    
    print("開始驗證 O-RAN × Nephio RAG 系統修復狀態...")
    print("-" * 60)
    
    # 執行各項驗證
    verification_results = {}
    
    try:
        # 檔案結構驗證
        success, issues = verify_file_structure()
        verification_results["檔案結構完整性"] = (success, issues)
        
        # 配置一致性驗證
        success, issues = verify_config_consistency()
        verification_results["配置一致性"] = (success, issues)
        
        # 模組導入驗證
        success, issues = verify_module_imports()
        verification_results["模組導入功能"] = (success, issues)
        
        # 程式碼品質驗證
        success, issues = verify_code_quality()
        verification_results["程式碼品質"] = (success, issues)
        
        # 依賴套件驗證
        success, issues = verify_dependencies()
        verification_results["依賴套件"] = (success, issues)
        
        # 安全性設定驗證
        success, issues = verify_security_settings()
        verification_results["安全性設定"] = (success, issues)
        
        # 生成報告
        report = generate_verification_report(verification_results)
        print(report)
        
        # 儲存報告
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/verification_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n詳細驗證報告已儲存至: logs/verification_report.txt")
        except Exception as e:
            print(f"\n無法儲存驗證報告: {e}")
        
        # 決定退出碼
        total_checks = len(verification_results)
        passed_checks = sum(1 for success, _ in verification_results.values() if success)
        success_rate = passed_checks / total_checks
        
        if success_rate >= 0.9:
            print("\n修復驗證完成：系統狀態優秀")
            return 0
        elif success_rate >= 0.7:
            print("\n修復驗證完成：系統狀態良好，有少數問題")
            return 1
        else:
            print("\n修復驗證失敗：系統仍有較多問題")
            return 2
            
    except Exception as e:
        print(f"\n驗證過程中發生錯誤: {e}")
        logging.error(f"驗證失敗: {e}", exc_info=True)
        return 3

if __name__ == "__main__":
    sys.exit(main())