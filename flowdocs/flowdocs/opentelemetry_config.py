"""
OpenTelemetry Configuration for AI Document Search Platform
Provides comprehensive observability across all application components
"""

import os
import logging
from typing import Optional, Dict, Any
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
try:
    from opentelemetry.semantic_conventions.resource import ResourceAttributes
except ImportError:
    # Fallback for older versions
    ResourceAttributes = None
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenTelemetryConfig:
    """Centralized OpenTelemetry configuration and initialization"""
    
    def __init__(self):
        self.service_name = os.getenv('OTEL_SERVICE_NAME', 'ai-document-search')
        self.service_version = os.getenv('OTEL_SERVICE_VERSION', '1.0.0')
        self.environment = os.getenv('OTEL_ENVIRONMENT', 'development')
        self.traces_endpoint = os.getenv('OTEL_EXPORTER_JAEGER_ENDPOINT', 'http://localhost:14268/api/traces')
        self.metrics_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
        self.enable_jaeger = os.getenv('OTEL_ENABLE_JAEGER', 'true').lower() == 'true'
        self.enable_prometheus = os.getenv('OTEL_ENABLE_PROMETHEUS', 'true').lower() == 'true'
        self.enable_otlp = os.getenv('OTEL_ENABLE_OTLP', 'false').lower() == 'true'
        
        self.tracer = None
        self.meter = None
        self._initialized = False
    
    def _create_resource(self) -> Resource:
        """Create OpenTelemetry resource with service metadata"""
        resource_attrs = {
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.environment,
            "service.namespace": "ai-document-search",
            "service.instance.id": os.getenv('HOSTNAME', 'unknown'),
            "service.owner": "Maharashtra IT Department",
            "service.description": "AI-powered document search and analysis platform",
        }
        
        # Add semantic conventions if available
        if ResourceAttributes:
            resource_attrs.update({
                ResourceAttributes.SERVICE_NAME: self.service_name,
                ResourceAttributes.SERVICE_VERSION: self.service_version,
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.environment,
                ResourceAttributes.SERVICE_NAMESPACE: "ai-document-search",
            })
        
        return Resource.create(resource_attrs)
    
    def _setup_tracing(self) -> None:
        """Configure and initialize tracing"""
        try:
            # Create tracer provider
            tracer_provider = TracerProvider(
                resource=self._create_resource(),
                active_span_processor=BatchSpanProcessor(
                    max_export_batch_size=512,
                    export_timeout_millis=30000,
                    schedule_delay_millis=5000,
                )
            )
            
            # Set global tracer provider
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)
            
            # Configure exporters
            if self.enable_jaeger:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=os.getenv('JAEGER_AGENT_HOST', 'localhost'),
                    agent_port=int(os.getenv('JAEGER_AGENT_PORT', '14268')),
                )
                tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
                logger.info("✅ Jaeger tracing enabled")
            
            if self.enable_otlp:
                otlp_exporter = OTLPSpanExporter(
                    endpoint=self.metrics_endpoint,
                    insecure=True,
                )
                tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                logger.info("✅ OTLP tracing enabled")
            
            logger.info("✅ Tracing configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure tracing: {e}")
            raise
    
    def _setup_metrics(self) -> None:
        """Configure and initialize metrics"""
        try:
            # Create metric readers
            readers = []
            
            if self.enable_prometheus:
                prometheus_reader = PrometheusMetricReader()
                readers.append(prometheus_reader)
                logger.info("✅ Prometheus metrics enabled")
            
            if self.enable_otlp:
                otlp_reader = PeriodicExportingMetricReader(
                    OTLPMetricExporter(
                        endpoint=self.metrics_endpoint,
                        insecure=True,
                    ),
                    export_interval_millis=10000,
                )
                readers.append(otlp_reader)
                logger.info("✅ OTLP metrics enabled")
            
            # Create meter provider
            meter_provider = MeterProvider(
                resource=self._create_resource(),
                metric_readers=readers,
            )
            
            # Set global meter provider
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter(__name__)
            
            logger.info("✅ Metrics configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure metrics: {e}")
            raise
    
    def _setup_instrumentation(self) -> None:
        """Configure automatic instrumentation for various libraries"""
        try:
            # Django instrumentation
            DjangoInstrumentor().instrument(
                is_sql_commentor_enabled=True,
                is_sql_commentor_sanitize_enabled=True,
                is_commenter_enabled=True,
                is_commenter_sanitize_enabled=True,
            )
            logger.info("✅ Django instrumentation enabled")
            
            # Database instrumentation
            Psycopg2Instrumentor().instrument()
            SQLAlchemyInstrumentor().instrument()
            logger.info("✅ Database instrumentation enabled")
            
            # HTTP requests instrumentation
            RequestsInstrumentor().instrument()
            logger.info("✅ HTTP requests instrumentation enabled")
            
            # Redis instrumentation (if used)
            try:
                RedisInstrumentor().instrument()
                logger.info("✅ Redis instrumentation enabled")
            except Exception as e:
                logger.warning(f"⚠️ Redis instrumentation skipped: {e}")
            
            # Celery instrumentation (if used)
            try:
                CeleryInstrumentor().instrument()
                logger.info("✅ Celery instrumentation enabled")
            except Exception as e:
                logger.warning(f"⚠️ Celery instrumentation skipped: {e}")
            
            logger.info("✅ All instrumentation configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure instrumentation: {e}")
            raise
    
    def initialize(self) -> None:
        """Initialize OpenTelemetry with all components"""
        if self._initialized:
            logger.warning("⚠️ OpenTelemetry already initialized")
            return
        
        try:
            logger.info("🚀 Initializing OpenTelemetry...")
            
            # Setup all components
            self._setup_tracing()
            self._setup_metrics()
            self._setup_instrumentation()
            
            self._initialized = True
            logger.info("✅ OpenTelemetry initialization completed successfully")
            
        except Exception as e:
            logger.error(f"❌ OpenTelemetry initialization failed: {e}")
            raise
    
    def get_tracer(self, name: str = None) -> trace.Tracer:
        """Get a tracer instance"""
        if not self._initialized:
            self.initialize()
        return self.tracer
    
    def get_meter(self, name: str = None) -> metrics.Meter:
        """Get a meter instance"""
        if not self._initialized:
            self.initialize()
        return self.meter
    
    def create_span(self, name: str, **kwargs) -> trace.Span:
        """Create a new span"""
        tracer = self.get_tracer()
        return tracer.start_span(name, **kwargs)
    
    def create_counter(self, name: str, description: str = "", unit: str = "1") -> metrics.Counter:
        """Create a counter metric"""
        meter = self.get_meter()
        return meter.create_counter(
            name=name,
            description=description,
            unit=unit,
        )
    
    def create_histogram(self, name: str, description: str = "", unit: str = "s") -> metrics.Histogram:
        """Create a histogram metric"""
        meter = self.get_meter()
        return meter.create_histogram(
            name=name,
            description=description,
            unit=unit,
        )
    
    def create_gauge(self, name: str, description: str = "", unit: str = "1") -> metrics.Gauge:
        """Create a gauge metric"""
        meter = self.get_meter()
        return meter.create_gauge(
            name=name,
            description=description,
            unit=unit,
        )

# Global instance
otel_config = OpenTelemetryConfig()

# Convenience functions
def get_tracer(name: str = None) -> trace.Tracer:
    """Get a tracer instance"""
    return otel_config.get_tracer(name)

def get_meter(name: str = None) -> metrics.Meter:
    """Get a meter instance"""
    return otel_config.get_meter(name)

def create_span(name: str, **kwargs) -> trace.Span:
    """Create a new span"""
    return otel_config.create_span(name, **kwargs)

def create_counter(name: str, description: str = "", unit: str = "1") -> metrics.Counter:
    """Create a counter metric"""
    return otel_config.create_counter(name, description, unit)

def create_histogram(name: str, description: str = "", unit: str = "s") -> metrics.Histogram:
    """Create a histogram metric"""
    return otel_config.create_histogram(name, description, unit)

def create_gauge(name: str, description: str = "", unit: str = "1") -> metrics.Gauge:
    """Create a gauge metric"""
    return otel_config.create_gauge(name, description, unit)

# Initialize on import
try:
    otel_config.initialize()
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenTelemetry: {e}")
    # Continue without OpenTelemetry if initialization fails
    pass
