from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# definemetrics
requests_total = Counter(
    'llm_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

requests_in_progress = Gauge(
    'llm_requests_in_progress',
    'Number of requests currently being processed'
)

request_duration = Histogram(
    'llm_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

generation_tokens = Histogram(
    'llm_generation_tokens',
    'Number of tokens generated',
    buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000]
)

generation_latency = Histogram(
    'llm_generation_latency_seconds',
    'Time to first token and total generation time',
    ['metric_type'],  # 'ttft' or 'total'
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

engine_errors = Counter(
    'llm_engine_errors_total',
    'Total number of engine errors',
    ['error_type']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """collects HTTP request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        # skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        path = request.url.path
        
        # start timer and increment in-progress counter
        start_time = time.time()
        requests_in_progress.inc()
        
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            engine_errors.labels(error_type=type(e).__name__).inc()
            raise
        finally:
            # record metrics
            duration = time.time() - start_time
            requests_in_progress.dec()
            requests_total.labels(method=method, endpoint=path, status=status).inc()
            request_duration.labels(method=method, endpoint=path).observe(duration)
        
        return response

def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def record_generation_metrics(tokens: int, ttft: float, total_time: float):
    """record generation metrics"""
    generation_tokens.observe(tokens)
    generation_latency.labels(metric_type="ttft").observe(ttft)
    generation_latency.labels(metric_type="total").observe(total_time)