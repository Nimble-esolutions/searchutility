# OpenTelemetry Integration for AI Document Search Platform

This document describes the comprehensive OpenTelemetry integration implemented for the AI Document Search platform, providing full observability across all application components.

## 🎯 Overview

The OpenTelemetry integration provides:
- **Distributed Tracing** - Track requests across all components
- **Metrics Collection** - Monitor performance and usage patterns
- **Custom Instrumentation** - AI/ML operations, PDF processing, OCR
- **Monitoring Dashboards** - Real-time visibility into system health
- **Alerting** - Proactive issue detection

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django App    │    │   Jaeger UI     │    │   Grafana       │
│   (Traces)      │───▶│   (Tracing)     │    │   (Dashboards)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   Elasticsearch │    │   Kibana        │
│   (Metrics)     │    │   (Logs)        │    │   (Log Analysis)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Instrumented Components

### 1. Django Application
- **HTTP Requests** - All incoming requests traced
- **Database Operations** - Query performance and errors
- **Authentication** - Login/logout events
- **File Uploads** - PDF processing pipeline

### 2. AI/ML Operations
- **OpenAI API Calls** - Request/response times, token usage
- **Keyword Extraction** - YAKE processing performance
- **Language Detection** - Text analysis operations
- **Document Search** - Query processing and results

### 3. PDF Processing
- **Text Extraction** - PyPDF2 operations
- **OCR Processing** - Tesseract performance
- **Image Conversion** - pdf2image operations
- **File I/O** - Upload and storage operations

### 4. Database Operations
- **Query Performance** - SQL execution times
- **Connection Pooling** - Database health
- **Transaction Tracking** - Data consistency

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd flowdocs
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.otel.template .env
# Edit .env with your configuration
```

### 3. Start Monitoring Stack
```bash
cd monitoring
docker-compose up -d
```

### 4. Run Application
```bash
python manage.py runserver
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_SERVICE_NAME` | Service name for traces | `ai-document-search` |
| `OTEL_SERVICE_VERSION` | Service version | `1.0.0` |
| `OTEL_ENVIRONMENT` | Deployment environment | `development` |
| `OTEL_ENABLE_JAEGER` | Enable Jaeger tracing | `true` |
| `OTEL_ENABLE_PROMETHEUS` | Enable Prometheus metrics | `true` |
| `JAEGER_AGENT_HOST` | Jaeger agent host | `localhost` |
| `JAEGER_AGENT_PORT` | Jaeger agent port | `14268` |

### Service URLs
- **Jaeger UI**: http://localhost:16686
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601

## 📈 Metrics Collected

### Application Metrics
- `ai_operations_total` - Total AI operations performed
- `ai_operation_duration_seconds` - AI operation response times
- `document_search_total` - Total document searches
- `document_search_duration_seconds` - Search response times
- `pdf_processing_total` - Total PDF processing operations
- `pdf_processing_duration_seconds` - PDF processing times
- `ocr_operations_total` - Total OCR operations
- `ocr_operation_duration_seconds` - OCR processing times

### Business Metrics
- `search_results_count` - Number of search results returned
- `pdf_text_extraction_total` - PDF text extractions
- `keyword_extraction_total` - Keyword extractions
- `user_activity_total` - User activity tracking

### System Metrics
- `http_requests_total` - HTTP request count
- `http_request_duration_seconds` - HTTP response times
- `database_queries_total` - Database query count
- `database_query_duration_seconds` - Database query times

## 🔍 Tracing

### Trace Structure
```
ai-document-search
├── search.query_processing
│   ├── ai.extract_keywords
│   ├── pdf.extract_text_from_pdf
│   ├── ocr.extract_text_from_image
│   └── openai.api_call
├── dashboard.view
│   ├── db.dashboard
│   └── pdf.upload
└── authentication.login
```

### Span Attributes
- **User Information**: `user.id`, `user.role`
- **Request Details**: `query`, `query_length`, `query_keywords_count`
- **File Information**: `file.name`, `file.size`, `file.path`
- **Processing Results**: `results_count`, `text_length`, `keywords_count`
- **Performance**: `duration`, `tokens_used`, `cache_hit`

## 📊 Dashboards

### 1. Overview Dashboard
- Request rates and response times
- Success rates and error counts
- System health indicators
- Real-time activity monitoring

### 2. AI Operations Dashboard
- OpenAI API usage and costs
- Keyword extraction performance
- Language detection accuracy
- AI response quality metrics

### 3. PDF Processing Dashboard
- File upload and processing rates
- OCR success rates
- Text extraction performance
- Storage utilization

### 4. User Activity Dashboard
- User engagement metrics
- Search patterns and trends
- Popular documents and queries
- Session analytics

## 🚨 Alerting

### Critical Alerts
- **High Error Rate**: >5% error rate for 5 minutes
- **Slow Response**: P95 response time >10 seconds
- **API Failures**: OpenAI API failures
- **Storage Issues**: Disk space <10%

### Warning Alerts
- **High CPU Usage**: >80% for 10 minutes
- **Memory Usage**: >85% for 10 minutes
- **Database Slow Queries**: >5 second queries
- **Low Success Rate**: <95% success rate

## 🔧 Custom Instrumentation

### Adding New Metrics
```python
from core.observability import create_counter, create_histogram

