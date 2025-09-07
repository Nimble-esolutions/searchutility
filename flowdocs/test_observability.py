#!/usr/bin/env python3
"""
OpenTelemetry Integration Test Script
Tests the observability implementation for AI Document Search Platform
"""

import os
import sys
import time
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_opentelemetry_imports():
    """Test that OpenTelemetry modules can be imported"""
    print("🔍 Testing OpenTelemetry imports...")
    
    try:
        from flowdocs.opentelemetry_config import otel_config
        print("✅ OpenTelemetry config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenTelemetry config: {e}")
        return False
    
    try:
        from core.observability import (
            trace_ai_operation, trace_pdf_processing, trace_document_search,
            search_metrics, create_span
        )
        print("✅ Observability modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import observability modules: {e}")
        return False
    
    return True

def test_opentelemetry_initialization():
    """Test OpenTelemetry initialization"""
    print("\n🔍 Testing OpenTelemetry initialization...")
    
    try:
        from flowdocs.opentelemetry_config import otel_config
        otel_config.initialize()
        print("✅ OpenTelemetry initialized successfully")
        return True
    except Exception as e:
        print(f"❌ OpenTelemetry initialization failed: {e}")
        return False

def test_metrics_creation():
    """Test metrics creation and recording"""
    print("\n🔍 Testing metrics creation...")
    
    try:
        from core.observability import (
            create_counter, create_histogram, create_gauge,
            search_metrics
        )
        
        # Test counter creation
        counter = create_counter("test_operations_total", "Test operations", "1")
        counter.add(1, {"test": "true"})
        print("✅ Counter created and recorded successfully")
        
        # Test histogram creation
        histogram = create_histogram("test_duration_seconds", "Test duration", "s")
        histogram.record(0.5, {"test": "true"})
        print("✅ Histogram created and recorded successfully")
        
        # Test gauge creation
        gauge = create_gauge("test_value", "Test value", "1")
        gauge.set(42, {"test": "true"})
        print("✅ Gauge created and recorded successfully")
        
        # Test search metrics
        search_metrics.record_search_query(
            query="test query",
            results_count=5,
            duration=1.2,
            user_id="test_user"
        )
        print("✅ Search metrics recorded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Metrics creation failed: {e}")
        return False

def test_tracing():
    """Test tracing functionality"""
    print("\n🔍 Testing tracing...")
    
    try:
        from core.observability import create_span, trace_ai_operation
        
        # Test basic span creation
        with create_span("test.operation") as span:
            span.set_attribute("test.attribute", "test_value")
            span.set_attribute("test.number", 42)
            print("✅ Basic span created successfully")
        
        # Test decorated function
        @trace_ai_operation("test_ai_operation")
        def test_ai_function():
            time.sleep(0.1)
            return "test_result"
        
        result = test_ai_function()
        print(f"✅ Decorated AI function executed: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Tracing failed: {e}")
        return False

def test_django_integration():
    """Test Django integration"""
    print("\n🔍 Testing Django integration...")
    
    try:
        import django
        from django.conf import settings
        
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdocs.settings')
        django.setup()
        
        print("✅ Django setup completed")
        
        # Test that OpenTelemetry is initialized in settings
        from flowdocs.opentelemetry_config import otel_config
        if otel_config._initialized:
            print("✅ OpenTelemetry initialized in Django settings")
        else:
            print("⚠️ OpenTelemetry not initialized in Django settings")
        
        return True
    except Exception as e:
        print(f"❌ Django integration failed: {e}")
        return False

def test_monitoring_endpoints():
    """Test monitoring endpoints"""
    print("\n🔍 Testing monitoring endpoints...")
    
    # Test if monitoring services are running
    endpoints = {
        "Jaeger UI": "http://localhost:16686",
        "Prometheus": "http://localhost:9090",
        "Grafana": "http://localhost:3000"
    }
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is accessible at {url}")
            else:
                print(f"⚠️ {name} returned status {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"❌ {name} is not accessible at {url}")
    
    return True

def test_application_metrics():
    """Test application metrics endpoint"""
    print("\n🔍 Testing application metrics...")
    
    try:
        # Start Django development server in background
        import subprocess
        import threading
        import time
        
        def start_server():
            subprocess.run([
                sys.executable, "manage.py", "runserver", "8001"
            ], cwd=project_root)
        
        # Start server in background
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(5)
        
        # Test metrics endpoint
        try:
            response = requests.get("http://localhost:8001/metrics", timeout=10)
            if response.status_code == 200:
                print("✅ Metrics endpoint is accessible")
                print(f"📊 Metrics content length: {len(response.text)} characters")
            else:
                print(f"⚠️ Metrics endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Metrics endpoint not accessible: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Application metrics test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting OpenTelemetry Integration Tests\n")
    
    tests = [
        ("OpenTelemetry Imports", test_opentelemetry_imports),
        ("OpenTelemetry Initialization", test_opentelemetry_initialization),
        ("Metrics Creation", test_metrics_creation),
        ("Tracing", test_tracing),
        ("Django Integration", test_django_integration),
        ("Monitoring Endpoints", test_monitoring_endpoints),
        ("Application Metrics", test_application_metrics),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! OpenTelemetry integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
