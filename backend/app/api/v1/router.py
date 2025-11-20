"""
API v1 router aggregation
"""
from fastapi import APIRouter
from app.api.v1.endpoints import documentos

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(documentos.router)
