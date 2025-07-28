"""
O-RAN × Nephio RAG 系統主程式
"""
import os
import sys
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.oran_nephio_rag import ORANNephioRAG
from src.config import Config

# 設定日誌
def setup_logging():
    """設定日誌系統"""
    config = Config()
    
    # 確保日誌目錄存在
    log_dir = os.path.dirname(config.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

class RAGInterface:
    """RAG 系統的互動式介面"""
    
    def __init__(self):
        self.console = Console()
        self.rag_system = None
        
    def show_welcome(self):
        """顯示歡迎訊息"""
        welcome_text = Text()
        welcome_text.append("O-RAN × Nephio 整合查詢系統", style="bold blue")
        welcome_text.append("\n\n專注於 Network Function Scale-out & Scale-in 實作指導", style="dim")
        
        panel = Panel(
            welcome_text,
            title="🚀 歡迎使用",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def show_commands(self):
        """顯示可用指令"""
        table = Table(title="可用指令", show_header=True, header_style="bold magenta")
        table.add_column("指令", style="cyan", no_wrap=True)
        table.add_column("說明", style="green")
        
        table.add_row("quit / exit / 退出", "結束程式")
        table.add_row("update", "更新向量資料庫")
        table.add_row("status", "顯示系統狀態")
        table.add_row("help", "顯示此說明")
        table.add_row("clear", "清除螢幕")
        
        self.console.print(table)
    
    def show_status(self):
        """顯示系統狀態"""
        if not self.rag_system:
            self.console.print("❌ 系統尚未初始化", style="red")
            return
        
        status = self.rag_system.get_system_status()
        
        table = Table(title="系統狀態", show_header=True, header_style="bold cyan")
        table.add_column("項目", style="white")
        table.add_column("狀態", style="green")
        
        table.add_row("向量資料庫", "✅ 就緒" if status["vectordb_ready"] else "❌ 未就緒")
        table.add_row("問答鏈", "✅ 就緒" if status["qa_chain_ready"] else "❌ 未就緒")
        table.add_row("文件來源數量", str(status["source_count"]))
        table.add_row("啟用來源數量", str(status["enabled_sources"]))
        table.add_row("最後更新", status["last_update"] or "未知")
        
        self.console.print(table)
    
    def initialize_system(self):
        """初始化 RAG 系統"""
        try:
            self.console.print("🔄 正在初始化系統...", style="yellow")
            
            # 初始化 RAG 系統
            self.rag_system = ORANNephioRAG()
            
            # 載入向量資料庫
            if not self.rag_system.load_existing_database():
                self.console.print("❌ 向量資料庫載入失敗", style="red")
                return False
            
            # 設定問答鏈
            if not self.rag_system.setup_qa_chain():
                self.console.print("❌ 問答鏈設定失敗", style="red")
                return False
            
            self.console.print("✅ 系統初始化完成！", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ 系統初始化失敗: {str(e)}", style="red")
            return False
    
    def process_query(self, question: str):
        """處理用戶查詢"""
        self.console.print("🤔 正在思考中...", style="yellow")
        
        result = self.rag_system.query(question)
        
        # 顯示答案
        answer_panel = Panel(
            result["answer"],
            title="💡 回答",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(answer_panel)
        
        # 顯示來源
        if result.get("sources"):
            self.console.print("\n📚 參考來源:", style="bold blue")
            for i, source in enumerate(result["sources"], 1):
                source_text = f"{i}. [{source['type'].upper()}] {source['description']}"
                self.console.print(f"   {source_text}", style="dim")
                self.console.print(f"   🔗 {source['url']}", style="blue")
    
    def run(self):
        """執行主循環"""
        self.show_welcome()
        
        # 初始化系統
        if not self.initialize_system():
            self.console.print("初始化失敗，程式結束。", style="red")
            return
        
        self.show_commands()
        self.console.print("\n" + "="*50 + "\n")
        
        while True:
            try:
                # 獲取用戶輸入
                question = Prompt.ask(
                    "\n[bold cyan]請輸入您的問題[/bold cyan]",
                    default=""
                ).strip()
                
                if not question:
                    continue
                
                # 處理指令
                if question.lower() in ['quit', 'exit', '退出']:
                    self.console.print("👋 再見！", style="yellow")
                    break
                
                elif question.lower() == 'help':
                    self.show_commands()
                    continue
                
                elif question.lower() == 'status':
                    self.show_status()
                    continue
                
                elif question.lower() == 'update':
                    self.console.print("🔄 正在更新資料庫...", style="yellow")
                    if self.rag_system.update_database():
                        self.console.print("✅ 資料庫更新成功！", style="green")
                    else:
                        self.console.print("❌ 資料庫更新失敗", style="red")
                    continue
                
                elif question.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_welcome()
                    continue
                
                # 處理問題查詢
                self.process_query(question)
                
                self.console.print("\n" + "-"*50)
                
            except KeyboardInterrupt:
                self.console.print("\n\n👋 程式被使用者中斷，再見！", style="yellow")
                break
            
            except Exception as e:
                self.console.print(f"\n❌ 發生錯誤: {str(e)}", style="red")
                logging.error(f"主程式錯誤: {str(e)}", exc_info=True)

def main():
    """主函數"""
    try:
        # 設定日誌
        setup_logging()
        
        # 執行介面
        interface = RAGInterface()
        interface.run()
        
    except Exception as e:
        print(f"程式啟動失敗: {str(e)}")
        logging.error(f"程式啟動失敗: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
