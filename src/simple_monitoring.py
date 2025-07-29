"""
簡化版監控系統
專注於核心指標收集和健康檢查
"""
import time
import logging
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """系統指標數據類"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApplicationMetrics:
    """應用指標數據類"""
    timestamp: str
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time: float = 0.0
    documents_loaded: int = 0
    vectordb_ready: bool = False
    
    @property
    def success_rate(self) -> float:
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['success_rate'] = self.success_rate
        return data


class SimpleMetricsCollector:
    """簡化版指標收集器"""
    
    def __init__(self):
        self.app_metrics = ApplicationMetrics(timestamp=datetime.now().isoformat())
        self.system_metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0
        )
        self._response_times = []
        self._collection_interval = 30  # 每30秒收集一次系統指標
        self._collection_thread = None
        self._stop_collection = False
        
    def start_collection(self):
        """開始指標收集"""
        if self._collection_thread is not None:
            return
            
        self._stop_collection = False
        self._collection_thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        self._collection_thread.start()
        logger.info("指標收集已開始")
    
    def stop_collection(self):
        """停止指標收集"""
        self._stop_collection = True
        if self._collection_thread:
            self._collection_thread.join(timeout=5)
        logger.info("指標收集已停止")
    
    def _collect_system_metrics(self):
        """在背景執行緒中收集系統指標"""
        while not self._stop_collection:
            try:
                # CPU 使用率
                cpu_usage = psutil.cpu_percent(interval=1)
                
                # 記憶體使用率
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                
                # 磁碟使用率
                disk = psutil.disk_usage('/')
                disk_usage = disk.percent
                
                # 更新系統指標
                self.system_metrics = SystemMetrics(
                    timestamp=datetime.now().isoformat(),
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    disk_usage=disk_usage
                )
                
                # 計算平均回應時間
                if self._response_times:
                    self.app_metrics.average_response_time = sum(self._response_times) / len(self._response_times)
                    # 只保留最近100個回應時間
                    if len(self._response_times) > 100:
                        self._response_times = self._response_times[-100:]
                
                time.sleep(self._collection_interval)
                
            except Exception as e:
                logger.error(f"收集系統指標時發生錯誤: {e}")
                time.sleep(self._collection_interval)
    
    @contextmanager
    def track_query(self, query_type: str = "default"):
        """追蹤查詢執行時間的上下文管理器"""
        start_time = time.time()
        self.app_metrics.total_queries += 1
        
        try:
            yield
            # 查詢成功
            duration = time.time() - start_time
            self.app_metrics.successful_queries += 1
            self._response_times.append(duration)
            
        except Exception as e:
            # 查詢失敗
            self.app_metrics.failed_queries += 1
            logger.error(f"查詢失敗: {e}")
            raise
        finally:
            self.app_metrics.timestamp = datetime.now().isoformat()
    
    def record_documents_loaded(self, count: int):
        """記錄載入的文件數量"""
        self.app_metrics.documents_loaded = count
        self.app_metrics.timestamp = datetime.now().isoformat()
    
    def set_vectordb_status(self, ready: bool):
        """設定向量資料庫狀態"""
        self.app_metrics.vectordb_ready = ready
        self.app_metrics.timestamp = datetime.now().isoformat()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """取得指標摘要"""
        return {
            "system": self.system_metrics.to_dict(),
            "application": self.app_metrics.to_dict(),
            "collection_time": datetime.now().isoformat()
        }


class SimpleHealthChecker:
    """簡化版健康檢查器"""
    
    def __init__(self, metrics_collector: SimpleMetricsCollector):
        self.metrics_collector = metrics_collector
        self.health_thresholds = {
            "cpu_usage_max": 85.0,      # CPU 使用率上限
            "memory_usage_max": 90.0,   # 記憶體使用率上限
            "disk_usage_max": 95.0,     # 磁碟使用率上限
            "success_rate_min": 80.0,   # 成功率下限
        }
    
    def check_health(self) -> Dict[str, Any]:
        """執行健康檢查"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # 系統資源檢查
        system_health = self._check_system_resources()
        health_status["checks"]["system"] = system_health
        
        # 應用狀態檢查
        app_health = self._check_application_status()
        health_status["checks"]["application"] = app_health
        
        # 向量資料庫檢查
        vectordb_health = self._check_vectordb_status()
        health_status["checks"]["vectordb"] = vectordb_health
        
        # 判斷整體健康狀態
        all_checks = [system_health, app_health, vectordb_health]
        if any(check["status"] == "unhealthy" for check in all_checks):
            health_status["status"] = "unhealthy"
        elif any(check["status"] == "degraded" for check in all_checks):
            health_status["status"] = "degraded"
        
        return health_status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """檢查系統資源狀態"""
        system_metrics = self.metrics_collector.system_metrics
        status = "healthy"
        issues = []
        
        # CPU 檢查
        if system_metrics.cpu_usage > self.health_thresholds["cpu_usage_max"]:
            status = "degraded"
            issues.append(f"高 CPU 使用率: {system_metrics.cpu_usage:.1f}%")
        
        # 記憶體檢查
        if system_metrics.memory_usage > self.health_thresholds["memory_usage_max"]:
            status = "unhealthy" if system_metrics.memory_usage > 95 else "degraded"
            issues.append(f"高記憶體使用率: {system_metrics.memory_usage:.1f}%")
        
        # 磁碟檢查
        if system_metrics.disk_usage > self.health_thresholds["disk_usage_max"]:
            status = "unhealthy"
            issues.append(f"磁碟空間不足: {system_metrics.disk_usage:.1f}%")
        
        return {
            "status": status,
            "cpu_usage": system_metrics.cpu_usage,
            "memory_usage": system_metrics.memory_usage,
            "disk_usage": system_metrics.disk_usage,
            "issues": issues
        }
    
    def _check_application_status(self) -> Dict[str, Any]:
        """檢查應用狀態"""
        app_metrics = self.metrics_collector.app_metrics
        status = "healthy"
        issues = []
        
        # 成功率檢查
        if app_metrics.total_queries > 0:
            success_rate = app_metrics.success_rate
            if success_rate < self.health_thresholds["success_rate_min"]:
                status = "degraded"
                issues.append(f"查詢成功率過低: {success_rate:.1f}%")
        
        # 回應時間檢查
        if app_metrics.average_response_time > 10.0:  # 超過10秒
            status = "degraded"
            issues.append(f"平均回應時間過長: {app_metrics.average_response_time:.1f}s")
        
        return {
            "status": status,
            "total_queries": app_metrics.total_queries,
            "success_rate": app_metrics.success_rate,
            "average_response_time": app_metrics.average_response_time,
            "issues": issues
        }
    
    def _check_vectordb_status(self) -> Dict[str, Any]:
        """檢查向量資料庫狀態"""
        app_metrics = self.metrics_collector.app_metrics
        
        if not app_metrics.vectordb_ready:
            return {
                "status": "unhealthy",
                "ready": False,
                "documents_loaded": app_metrics.documents_loaded,
                "issues": ["向量資料庫未就緒"]
            }
        
        return {
            "status": "healthy",
            "ready": True,
            "documents_loaded": app_metrics.documents_loaded,
            "issues": []
        }


