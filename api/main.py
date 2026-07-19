from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.pipeline import router as pipeline_router

app = FastAPI(
    title="Adaptive Intelligence Fabric API",
    description="REST API for Data Pipeline Operations Intelligence",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(pipeline_router)