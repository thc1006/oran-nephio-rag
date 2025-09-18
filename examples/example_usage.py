"""
O-RAN × Nephio RAG 系統使用範例

本檔案展示如何使用 RAG 系統的各種功能
"""

import os
import sys
from datetime import datetime

# 添加父目錄到路徑以導入 src 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import Config
    from src.document_loader import DocumentLoader
    from src.oran_nephio_rag import ORANNephioRAG, create_rag_system, quick_query
except ImportError as e:
    print(f"❌ 模組導入失敗: {e}")
    print("請確保已安裝所有依賴套件：pip install -r requirements.txt")
    sys.exit(1)


def example_1_basic_usage():
    """範例 1: 基本使用方式"""
    print("=" * 60)
    print("範例 1: 基本使用方式")
    print("=" * 60)

    try:
        # 建立 RAG 系統實例
        print("🚀 初始化 RAG 系統...")
        rag = ORANNephioRAG()

        # 載入向量資料庫
        print("📚 載入向量資料庫...")
        if not rag.load_existing_database():
            print("❌ 向量資料庫載入失敗")
            return

        # 設定問答鏈
        print("🔗 設定問答鏈...")
        if not rag.setup_qa_chain():
            print("❌ 問答鏈設定失敗")
            return

        # 執行查詢
        question = "什麼是 Nephio？它的主要功能是什麼？"
        print(f"\n❓ 問題: {question}")
        print("🤔 正在思考中...")

        result = rag.query(question)

        print(f"\n💡 回答: {result['answer'][:200]}...")
        print(f"📚 參考來源數量: {len(result.get('sources', []))}")

        if result.get("sources"):
            print("主要來源:")
            for i, source in enumerate(result["sources"][:2], 1):
                print(f"  {i}. {source['description']}")

        print("✅ 範例 1 完成")

    except Exception as e:
        print(f"❌ 範例 1 執行失敗: {e}")


def example_2_quick_query():
    """範例 2: 快速查詢功能"""
    print("\n" + "=" * 60)
    print("範例 2: 快速查詢功能")
    print("=" * 60)

    try:
        question = "如何在 Nephio 上實現 O-RAN DU 的 scale-out？"
        print(f"❓ 問題: {question}")
        print("🤔 正在思考中...")

        # 使用快速查詢函數
        answer = quick_query(question)

        print(f"\n💡 回答: {answer[:300]}...")
        print("✅ 範例 2 完成")

    except Exception as e:
        print(f"❌ 範例 2 執行失敗: {e}")


def example_3_batch_queries():
    """範例 3: 批次查詢處理"""
    print("\n" + "=" * 60)
    print("範例 3: 批次查詢處理")
    print("=" * 60)

    try:
        # 初始化系統
        rag = create_rag_system()
        rag.load_existing_database()
        rag.setup_qa_chain()

        # 定義一批問題
        questions = [
            "什麼是 O2IMS 介面？",
            "FOCOM 的作用是什麼？",
            "ProvisioningRequest CRD 如何使用？",
            "Nephio 如何支援 GitOps？",
        ]

        print(f"📝 處理 {len(questions)} 個問題...")

        for i, question in enumerate(questions, 1):
            print(f"\n{i}. 問題: {question}")

            start_time = datetime.now()
            result = rag.query(question, include_citations=False)
            end_time = datetime.now()

            query_time = (end_time - start_time).total_seconds()

            print(f"   答案: {result['answer'][:100]}...")
            print(f"   耗時: {query_time:.2f} 秒")
            print(f"   來源: {len(result.get('sources', []))} 個")

        print("✅ 範例 3 完成")

    except Exception as e:
        print(f"❌ 範例 3 執行失敗: {e}")


def example_4_system_status():
    """範例 4: 系統狀態檢查"""
    print("\n" + "=" * 60)
    print("範例 4: 系統狀態檢查")
    print("=" * 60)

    try:
        # 初始化系統
        rag = ORANNephioRAG()
        rag.load_existing_database()
        rag.setup_qa_chain()

        # 取得系統狀態
        status = rag.get_system_status()

        print("📊 系統狀態:")
        print(f"  向量資料庫: {'✅ 就緒' if status['vectordb_ready'] else '❌ 未就緒'}")
        print(f"  問答鏈: {'✅ 就緒' if status['qa_chain_ready'] else '❌ 未就緒'}")
        print(f"  文件來源總數: {status['total_sources']}")
        print(f"  啟用來源數: {status['enabled_sources']}")
        print(f"  最後更新: {status.get('last_update', '未知')}")

        # 向量資料庫資訊
        vectordb_info = status.get("vectordb_info", {})
        if vectordb_info and not vectordb_info.get("error"):
            print(f"  文件塊數量: {vectordb_info.get('document_count', 0)}")

        # 載入統計
        load_stats = status.get("load_statistics", {})
        if load_stats:
            print(f"  載入成功率: {load_stats.get('success_rate', 0)}%")

        print("✅ 範例 4 完成")

    except Exception as e:
        print(f"❌ 範例 4 執行失敗: {e}")


