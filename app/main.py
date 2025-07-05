from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
from app.middleware.metrics_middleware import MetricsMiddleware
from app.metrics.system_metrics import register_system_metrics
from app.routers import health, api

app = FastAPI(
    title="FastAPI Metrics Monitoring System",
    description="A FastAPI app exposing system and HTTP metrics in Prometheus format",
    version="1.0.0",
)

# Allow CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register system metrics collection
register_system_metrics(app)

# Metrics middleware to capture HTTP request metrics
app.add_middleware(MetricsMiddleware)

# Mount API routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api.router, prefix="/data", tags=["data"])

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to FastAPI Metrics Monitoring System"}

@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """
    Expose Prometheus metrics.
    """
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
