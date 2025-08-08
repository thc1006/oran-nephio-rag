"""
O-RAN × Nephio RAG System Monitoring and Observability
Based on 2024 best practices with OpenTelemetry, Prometheus, and Grafana
"""
import time
import logging
import functools
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import psutil
import json

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

# Prometheus client
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server

try:
    from .config import Config
except ImportError:
    from config import Config

logger = logging.getLogger(__name__)


class RAGSystemMetrics:
    """
    Comprehensive metrics collection for RAG system
    """
    
    def __init__(self, config=None):
        self.config = config or Config()
        # Initialize OpenTelemetry
        self._setup_opentelemetry()
        
        # System metrics
        self.system_info = Gauge(
            'rag_system_info', 
            'System information', 
            ['version', 'python_version', 'host']
        )
        
        # Query metrics
        self.query_total = Counter(
            'rag_queries_total', 
            'Total number of queries processed', 
            ['status', 'query_type']
        )
        
        self.query_duration = Histogram(
            'rag_query_duration_seconds',
            'Time spent processing queries',
            ['query_type', 'model'],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float('inf'))
        )
        
        self.query_response_size = Histogram(
            'rag_query_response_size_bytes',
            'Size of query responses in bytes',
            buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, float('inf'))
        )
        
        # Document loading metrics
        self.documents_loaded = Counter(
            'rag_documents_loaded_total',
            'Total number of documents loaded',
            ['source_type', 'status']
        )
        
        self.document_loading_duration = Histogram(
            'rag_document_loading_duration_seconds',
            'Time spent loading documents',
            ['source_type'],
            buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, float('inf'))
        )
        
        # Vector database metrics
        self.vectordb_operations = Counter(
            'rag_vectordb_operations_total',
            'Vector database operations',
            ['operation', 'status']
        )
        
        self.vectordb_search_duration = Histogram(
            'rag_vectordb_search_duration_seconds',
            'Vector database search duration',
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, float('inf'))
        )
        
        # AI model metrics
        self.ai_model_requests = Counter(
            'rag_ai_model_requests_total',
            'AI model API requests',
            ['model', 'status']
        )
        
        self.ai_model_duration = Histogram(
            'rag_ai_model_request_duration_seconds',
            'AI model request duration',
            ['model'],
            buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0, float('inf'))
        )
        
        self.ai_model_tokens = Histogram(
            'rag_ai_model_tokens_total',
            'AI model tokens used',
            ['model', 'type'],
            buckets=(10, 50, 100, 500, 1000, 2000, 5000, 10000, float('inf'))
        )
        
        # System resource metrics
        self.system_cpu_usage = Gauge('rag_system_cpu_usage_percent', 'CPU usage percentage')
        self.system_memory_usage = Gauge('rag_system_memory_usage_bytes', 'Memory usage in bytes')
        self.system_disk_usage = Gauge('rag_system_disk_usage_bytes', 'Disk usage in bytes')
        
        # Application-specific metrics
        self.active_sessions = Gauge('rag_active_sessions', 'Number of active sessions')
        self.cache_hit_rate = Gauge('rag_cache_hit_rate', 'Cache hit rate percentage')
        self.error_rate = Gauge('rag_error_rate_percent', 'Error rate percentage')
        
        # OpenTelemetry metrics
        self.meter = metrics.get_meter(__name__)
        self.tracer = trace.get_tracer(__name__)
        
        # Custom metrics with OpenTelemetry
        self.otel_query_counter = self.meter.create_counter(
            "rag_otel_queries_total",
            description="Total queries processed via OpenTelemetry"
        )
        
        self.otel_response_time = self.meter.create_histogram(
            "rag_otel_response_time_ms",
            description="Response time in milliseconds",
            unit="ms"
        )
        
        # Start system metrics collection
        self._start_system_metrics_collection()
        
    def _setup_opentelemetry(self):
        """Setup OpenTelemetry with exporters"""
        # Setup tracing
        trace.set_tracer_provider(TracerProvider())
        
        # Jaeger exporter for distributed tracing
        jaeger_exporter = JaegerExporter(
            agent_host_name=self.config.JAEGER_AGENT_HOST if hasattr(self, 'config') else Config.JAEGER_AGENT_HOST,
            agent_port=self.config.JAEGER_AGENT_PORT if hasattr(self, 'config') else Config.JAEGER_AGENT_PORT,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Setup metrics
        # Prometheus exporter
        prometheus_reader = PrometheusMetricReader()
        
        # OTLP exporter for metrics
        otlp_exporter = OTLPMetricExporter(
            endpoint=self.config.OTLP_ENDPOINT if hasattr(self, 'config') else Config.OTLP_ENDPOINT,
            insecure=self.config.OTLP_INSECURE if hasattr(self, 'config') else Config.OTLP_INSECURE
        )
        otlp_reader = PeriodicExportingMetricReader(
            exporter=otlp_exporter,
            export_interval_millis=10000
        )
        
        metrics.set_meter_provider(
            MeterProvider(metric_readers=[prometheus_reader, otlp_reader])
        )
        
        # Setup propagation
        set_global_textmap(B3MultiFormat())
        
        # Auto-instrumentation
        RequestsInstrumentor().instrument()
        LoggingInstrumentor().instrument()
        URLLib3Instrumentor().instrument()
        
    def _start_system_metrics_collection(self):
        """Start background thread for system metrics collection"""
        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.system_cpu_usage.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.system_memory_usage.set(memory.used)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    self.system_disk_usage.set(disk.used)
                    
                    time.sleep(30)  # Collect every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")
                    time.sleep(60)  # Wait longer on error
        
        metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
        metrics_thread.start()
        
    @contextmanager
    def track_query(self, query_type: str = "default", model: str = "claude"):
        """Context manager for tracking query performance"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span("rag_query_processing") as span:
            span.set_attribute("query.type", query_type)
            span.set_attribute("ai.model", model)
            
            try:
                yield
                
                # Success metrics
                duration = time.time() - start_time
                self.query_total.labels(status="success", query_type=query_type).inc()
                self.query_duration.labels(query_type=query_type, model=model).observe(duration)
                self.otel_query_counter.add(1, {"status": "success", "type": query_type})
                self.otel_response_time.record(duration * 1000, {"type": query_type})
                
                span.set_attribute("query.duration", duration)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
            except Exception as e:
                # Error metrics
                self.query_total.labels(status="error", query_type=query_type).inc()
                self.otel_query_counter.add(1, {"status": "error", "type": query_type})
                
                span.set_attribute("error.message", str(e))
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
                
    @contextmanager
    def track_document_loading(self, source_type: str):
        """Context manager for tracking document loading"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span("document_loading") as span:
            span.set_attribute("document.source_type", source_type)
            
            try:
                yield
                
                duration = time.time() - start_time
                self.documents_loaded.labels(source_type=source_type, status="success").inc()
                self.document_loading_duration.labels(source_type=source_type).observe(duration)
                
                span.set_attribute("loading.duration", duration)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
            except Exception as e:
                self.documents_loaded.labels(source_type=source_type, status="error").inc()
                
                span.set_attribute("error.message", str(e))
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
                
    @contextmanager
    def track_vectordb_operation(self, operation: str):
        """Context manager for tracking vector database operations"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span("vectordb_operation") as span:
            span.set_attribute("vectordb.operation", operation)
            
            try:
                yield
                
                if operation == "search":
                    duration = time.time() - start_time
                    self.vectordb_search_duration.observe(duration)
                
                self.vectordb_operations.labels(operation=operation, status="success").inc()
                span.set_status(trace.Status(trace.StatusCode.OK))
                
            except Exception as e:
                self.vectordb_operations.labels(operation=operation, status="error").inc()
                
                span.set_attribute("error.message", str(e))
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
                
    @contextmanager
    def track_ai_model_request(self, model: str):
        """Context manager for tracking AI model requests"""
        start_time = time.time()
        
        with self.tracer.start_as_current_span("ai_model_request") as span:
            span.set_attribute("ai.model", model)
            
            try:
                yield
                
                duration = time.time() - start_time
                self.ai_model_requests.labels(model=model, status="success").inc()
                self.ai_model_duration.labels(model=model).observe(duration)
                
                span.set_attribute("request.duration", duration)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
            except Exception as e:
                self.ai_model_requests.labels(model=model, status="error").inc()
                
                span.set_attribute("error.message", str(e))
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
                
    def record_response_size(self, size_bytes: int):
        """Record the size of a query response"""
        self.query_response_size.observe(size_bytes)
        
    def record_token_usage(self, model: str, input_tokens: int, output_tokens: int):
        """Record AI model token usage"""
        self.ai_model_tokens.labels(model=model, type="input").observe(input_tokens)
        self.ai_model_tokens.labels(model=model, type="output").observe(output_tokens)
        
    def update_active_sessions(self, count: int):
        """Update active sessions count"""
        self.active_sessions.set(count)
        
    def update_cache_hit_rate(self, rate: float):
        """Update cache hit rate percentage"""
        self.cache_hit_rate.set(rate * 100)
        
    def update_error_rate(self, rate: float):
        """Update error rate percentage"""
        self.error_rate.set(rate * 100)


class HealthChecker:
    """
    Health checking and status monitoring
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.metrics = RAGSystemMetrics()
        self.last_health_check = None
        self.health_status = {}
        
    async def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        health_checks = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Check system resources
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_checks["checks"]["system"] = {
                "status": "healthy" if cpu_usage < 80 and memory.percent < 85 else "degraded",
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent
            }
        except Exception as e:
            health_checks["checks"]["system"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            
        # Check vector database
        try:
            # This would check if vector database is accessible
            health_checks["checks"]["vectordb"] = {
                "status": "healthy",
                "connection": "ok"
            }
        except Exception as e:
            health_checks["checks"]["vectordb"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            
        # Check AI model API
        try:
            # This would ping the AI model API
            health_checks["checks"]["ai_model"] = {
                "status": "healthy",
                "api_accessible": True
            }
        except Exception as e:
            health_checks["checks"]["ai_model"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            
        # Determine overall status
        statuses = [check["status"] for check in health_checks["checks"].values()]
        if "unhealthy" in statuses:
            health_checks["status"] = "unhealthy"
        elif "degraded" in statuses:
            health_checks["status"] = "degraded"
            
        self.last_health_check = health_checks
        return health_checks
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of key metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "application": {
                "active_sessions": self.metrics.active_sessions._value._value,
                "cache_hit_rate": self.metrics.cache_hit_rate._value._value,
                "error_rate": self.metrics.error_rate._value._value
            }
        }


class AlertManager:
    """
    Alert management and notification system
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.alert_thresholds = {
            "cpu_usage": 85.0,
            "memory_usage": 90.0,
            "disk_usage": 95.0,
            "error_rate": 5.0,
            "response_time": 30.0
        }
        self.active_alerts = {}
        
    def check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        current_time = datetime.now()
        
        # CPU usage alert
        if metrics.get("system", {}).get("cpu_usage", 0) > self.alert_thresholds["cpu_usage"]:
            self._create_alert("high_cpu_usage", metrics["system"]["cpu_usage"], current_time)
            
        # Memory usage alert
        if metrics.get("system", {}).get("memory_usage", 0) > self.alert_thresholds["memory_usage"]:
            self._create_alert("high_memory_usage", metrics["system"]["memory_usage"], current_time)
            
        # Error rate alert
        if metrics.get("application", {}).get("error_rate", 0) > self.alert_thresholds["error_rate"]:
            self._create_alert("high_error_rate", metrics["application"]["error_rate"], current_time)
            
    def _create_alert(self, alert_type: str, value: float, timestamp: datetime):
        """Create and log an alert"""
        alert_id = f"{alert_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        alert = {
            "id": alert_id,
            "type": alert_type,
            "value": value,
            "threshold": self.alert_thresholds.get(alert_type, 0),
            "timestamp": timestamp.isoformat(),
            "status": "active"
        }
        
        self.active_alerts[alert_id] = alert
        logger.warning(f"Alert generated: {alert_type} - Value: {value}")
        
        # Here you would integrate with notification systems
        # (Slack, email, PagerDuty, etc.)
        
    def get_active_alerts(self) -> Dict[str, Any]:
        """Get all active alerts"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_count": len(self.active_alerts),
            "alerts": list(self.active_alerts.values())
        }


def monitoring_decorator(metrics: RAGSystemMetrics, operation_type: str = "default"):
    """Decorator for automatic monitoring of functions"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if operation_type == "query":
                with metrics.track_query():
                    return func(*args, **kwargs)
            elif operation_type == "document_loading":
                with metrics.track_document_loading("default"):
                    return func(*args, **kwargs)
            elif operation_type == "vectordb":
                with metrics.track_vectordb_operation("search"):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global metrics instance
_global_metrics = RAGSystemMetrics()

def get_metrics() -> RAGSystemMetrics:
    """Get global metrics instance"""
    return _global_metrics

def start_metrics_server(port: int = 8000):
    """Start Prometheus metrics server"""
    start_http_server(port)
    logger.info(f"Metrics server started on port {port}")

# Example usage functions
def setup_monitoring(config: Optional[Config] = None, metrics_port: int = 8000):
    """Setup complete monitoring system"""
    start_metrics_server(metrics_port)
    health_checker = HealthChecker(config)
    alert_manager = AlertManager(config)
    
    logger.info("Monitoring system initialized successfully")
    
    return {
        "metrics": get_metrics(),
        "health_checker": health_checker,
        "alert_manager": alert_manager
    }