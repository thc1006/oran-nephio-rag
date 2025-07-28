"""
使用範例
"""
import sys
import os

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.oran_nephio_rag import ORANNephioRAG

def main():
    """範例使用"""
    print("初始化 RAG 系統...")
    
    # 初始化系統
    rag = ORANNephioRAG()
    rag.load_existing_database()
    rag.setup_qa_chain()
    
    # 範例問題
    questions = [
        "什麼是 Nephio？它的主要功能是什麼？",
        "如何在 Nephio 上實現 O-RAN DU 的 scale-out？",
        "O2IMS 介面在 O-RAN NF 擴縮中扮演什麼角色？",
        "FOCOM 和 SMO 如何協作進行 NF 的自動擴縮？", 
        "Nephio 的 ProvisioningRequest CRD 如何支援 scale-in 操作？",
        "O-RAN 架構中的主要組件有哪些？"
    ]
    
    print("\n開始測試查詢...")
    
    for i, question in enumerate(questions, 1):
        print(f"\n問題 {i}: {question}")
        print("-" * 60)
        
        result = rag.query(question)
        
        print(f"回答: {result['answer'][:300]}...")
        print(f"來源數量: {len(result['sources'])}")
        
        if result['sources']:
            print("主要來源:")
            for source in result['sources'][:2]:  # 只顯示前兩個來源
                print(f"  - {source['description']}")
        
        print("=" * 60)

if __name__ == "__main__":
    main()
