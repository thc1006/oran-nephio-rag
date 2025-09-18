"""
Performance Monitoring System for O-RAN × Nephio RAG
Comprehensive monitoring, metrics collection, and performance analysis
"""

import logging
import time
import json
import os
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
import threading
from collections import defaultdict, deque
import psutil
import asyncio

# Import configuration
try:
    from .config import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: str
    component: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SystemHealth:
    """System health snapshot"""
    timestamp: str
    overall_score: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    rag_components_health: Dict[str, float]
    active_queries: int
    error_rate: float


class MetricsCollector:
    """Collects and stores performance metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: deque = deque(maxlen=max_metrics)
        self.aggregated_metrics: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, unit: str, 
                     component: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            component=component,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
            self.aggregated_metrics[f"{component}.{name}"].append(value)
            
            # Keep only recent aggregated metrics
            if len(self.aggregated_metrics[f"{component}.{name}"]) > 1000:
                self.aggregated_metrics[f"{component}.{name}"] = \
                    self.aggregated_metrics[f"{component}.{name}"][-500:]
    
    def get_metrics(self, component: Optional[str] = None, 
                   metric_name: Optional[str] = None,
                   since: Optional[datetime] = None) -> List[PerformanceMetric]:
        """Get metrics with optional filtering"""
        with self.lock:
            filtered_metrics = list(self.metrics)
        
        if component:
            filtered_metrics = [m for m in filtered_metrics if m.component == component]
        
        if metric_name:
            filtered_metrics = [m for m in filtered_metrics if m.name == metric_name]
        
        if since:
            since_str = since.isoformat()
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since_str]
        
        return filtered_metrics
    
    def get_aggregated_stats(self, metric_key: str) -> Dict[str, float]:
        """Get aggregated statistics for a metric"""
        with self.lock:
            values = self.aggregated_metrics.get(metric_key, [])
        
        if not values:
            return {'count': 0, 'avg': 0, 'min': 0, 'max': 0, 'p95': 0, 'p99': 0}
        
        sorted_values = sorted(values)
        count = len(values)
        
        return {
            'count': count,
            'avg': sum(values) / count,
            'min': min(values),
            'max': max(values),
            'p95': sorted_values[int(count * 0.95)] if count > 0 else 0,
            'p99': sorted_values[int(count * 0.99)] if count > 0 else 0
        }


class SystemMonitor:
    """Monitors system resources and health"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.health_history: deque = deque(maxlen=100)
    
    def start_monitoring(self, interval: float = 5.0) -> None:
        """Start system monitoring in background thread"""
        if self.monitoring_active:
            logger.warning("System monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"System monitoring started with {interval}s interval")
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: float) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> None:
        """Collect system resource metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.metrics_collector.record_metric(
            'cpu_usage', cpu_percent, 'percent', 'system'
        )
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics_collector.record_metric(
            'memory_usage', memory.percent, 'percent', 'system'
        )
        self.metrics_collector.record_metric(
            'memory_available', memory.available / (1024**3), 'GB', 'system'
        )
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.metrics_collector.record_metric(
            'disk_usage', (disk.used / disk.total) * 100, 'percent', 'system'
        )
        
        # Process metrics for current process
        process = psutil.Process()
        self.metrics_collector.record_metric(
            'process_memory', process.memory_info().rss / (1024**2), 'MB', 'process'
        )
        self.metrics_collector.record_metric(
            'process_cpu', process.cpu_percent(), 'percent', 'process'
        )
        
        # Calculate and store health score
        health_score = self._calculate_health_score(cpu_percent, memory.percent, 
                                                  (disk.used / disk.total) * 100)
        
        health_snapshot = SystemHealth(
            timestamp=datetime.now().isoformat(),
            overall_score=health_score,
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=(disk.used / disk.total) * 100,
            rag_components_health={},  # Will be updated by RAG system
            active_queries=0,  # Will be updated by query processor
            error_rate=0  # Will be calculated from metrics
        )
        
        self.health_history.append(health_snapshot)
    
    def _calculate_health_score(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate overall system health score"""
        score = 100.0
        
        # CPU score (deduct points for high usage)
        if cpu > 90:
            score -= 30
        elif cpu > 80:
            score -= 20
        elif cpu > 70:
            score -= 10
        
        # Memory score
        if memory > 95:
            score -= 40
        elif memory > 90:
            score -= 25
        elif memory > 80:
            score -= 15
        
        # Disk score
        if disk > 95:
            score -= 20
        elif disk > 90:
            score -= 10
        
        return max(score, 0.0)
    
    def get_current_health(self) -> Optional[SystemHealth]:
        """Get current system health"""
        if self.health_history:
            return self.health_history[-1]
        return None
    
    def get_health_trend(self, hours: int = 1) -> List[SystemHealth]:
        """Get health trend for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat()
        
        return [h for h in self.health_history if h.timestamp >= cutoff_str]


def performance_monitor(component: str, operation: str = None):
    """Decorator for monitoring function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = operation or func.__name__
            
            try:
                result = func(*args, **kwargs)
                
                # Record success metric
                execution_time = time.time() - start_time
                if hasattr(performance_monitor, '_metrics_collector'):
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_time', execution_time, 'seconds', component
                    )
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_success', 1, 'count', component
                    )
                
                return result
                
            except Exception as e:
                # Record failure metric
                execution_time = time.time() - start_time
                if hasattr(performance_monitor, '_metrics_collector'):
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_time', execution_time, 'seconds', component
                    )
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_failure', 1, 'count', component
                    )
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = operation or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success metric
                execution_time = time.time() - start_time
                if hasattr(performance_monitor, '_metrics_collector'):
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_time', execution_time, 'seconds', component
                    )
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_success', 1, 'count', component
                    )
                
                return result
                
            except Exception as e:
                # Record failure metric
                execution_time = time.time() - start_time
                if hasattr(performance_monitor, '_metrics_collector'):
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_time', execution_time, 'seconds', component
                    )
                    performance_monitor._metrics_collector.record_metric(
                        f'{operation_name}_failure', 1, 'count', component
                    )
                raise
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class PerformanceAnalyzer:
    """Analyzes performance metrics and provides insights"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
    
    def analyze_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance over specified time period"""
        since = datetime.now() - timedelta(hours=hours)
        metrics = self.metrics_collector.get_metrics(since=since)
        
        if not metrics:
            return {'error': 'No metrics available for analysis'}
        
        # Group metrics by component and operation
        component_stats = defaultdict(lambda: defaultdict(list))
        
        for metric in metrics:
            component_stats[metric.component][metric.name].append(metric.value)
        
        # Calculate statistics for each component
        analysis = {}
        
        for component, operations in component_stats.items():
            component_analysis = {}
            
            for operation, values in operations.items():
                if values:
                    sorted_values = sorted(values)
                    count = len(values)
                    
                    stats = {
                        'count': count,
                        'avg': sum(values) / count,
                        'min': min(values),
                        'max': max(values),
                        'median': sorted_values[count // 2],
                        'p95': sorted_values[int(count * 0.95)] if count > 0 else 0,
                        'p99': sorted_values[int(count * 0.99)] if count > 0 else 0
                    }
                    
                    component_analysis[operation] = stats
            
            analysis[component] = component_analysis
        
        # Add performance insights
        insights = self._generate_insights(analysis)
        
        return {
            'analysis_period_hours': hours,
            'total_metrics': len(metrics),
            'components_analyzed': len(component_stats),
            'performance_stats': analysis,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance insights from analysis"""
        insights = []
        
        for component, operations in analysis.items():
            # Check for slow operations
            for operation, stats in operations.items():
                if 'time' in operation and stats['avg'] > 5.0:
                    insights.append(
                        f"Slow performance detected in {component}.{operation}: "
                        f"avg {stats['avg']:.2f}s, p95 {stats['p95']:.2f}s"
                    )
                
                # Check for high failure rates
                if 'failure' in operation and 'success' in operation:
                    failure_count = stats.get('count', 0)
                    success_stats = operations.get(operation.replace('failure', 'success'), {})
                    success_count = success_stats.get('count', 0)
                    
                    if failure_count + success_count > 0:
                        failure_rate = failure_count / (failure_count + success_count)
                        if failure_rate > 0.1:  # More than 10% failure rate
                            insights.append(
                                f"High failure rate in {component}.{operation}: "
                                f"{failure_rate:.1%} ({failure_count} failures)"
                            )
        
        return insights
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        # Get recent performance analysis
        recent_analysis = self.analyze_performance(hours=1)
        daily_analysis = self.analyze_performance(hours=24)
        
        # Get top metrics by component
        top_metrics = self._get_top_metrics_by_component()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(recent_analysis, daily_analysis)
        
        return {
            'report_generated_at': datetime.now().isoformat(),
            'recent_performance': recent_analysis,
            'daily_performance': daily_analysis,
            'top_metrics': top_metrics,
            'recommendations': recommendations
        }
    
    def _get_top_metrics_by_component(self) -> Dict[str, Any]:
        """Get top metrics for each component"""
        top_metrics = {}
        
        # Get aggregated stats for all metric keys
        for metric_key in self.metrics_collector.aggregated_metrics.keys():
            stats = self.metrics_collector.get_aggregated_stats(metric_key)
            component, metric_name = metric_key.split('.', 1)
            
            if component not in top_metrics:
                top_metrics[component] = {}
            
            top_metrics[component][metric_name] = stats
        
        return top_metrics
    
    def _generate_recommendations(self, recent: Dict[str, Any], 
                                daily: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Combine insights from both periods
        recent_insights = recent.get('insights', [])
        daily_insights = daily.get('insights', [])
        
        all_insights = set(recent_insights + daily_insights)
        
        # Convert insights to recommendations
        for insight in all_insights:
            if 'slow performance' in insight.lower():
                recommendations.append(
                    "Consider optimizing slow operations or implementing caching"
                )
            elif 'high failure rate' in insight.lower():
                recommendations.append(
                    "Investigate and fix components with high failure rates"
                )
        
        # Add general recommendations
        if not recommendations:
            recommendations.append("System performance appears healthy")
        
        return list(set(recommendations))


class PerformanceMonitoringSystem:
    """Main performance monitoring system"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.system_monitor = SystemMonitor(self.metrics_collector)
        self.analyzer = PerformanceAnalyzer(self.metrics_collector)
        
        # Set global metrics collector for decorator
        performance_monitor._metrics_collector = self.metrics_collector
        
        # Monitoring state
        self.is_monitoring = False
        
        logger.info("Performance monitoring system initialized")
    
    def start_monitoring(self, interval: float = 5.0) -> None:
        """Start comprehensive monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
        
        self.system_monitor.start_monitoring(interval)
        self.is_monitoring = True
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        if not self.is_monitoring:
            return
        
        self.system_monitor.stop_monitoring()
        self.is_monitoring = False
        
        logger.info("Performance monitoring stopped")
    
    def record_custom_metric(self, name: str, value: float, unit: str, 
                           component: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a custom metric"""
        self.metrics_collector.record_metric(name, value, unit, component, metadata)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard"""
        # Get current health
        current_health = self.system_monitor.get_current_health()
        
        # Get recent metrics summary
        recent_analysis = self.analyzer.analyze_performance(hours=1)
        
        # Get health trend
        health_trend = self.system_monitor.get_health_trend(hours=6)
        
        return {
            'current_health': asdict(current_health) if current_health else None,
            'health_trend': [asdict(h) for h in health_trend],
            'recent_performance': recent_analysis,
            'monitoring_active': self.is_monitoring,
            'dashboard_updated_at': datetime.now().isoformat()
        }
    
    def export_metrics(self, filepath: str, hours: int = 24) -> bool:
        """Export metrics to file"""
        try:
            since = datetime.now() - timedelta(hours=hours)
            metrics = self.metrics_collector.get_metrics(since=since)
            
            # Convert metrics to JSON-serializable format
            metrics_data = {
                'export_timestamp': datetime.now().isoformat(),
                'export_period_hours': hours,
                'metrics_count': len(metrics),
                'metrics': [asdict(metric) for metric in metrics]
            }
            
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(metrics)} metrics to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'monitoring_active': self.is_monitoring,
            'metrics_collected': len(self.metrics_collector.metrics),
            'current_health': self.system_monitor.get_current_health(),
            'performance_report': self.analyzer.get_performance_report()
        }


# Global instance for easy access
_global_monitor: Optional[PerformanceMonitoringSystem] = None


def get_global_monitor() -> PerformanceMonitoringSystem:
    """Get or create global performance monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitoringSystem()
    return _global_monitor


def start_global_monitoring(interval: float = 5.0) -> None:
    """Start global monitoring"""
    monitor = get_global_monitor()
    monitor.start_monitoring(interval)


def stop_global_monitoring() -> None:
    """Stop global monitoring"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring()
