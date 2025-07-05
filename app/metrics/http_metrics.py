from prometheus_client import Histogram

# HTTP request/response size metrics (prefixed to avoid collisions)
REQUEST_SIZE_BYTES = Histogram(
    'fastapi_http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)
RESPONSE_SIZE_BYTES = Histogram(
    'fastapi_http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)
