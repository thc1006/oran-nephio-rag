"""
簡單的 RAG 系統結構驗證（不依賴外部套件）
"""
import sys
import os
import ast
import inspect

def test_file_structure():
    """測試檔案結構"""
    print("🧪 測試檔案結構...")
    
    required_files = [
        "src/oran_nephio_rag.py",
        "src/document_loader.py", 
        "src/config.py",
        "main.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} 存在")
    
    if missing_files:
        print(f"❌ 缺少檔案: {missing_files}")
        return False
    
    return True

def test_file_syntax():
    """測試檔案語法"""
    print("\n🧪 測試檔案語法...")
    
    python_files = [
        "src/oran_nephio_rag.py",
        "src/document_loader.py",
        "src/config.py", 
        "main.py"
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"❌ {file_path} 是空檔案")
                return False
            
            # 嘗試解析 AST
            ast.parse(content)
            print(f"✅ {file_path} 語法正確")
            
        except SyntaxError as e:
            print(f"❌ {file_path} 語法錯誤: {e}")
            return False
        except Exception as e:
            print(f"❌ {file_path} 讀取失敗: {e}")
            return False
    
    return True

def test_class_definitions():
    """測試類別定義"""
    print("\n🧪 測試類別定義...")
    
    try:
        # 讀取檔案內容
        with open("src/oran_nephio_rag.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查類別定義
        required_classes = [
            "VectorDatabaseManager",
            "QueryProcessor", 
            "ORANNephioRAG"
        ]
        
        for class_name in required_classes:
            if f"class {class_name}" in content:
                print(f"✅ {class_name} 類別已定義")
            else:
                print(f"❌ {class_name} 類別未找到")
                return False
        
        # 檢查函數定義
        required_functions = [
            "create_rag_system",
            "quick_query"
        ]
        
        for func_name in required_functions:
            if f"def {func_name}" in content:
                print(f"✅ {func_name} 函數已定義")
            else:
                print(f"❌ {func_name} 函數未找到")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查類別定義失敗: {e}")
        return False

def test_import_structure():
    """測試導入結構"""
    print("\n🧪 測試導入結構...")
    
    try:
        with open("src/oran_nephio_rag.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查關鍵導入
        required_imports = [
            "from .config import Config",
            "from .document_loader import DocumentLoader"
        ]
        
        for import_stmt in required_imports:
            if import_stmt in content:
                print(f"✅ 找到導入: {import_stmt}")
            else:
                print(f"❌ 缺少導入: {import_stmt}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查導入結構失敗: {e}")
        return False

def test_requirements_fix():
    """測試 requirements.txt 修復"""
    print("\n🧪 測試 requirements.txt 修復...")
    
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查錯誤的依賴是否已移除
        problematic_deps = ["asyncio==3.4.3", "threading2==0.1.1"]
        
        for dep in problematic_deps:
            if dep in content:
                print(f"❌ 仍然包含問題依賴: {dep}")
                return False
            else:
                print(f"✅ 已移除問題依賴: {dep}")
        
        # 檢查必要依賴是否存在
        required_deps = ["langchain", "chromadb", "sentence-transformers"]
        
        for dep in required_deps:
            if dep in content:
                print(f"✅ 包含必要依賴: {dep}")
            else:
                print(f"❌ 缺少必要依賴: {dep}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查 requirements.txt 失敗: {e}")
        return False

def test_file_differences():
    """測試檔案差異"""
    print("\n🧪 測試檔案差異...")
    
    try:
        # 讀取兩個檔案
        with open("src/oran_nephio_rag.py", 'r', encoding='utf-8') as f:
            rag_content = f.read()
        
        with open("src/document_loader.py", 'r', encoding='utf-8') as f:
            loader_content = f.read()
        
        # 檢查檔案是否相同
        if rag_content == loader_content:
            print("❌ oran_nephio_rag.py 和 document_loader.py 內容相同")
            return False
        else:
            print("✅ oran_nephio_rag.py 和 document_loader.py 內容不同")
        
        # 檢查 RAG 檔案是否包含特定內容
        if "class ORANNephioRAG" in rag_content:
            print("✅ oran_nephio_rag.py 包含 ORANNephioRAG 類別")
        else:
            print("❌ oran_nephio_rag.py 缺少 ORANNephioRAG 類別")
            return False
        
        # 檢查文件載入器檔案是否包含正確內容
        if "class DocumentLoader" in loader_content:
            print("✅ document_loader.py 包含 DocumentLoader 類別")
        else:
            print("❌ document_loader.py 缺少 DocumentLoader 類別")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查檔案差異失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🔧 RAG 系統結構驗證測試")
    print("=" * 50)
    
    tests = [
        ("檔案結構", test_file_structure),
        ("檔案語法", test_file_syntax),
        ("類別定義", test_class_definitions),
        ("導入結構", test_import_structure),
        ("requirements.txt 修復", test_requirements_fix),
        ("檔案差異", test_file_differences)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 測試發生異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有結構測試通過！主要問題已修復！")
        print("\n📝 下一步:")
        print("1. 安裝依賴套件: pip install -r requirements.txt")
        print("2. 設定環境變數: 複製 .env.example 為 .env 並設定 ANTHROPIC_API_KEY")
        print("3. 執行系統測試: python scripts/test_system.py")
    elif passed >= total * 0.8:
        print("⚠️  大部分測試通過，但還有一些小問題需要修復")
        return 1
    else:
        print("❌ 多數測試失敗，需要進一步檢查")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