class SimpleMonitoring:
    """簡化版監控系統主類"""
    
    def __init__(self):
        self.metrics_collector = SimpleMetricsCollector()
        self.health_checker = SimpleHealthChecker(self.metrics_collector)
        self._initialized = False
    
    def start(self):
        """啟動監控系統"""
        if self._initialized:
            return
        
        self.metrics_collector.start_collection()
        self._initialized = True
        logger.info("簡化版監控系統已啟動")
    
    def stop(self):
        """停止監控系統"""
        if not self._initialized:
            return
        
        self.metrics_collector.stop_collection()
        self._initialized = False
        logger.info("簡化版監控系統已停止")
    
    def get_metrics(self) -> Dict[str, Any]:
        """取得指標資料"""
        return self.metrics_collector.get_metrics_summary()
    
    def get_health(self) -> Dict[str, Any]:
        """取得健康狀態"""
        return self.health_checker.check_health()
    
    def track_query(self, query_type: str = "default"):
        """追蹤查詢的裝飾器"""
        return self.metrics_collector.track_query(query_type)
    
    def record_documents_loaded(self, count: int):
        """記錄載入的文件數量"""
        self.metrics_collector.record_documents_loaded(count)
    
    def set_vectordb_ready(self, ready: bool):
        """設定向量資料庫狀態"""
        self.metrics_collector.set_vectordb_status(ready)
    
    def export_metrics_json(self, filepath: str):
        """將指標匯出為 JSON 檔案"""
        try:
            metrics = self.get_metrics()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            logger.info(f"指標已匯出至: {filepath}")
        except Exception as e:
            logger.error(f"匯出指標失敗: {e}")


# 全域監控實例
_global_monitoring: Optional[SimpleMonitoring] = None


def get_monitoring() -> SimpleMonitoring:
    """取得全域監控實例"""
    global _global_monitoring
    if _global_monitoring is None:
        _global_monitoring = SimpleMonitoring()
    return _global_monitoring


def start_monitoring():
    """啟動全域監控"""
    monitoring = get_monitoring()
    monitoring.start()


def stop_monitoring():
    """停止全域監控"""
    global _global_monitoring
    if _global_monitoring:
        _global_monitoring.stop()


# 裝飾器函數
def monitor_query(query_type: str = "default"):
    """查詢監控裝飾器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitoring = get_monitoring()
            with monitoring.track_query(query_type):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# 使用範例
if __name__ == "__main__":
    # 測試監控系統
    monitoring = SimpleMonitoring()
    monitoring.start()
    
    # 模擬一些查詢
    for i in range(5):
        with monitoring.track_query("test"):
            time.sleep(0.1)  # 模擬查詢時間
    
    # 設定系統狀態
    monitoring.record_documents_loaded(150)
    monitoring.set_vectordb_ready(True)
    
    # 取得指標和健康狀態
    print("=== 指標摘要 ===")
    print(json.dumps(monitoring.get_metrics(), indent=2, ensure_ascii=False))
    
    print("\n=== 健康狀態 ===")
    print(json.dumps(monitoring.get_health(), indent=2, ensure_ascii=False))
    
    monitoring.stop()