"""API Router aggregating v1 endpoints."""
from fastapi import APIRouter
from backend.app.api.v1.endpoints import predict, analytics, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(predict.router, tags=["Inference"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Intelligence"])