def example_5_similarity_search():
    """範例 5: 相似文件搜尋"""
    print("\n" + "=" * 60)
    print("範例 5: 相似文件搜尋")
    print("=" * 60)

    try:
        # 初始化系統
        rag = ORANNephioRAG()
        rag.load_existing_database()

        # 執行相似性搜尋
        query = "network function scaling"
        print(f"🔍 搜尋關鍵字: {query}")

        similar_docs = rag.search_similar_documents(query, k=3)

        print(f"📄 找到 {len(similar_docs)} 個相似文件:")

        for i, doc in enumerate(similar_docs, 1):
            print(f"\n{i}. 相似度分數: {doc['score']:.3f}")
            print(f"   內容預覽: {doc['content'][:150]}...")

            metadata = doc.get("metadata", {})
            if metadata:
                print(f"   來源: {metadata.get('description', '未知')}")
                print(f"   類型: {metadata.get('source_type', '未知')}")

        print("✅ 範例 5 完成")

    except Exception as e:
        print(f"❌ 範例 5 執行失敗: {e}")


def example_6_config_usage():
    """範例 6: 配置系統使用"""
    print("\n" + "=" * 60)
    print("範例 6: 配置系統使用")
    print("=" * 60)

    try:
        # 取得配置摘要
        config = Config()
        summary = config.get_config_summary()

        print("⚙️ 配置摘要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # 顯示啟用的文件來源
        enabled_sources = config.get_enabled_sources()
        print(f"\n📚 啟用的文件來源 ({len(enabled_sources)} 個):")

        for i, source in enumerate(enabled_sources, 1):
            print(f"  {i}. [{source.source_type.upper()}] {source.description}")
            print(f"     優先級: {source.priority}")
            print(f"     URL: {source.url}")

        # 按類型分組顯示
        nephio_sources = config.get_sources_by_type("nephio")
        oran_sc_sources = config.get_sources_by_type("oran_sc")

        print("\n📊 來源統計:")
        print(f"  Nephio 來源: {len(nephio_sources)} 個")
        print(f"  O-RAN SC 來源: {len(oran_sc_sources)} 個")

        print("✅ 範例 6 完成")

    except Exception as e:
        print(f"❌ 範例 6 執行失敗: {e}")


def example_7_document_loader():
    """範例 7: 文件載入器使用"""
    print("\n" + "=" * 60)
    print("範例 7: 文件載入器使用")
    print("=" * 60)

    try:
        # 建立文件載入器
        loader = DocumentLoader()

        # 取得啟用的文件來源
        config = Config()
        sources = config.get_enabled_sources()[:2]  # 只載入前兩個來源作為示範

        print(f"📥 載入 {len(sources)} 個文件來源...")

        # 載入文件
        documents = []
        for source in sources:
            print(f"正在載入: {source.description}")
            doc = loader.load_document(source)
            if doc:
                documents.append(doc)
                print(f"  ✅ 成功，內容長度: {len(doc.page_content)} 字元")
            else:
                print("  ❌ 失敗")

        # 顯示載入統計
        stats = loader.get_load_statistics()
        print("\n📊 載入統計:")
        print(f"  總嘗試次數: {stats['total_attempts']}")
        print(f"  成功載入: {stats['successful_loads']}")
        print(f"  失敗載入: {stats['failed_loads']}")
        print(f"  重試次數: {stats['retry_attempts']}")
        print(f"  成功率: {stats['success_rate']}%")

        print("✅ 範例 7 完成")

    except Exception as e:
        print(f"❌ 範例 7 執行失敗: {e}")


def main():
    """主函數 - 執行所有範例"""
    print("🎯 O-RAN × Nephio RAG 系統使用範例")
    print("本程式將示範系統的各種功能和使用方式")
    print()

    try:
        # 執行所有範例
        example_1_basic_usage()
        example_2_quick_query()
        example_3_batch_queries()
        example_4_system_status()
        example_5_similarity_search()
        example_6_config_usage()
        example_7_document_loader()

        print("\n" + "=" * 60)
        print("🎉 所有範例執行完成！")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n👋 範例程式被使用者中斷")
    except Exception as e:
        print(f"\n❌ 範例程式執行失敗: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
