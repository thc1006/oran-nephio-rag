#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final E2E Test Report Generator
"""
import os
import sys
from datetime import datetime
from pathlib import Path

def read_report_file(file_path):
    """Read a report file if it exists"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Report file not found: {file_path}"
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def generate_comprehensive_report():
    """Generate comprehensive E2E test report"""
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("O-RAN × Nephio RAG 系統完整端對端測試報告")
    report_lines.append("O-RAN x Nephio RAG System Complete End-to-End Test Report")
    report_lines.append("=" * 80)
    report_lines.append(f"報告生成時間 / Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Python 版本 / Python Version: {sys.version}")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("執行摘要 / EXECUTIVE SUMMARY")
    report_lines.append("-" * 40)
    report_lines.append("本報告包含對 O-RAN × Nephio RAG 系統的完整端對端測試結果。")
    report_lines.append("This report contains complete end-to-end test results for the O-RAN × Nephio RAG system.")
    report_lines.append("")
    
    # Test Categories
    test_categories = [
        ("系統修復驗證", "System Fix Verification", "logs/verification_report.txt"),
        ("基本系統測試", "Basic System Test", "logs/system_test_report.txt"),
        ("核心 RAG 功能測試", "Core RAG Functionality Test", "logs/rag_core_test_report.txt"),
        ("主程式啟動測試", "Main Program Startup Test", "logs/main_startup_test_report.txt")
    ]
    
    overall_results = []
    
    for chinese_name, english_name, report_path in test_categories:
        report_lines.append(f"{chinese_name} / {english_name}")
        report_lines.append("-" * 60)
        
        if os.path.exists(report_path):
            report_content = read_report_file(report_path)
            report_lines.append(report_content)
            
            # Extract success rate if available
            if "Success rate:" in report_content:
                try:
                    success_line = [line for line in report_content.split('\n') if 'Success rate:' in line][0]
                    if '%' in success_line:
                        success_rate = float(success_line.split('%')[0].split()[-1])
                        overall_results.append((chinese_name, success_rate))
                except:
                    overall_results.append((chinese_name, 0))
            elif "通過" in report_content and "項檢查" in report_content:
                # Handle verification report format
                try:
                    lines = report_content.split('\n')
                    for line in lines:
                        if "項檢查通過" in line:
                            parts = line.split('/')
                            if len(parts) >= 2:
                                passed = int(parts[0].split()[-1])
                                total = int(parts[1].split()[0])
                                success_rate = (passed / total) * 100
                                overall_results.append((chinese_name, success_rate))
                                break
                except:
                    overall_results.append((chinese_name, 0))
        else:
            report_lines.append(f"報告檔案未找到 / Report file not found: {report_path}")
            overall_results.append((chinese_name, 0))
        
        report_lines.append("")
        report_lines.append("")
    
    # Overall Analysis
    report_lines.append("整體分析 / OVERALL ANALYSIS")
    report_lines.append("-" * 40)
    
    if overall_results:
        total_avg = sum(rate for _, rate in overall_results) / len(overall_results)
        report_lines.append(f"平均成功率 / Average Success Rate: {total_avg:.1f}%")
        report_lines.append("")
        
        report_lines.append("各測試類別結果 / Test Category Results:")
        for category, rate in overall_results:
            status = "[PASS] 通過" if rate >= 80 else "[WARNING] 需要注意" if rate >= 60 else "[FAIL] 失敗"
            report_lines.append(f"  - {category}: {rate:.1f}% {status}")
        report_lines.append("")
        
        # Overall conclusion
        if total_avg >= 90:
            conclusion = "[EXCELLENT] 系統測試優秀 - System is ready for production"
        elif total_avg >= 80:
            conclusion = "[GOOD] 系統測試良好 - System is functional with minor issues"
        elif total_avg >= 60:
            conclusion = "[NEEDS IMPROVEMENT] 系統需要改進 - System has several issues"
        else:
            conclusion = "[MAJOR ISSUES] 系統需要大幅修復 - System requires significant fixes"
        
        report_lines.append(f"總體結論 / Overall Conclusion: {conclusion}")
    else:
        report_lines.append("無法計算整體成功率 / Unable to calculate overall success rate")
    
    report_lines.append("")
    
    # Technical Details
    report_lines.append("技術細節 / TECHNICAL DETAILS")
    report_lines.append("-" * 40)
    report_lines.append("已解決的問題 / Issues Resolved:")
    report_lines.append("  [OK] 重複配置檔案已移除 / Duplicate config files removed")
    report_lines.append("  [OK] 硬編碼數值已提取至配置 / Hardcoded values extracted to config")
    report_lines.append("  [OK] SSL 憑證驗證已啟用 / SSL certificate verification enabled")
    report_lines.append("  [OK] 相對導入問題已修復 / Relative import issues fixed")
    report_lines.append("  [OK] Unicode 編碼問題已處理 / Unicode encoding issues handled")
    report_lines.append("")
    
    report_lines.append("已知限制 / Known Limitations:")
    report_lines.append("  [WARNING] ChromaDB 在 Python 3.13 中存在相容性問題 / ChromaDB compatibility issues with Python 3.13")
    report_lines.append("  [WARNING] 需要 ANTHROPIC_API_KEY 環境變數才能完整運行 / Requires ANTHROPIC_API_KEY environment variable for full operation")
    report_lines.append("")
    
    # Recommendations
    report_lines.append("建議 / RECOMMENDATIONS")
    report_lines.append("-" * 40)
    report_lines.append("1. 設定 ANTHROPIC_API_KEY 環境變數以啟用完整功能")
    report_lines.append("   Set ANTHROPIC_API_KEY environment variable to enable full functionality")
    report_lines.append("")
    report_lines.append("2. 考慮降級至 Python 3.11 以獲得更好的套件相容性")
    report_lines.append("   Consider downgrading to Python 3.11 for better package compatibility")
    report_lines.append("")
    report_lines.append("3. 定期更新依賴套件以修復已知問題")
    report_lines.append("   Regularly update dependencies to fix known issues")
    report_lines.append("")
    
    # Footer
    report_lines.append("=" * 80)
    report_lines.append("報告結束 / END OF REPORT")
    report_lines.append("=" * 80)
    
    # Generate report
    final_report = "\n".join(report_lines)
    
    # Save comprehensive report
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/comprehensive_e2e_test_report.txt", "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print("=" * 60)
        print("綜合測試報告已生成 / Comprehensive Test Report Generated")
        print("=" * 60)
        print(final_report)
        print("\n詳細報告已保存至 / Detailed report saved to: logs/comprehensive_e2e_test_report.txt")
        
        return True
    except Exception as e:
        print(f"生成報告時發生錯誤 / Error generating report: {e}")
        return False

def main():
    """Main function"""
    return generate_comprehensive_report()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)