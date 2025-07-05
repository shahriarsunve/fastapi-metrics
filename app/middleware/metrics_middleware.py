import time
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.metrics.http_metrics import REQUEST_SIZE_BYTES, RESPONSE_SIZE_BYTES

# Counter: total number of HTTP requests (prefixed)
REQUEST_COUNT = Counter(
    'fastapi_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Histogram: request duration in seconds (prefixed)
REQUEST_LATENCY = Histogram(
    'fastapi_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        elapsed = time.time() - start_time

        method = request.method
        endpoint = request.url.path
        status_code = str(response.status_code)

        # Request size
        try:
            req_size = int(request.headers.get('content-length', 0))
        except (TypeError, ValueError):
            req_size = 0
        REQUEST_SIZE_BYTES.labels(method=method, endpoint=endpoint).observe(req_size)

        # Response size
        try:
            body = response.body if hasattr(response, 'body') else b''.join(response.body_iterator)
            resp_size = len(body)
        except Exception:
            resp_size = 0
        RESPONSE_SIZE_BYTES.labels(method=method, endpoint=endpoint).observe(resp_size)

        # Core metrics
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)

        return response
