"""
Custom OpenTelemetry instrumentation for AI Document Search components
Provides detailed observability for AI/ML operations, PDF processing, and document search
"""

import time
import logging
from typing import Dict, Any, Optional, List
from functools import wraps
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
# Note: semantic_conventions may not be available in all versions
try:
    from opentelemetry.semantic_conventions.trace import SpanAttributes
    from opentelemetry.semantic_conventions.metrics import MetricInstruments
except ImportError:
    # Fallback for older versions
    SpanAttributes = None
    MetricInstruments = None
try:
    from .opentelemetry_config import get_tracer, get_meter, create_counter, create_histogram, create_gauge
except ImportError:
    # Fallback for when opentelemetry_config is not available
    def get_tracer(name=None):
        return None
    def get_meter(name=None):
        return None
    def create_counter(name, description="", unit="1"):
        return None
    def create_histogram(name, description="", unit="s"):
        return None
    def create_gauge(name, description="", unit="1"):
        return None

logger = logging.getLogger(__name__)

# Get tracer and meter
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Define custom metrics
ai_operations_counter = create_counter(
    name="ai_operations_total",
    description="Total number of AI operations performed",
    unit="1"
)

ai_operation_duration = create_histogram(
    name="ai_operation_duration_seconds",
    description="Duration of AI operations in seconds",
    unit="s"
)

pdf_processing_counter = create_counter(
    name="pdf_processing_total",
    description="Total number of PDF processing operations",
    unit="1"
)

pdf_processing_duration = create_histogram(
    name="pdf_processing_duration_seconds",
    description="Duration of PDF processing operations in seconds",
    unit="s"
)

ocr_operations_counter = create_counter(
    name="ocr_operations_total",
    description="Total number of OCR operations performed",
    unit="1"
)

ocr_operation_duration = create_histogram(
    name="ocr_operation_duration_seconds",
    description="Duration of OCR operations in seconds",
    unit="s"
)

document_search_counter = create_counter(
    name="document_search_total",
    description="Total number of document search operations",
    unit="1"
)

document_search_duration = create_histogram(
    name="document_search_duration_seconds",
    description="Duration of document search operations in seconds",
    unit="s"
)

search_results_gauge = create_gauge(
    name="search_results_count",
    description="Number of search results returned",
    unit="1"
)

pdf_text_extraction_counter = create_counter(
    name="pdf_text_extraction_total",
    description="Total number of PDF text extractions",
    unit="1"
)

pdf_text_extraction_duration = create_histogram(
    name="pdf_text_extraction_duration_seconds",
    description="Duration of PDF text extraction in seconds",
    unit="s"
)

keyword_extraction_counter = create_counter(
    name="keyword_extraction_total",
    description="Total number of keyword extractions",
    unit="1"
)

keyword_extraction_duration = create_histogram(
    name="keyword_extraction_duration_seconds",
    description="Duration of keyword extraction in seconds",
    unit="s"
)