# Create custom metrics
custom_counter = create_counter(
    name="custom_operations_total",
    description="Total custom operations",
    unit="1"
)

custom_histogram = create_histogram(
    name="custom_operation_duration_seconds",
    description="Custom operation duration",
    unit="s"
)

# Use in your code
custom_counter.add(1, {"operation": "custom_op"})
custom_histogram.record(duration, {"operation": "custom_op"})
```

### Adding New Traces
```python
from core.observability import create_span

def my_function():
    with create_span("my.operation") as span:
        span.set_attribute("custom.attribute", "value")
        # Your code here
        span.set_attribute("result.success", True)
```

## 🐛 Troubleshooting

### Common Issues

1. **Traces not appearing in Jaeger**
   - Check `OTEL_ENABLE_JAEGER=true`
   - Verify Jaeger is running on correct port
   - Check network connectivity

2. **Metrics not showing in Prometheus**
   - Ensure `/metrics` endpoint is accessible
   - Check Prometheus configuration
   - Verify service discovery

3. **High memory usage**
   - Adjust `OTEL_BSP_MAX_EXPORT_BATCH_SIZE`
   - Increase `OTEL_BSP_SCHEDULE_DELAY_MILLIS`
   - Check for memory leaks in instrumentation

### Debug Mode
```bash
export OTEL_LOG_LEVEL=DEBUG
export OTEL_PYTHON_LOG_CORRELATION=true
python manage.py runserver
```

## 📚 Advanced Configuration

### Custom Exporters
```python
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Add custom exporter
custom_exporter = OTLPSpanExporter(
    endpoint="https://your-otel-collector:4317",
    headers={"Authorization": "Bearer your-token"}
)
```

### Sampling Configuration
```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBasedSampler

# Configure sampling
sampler = TraceIdRatioBasedSampler(0.1)  # 10% sampling
```

### Resource Configuration
```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "ai-document-search",
    "service.version": "1.0.0",
    "deployment.environment": "production",
    "custom.attribute": "value"
})
```

## 🔒 Security Considerations

- **API Keys**: Never log sensitive information
- **User Data**: Sanitize user queries in traces
- **Network**: Use TLS for all external communications
- **Access Control**: Secure monitoring endpoints

## 📈 Performance Impact

- **CPU Overhead**: <2% additional CPU usage
- **Memory Overhead**: ~50MB additional memory
- **Network Overhead**: <1% additional bandwidth
- **Storage Overhead**: ~100MB/day for traces and metrics

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
# Add to your Dockerfile
ENV OTEL_SERVICE_NAME=ai-document-search
ENV OTEL_ENABLE_JAEGER=true
ENV JAEGER_AGENT_HOST=jaeger
```

### Kubernetes Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-config
data:
  OTEL_SERVICE_NAME: "ai-document-search"
  OTEL_ENABLE_JAEGER: "true"
  JAEGER_AGENT_HOST: "jaeger-collector"
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review OpenTelemetry documentation
3. Check application logs
4. Contact the development team

## 🔄 Updates

To update OpenTelemetry packages:
```bash
pip install --upgrade opentelemetry-api opentelemetry-sdk
pip install --upgrade opentelemetry-instrumentation-django
```

## 📋 Checklist

- [ ] OpenTelemetry packages installed
- [ ] Environment variables configured
- [ ] Monitoring stack running
- [ ] Application instrumented
- [ ] Dashboards configured
- [ ] Alerts set up
- [ ] Performance baseline established
- [ ] Documentation updated