def trace_ai_operation(operation_name: str, **attributes):
    """Decorator to trace AI operations with metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Prepare span attributes
            span_attributes = {
                "code.function": func.__name__,
                "code.filepath": func.__code__.co_filename,
                "code.lineno": func.__code__.co_firstlineno,
                **attributes
            }
            
            # Add semantic conventions if available
            if SpanAttributes:
                span_attributes.update({
                    SpanAttributes.CODE_FUNCTION: func.__name__,
                    SpanAttributes.CODE_FILEPATH: func.__code__.co_filename,
                    SpanAttributes.CODE_LINENO: func.__code__.co_firstlineno,
                })
            
            with tracer.start_as_current_span(
                f"ai.{operation_name}",
                attributes=span_attributes
            ) as span:
                try:
                    # Record operation start
                    ai_operations_counter.add(1, {
                        "operation": operation_name,
                        "status": "started"
                    })
                    
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Record success metrics
                    duration = time.time() - start_time
                    ai_operation_duration.record(duration, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    ai_operations_counter.add(1, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    # Add result attributes to span
                    if isinstance(result, dict):
                        for key, value in result.items():
                            if isinstance(value, (str, int, float, bool)):
                                span.set_attribute(f"result.{key}", value)
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    # Record error metrics
                    duration = time.time() - start_time
                    ai_operation_duration.record(duration, {
                        "operation": operation_name,
                        "status": "error"
                    })
                    
                    ai_operations_counter.add(1, {
                        "operation": operation_name,
                        "status": "error",
                        "error_type": type(e).__name__
                    })
                    
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    logger.error(f"AI operation {operation_name} failed: {e}")
                    raise
        
        return wrapper
    return decorator

def trace_pdf_processing(operation_name: str, **attributes):
    """Decorator to trace PDF processing operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            span_attributes = {
                "code.function": func.__name__,
                **attributes
            }
            
            if SpanAttributes:
                span_attributes[SpanAttributes.CODE_FUNCTION] = func.__name__
            
            with tracer.start_as_current_span(
                f"pdf.{operation_name}",
                attributes=span_attributes
            ) as span:
                try:
                    pdf_processing_counter.add(1, {
                        "operation": operation_name,
                        "status": "started"
                    })
                    
                    result = func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    pdf_processing_duration.record(duration, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    pdf_processing_counter.add(1, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    # Add file-specific attributes
                    if 'file_path' in kwargs:
                        span.set_attribute("file.path", kwargs['file_path'])
                    if 'file_size' in kwargs:
                        span.set_attribute("file.size", kwargs['file_size'])
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    pdf_processing_duration.record(duration, {
                        "operation": operation_name,
                        "status": "error"
                    })
                    
                    pdf_processing_counter.add(1, {
                        "operation": operation_name,
                        "status": "error",
                        "error_type": type(e).__name__
                    })
                    
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    logger.error(f"PDF processing {operation_name} failed: {e}")
                    raise
        
        return wrapper
    return decorator

def trace_ocr_operation(operation_name: str, **attributes):
    """Decorator to trace OCR operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            span_attributes = {
                "code.function": func.__name__,
                **attributes
            }
            
            if SpanAttributes:
                span_attributes[SpanAttributes.CODE_FUNCTION] = func.__name__
            
            with tracer.start_as_current_span(
                f"ocr.{operation_name}",
                attributes=span_attributes
            ) as span:
                try:
                    ocr_operations_counter.add(1, {
                        "operation": operation_name,
                        "status": "started"
                    })
                    
                    result = func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    ocr_operation_duration.record(duration, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    ocr_operations_counter.add(1, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    # Add OCR-specific attributes
                    if isinstance(result, str):
                        span.set_attribute("ocr.text_length", len(result))
                        span.set_attribute("ocr.has_text", len(result) > 0)
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    ocr_operation_duration.record(duration, {
                        "operation": operation_name,
                        "status": "error"
                    })
                    
                    ocr_operations_counter.add(1, {
                        "operation": operation_name,
                        "status": "error",
                        "error_type": type(e).__name__
                    })
                    
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    logger.error(f"OCR operation {operation_name} failed: {e}")
                    raise
        
        return wrapper
    return decorator

def trace_document_search(operation_name: str, **attributes):
    """Decorator to trace document search operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            span_attributes = {
                "code.function": func.__name__,
                **attributes
            }
            
            if SpanAttributes:
                span_attributes[SpanAttributes.CODE_FUNCTION] = func.__name__
            
            with tracer.start_as_current_span(
                f"search.{operation_name}",
                attributes=span_attributes
            ) as span:
                try:
                    document_search_counter.add(1, {
                        "operation": operation_name,
                        "status": "started"
                    })
                    
                    result = func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    document_search_duration.record(duration, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    document_search_counter.add(1, {
                        "operation": operation_name,
                        "status": "success"
                    })
                    
                    # Add search-specific attributes
                    if 'query' in kwargs:
                        span.set_attribute("search.query", kwargs['query'])
                        span.set_attribute("search.query_length", len(kwargs['query']))
                    
                    if isinstance(result, (list, tuple)):
                        search_results_gauge.set(len(result), {
                            "operation": operation_name
                        })
                        span.set_attribute("search.results_count", len(result))
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    document_search_duration.record(duration, {
                        "operation": operation_name,
                        "status": "error"
                    })
                    
                    document_search_counter.add(1, {
                        "operation": operation_name,
                        "status": "error",
                        "error_type": type(e).__name__
                    })
                    
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    logger.error(f"Document search {operation_name} failed: {e}")
                    raise
        
        return wrapper
    return decorator

class DocumentSearchMetrics:
    """Centralized metrics collection for document search operations"""
    
    def __init__(self):
        self.tracer = get_tracer(__name__)
        self.meter = get_meter(__name__)
    
    def record_search_query(self, query: str, results_count: int, duration: float, 
                          user_id: Optional[str] = None, folder_id: Optional[int] = None):
        """Record metrics for a search query"""
        with self.tracer.start_as_current_span("search.query") as span:
            span.set_attribute("search.query", query)
            span.set_attribute("search.results_count", results_count)
            span.set_attribute("search.duration", duration)
            
            if user_id:
                span.set_attribute("user.id", user_id)
            if folder_id:
                span.set_attribute("folder.id", folder_id)
            
            # Record metrics
            document_search_counter.add(1, {
                "query_length": len(query),
                "results_count": results_count,
                "user_id": user_id or "anonymous"
            })
            
            document_search_duration.record(duration, {
                "query_length": len(query),
                "results_count": results_count
            })
            
            search_results_gauge.set(results_count, {
                "query_length": len(query)
            })
    
    def record_pdf_upload(self, file_name: str, file_size: int, processing_time: float, 
                         success: bool, user_id: Optional[str] = None):
        """Record metrics for PDF upload and processing"""
        with self.tracer.start_as_current_span("pdf.upload") as span:
            span.set_attribute("file.name", file_name)
            span.set_attribute("file.size", file_size)
            span.set_attribute("processing.time", processing_time)
            span.set_attribute("success", success)
            
            if user_id:
                span.set_attribute("user.id", user_id)
            
            pdf_processing_counter.add(1, {
                "operation": "upload",
                "file_size": file_size,
                "success": success,
                "user_id": user_id or "anonymous"
            })
            
            pdf_processing_duration.record(processing_time, {
                "operation": "upload",
                "file_size": file_size,
                "success": success
            })
    
    def record_ai_operation(self, operation: str, model: str, tokens_used: int, 
                          duration: float, success: bool, cost: Optional[float] = None):
        """Record metrics for AI operations"""
        with self.tracer.start_as_current_span("ai.operation") as span:
            span.set_attribute("ai.operation", operation)
            span.set_attribute("ai.model", model)
            span.set_attribute("ai.tokens_used", tokens_used)
            span.set_attribute("ai.duration", duration)
            span.set_attribute("ai.success", success)
            
            if cost:
                span.set_attribute("ai.cost", cost)
            
            ai_operations_counter.add(1, {
                "operation": operation,
                "model": model,
                "tokens_used": tokens_used,
                "success": success
            })
            
            ai_operation_duration.record(duration, {
                "operation": operation,
                "model": model,
                "success": success
            })

# Global metrics instance
search_metrics = DocumentSearchMetrics()

# Convenience functions for common operations
def trace_openai_call(func):
    """Decorator specifically for OpenAI API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        with tracer.start_as_current_span("openai.api_call") as span:
            try:
                # Extract model and operation info
                model = kwargs.get('model', 'unknown')
                operation = func.__name__
                
                span.set_attribute("openai.model", model)
                span.set_attribute("openai.operation", operation)
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                
                # Extract usage information if available
                if hasattr(result, 'usage'):
                    tokens_used = result.usage.total_tokens
                    span.set_attribute("openai.tokens_used", tokens_used)
                    span.set_attribute("openai.prompt_tokens", result.usage.prompt_tokens)
                    span.set_attribute("openai.completion_tokens", result.usage.completion_tokens)
                    
                    # Record AI metrics
                    search_metrics.record_ai_operation(
                        operation=operation,
                        model=model,
                        tokens_used=tokens_used,
                        duration=duration,
                        success=True
                    )
                
                span.set_status(Status(StatusCode.OK))
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                # Record failed AI operation
                search_metrics.record_ai_operation(
                    operation=func.__name__,
                    model=kwargs.get('model', 'unknown'),
                    tokens_used=0,
                    duration=duration,
                    success=False
                )
                
                logger.error(f"OpenAI API call failed: {e}")
                raise
        
        return wrapper
    return wrapper

def trace_database_operation(operation_name: str):
    """Decorator for database operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"db.{operation_name}") as span:
                try:
                    span.set_attribute("db.operation", operation_name)
                    span.set_attribute("db.system", "postgresql")
                    
                    result = func(*args, **kwargs)
                    
                    if isinstance(result, (list, tuple)):
                        span.set_attribute("db.rows_affected", len(result))
                    elif hasattr(result, 'count'):
                        span.set_attribute("db.rows_affected", result.count())
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    span.set_attribute("error", True)
                    span.set_attribute("error.message", str(e))
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    logger.error(f"Database operation {operation_name} failed: {e}")
                    raise
        
        return wrapper
    return decorator
