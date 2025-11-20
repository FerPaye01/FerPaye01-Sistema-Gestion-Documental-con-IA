from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session
import structlog
import redis
from minio import Minio
from datetime import datetime

from app.api.v1.router import api_router
from app.database import get_db, engine
from app.config import settings
from app.workers.celery_app import celery_app

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

app = FastAPI(
    title="SGD UGEL Ilo API",
    description="Sistema de Gestión Documental Inteligente para UGEL Ilo",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with structured response"""
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors()
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with structured logging"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "sgd-ugel-api"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service dependencies"""
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "minio": check_minio(),
        "celery": check_celery_workers()
    }
    
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "service": "sgd-ugel-api",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    )


def check_database() -> bool:
    """Check PostgreSQL connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("database_health_check_failed", error=str(exc))
        return False


def check_redis() -> bool:
    """Check Redis connection"""
    try:
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        return True
    except Exception as exc:
        logger.error("redis_health_check_failed", error=str(exc))
        return False


def check_minio() -> bool:
    """Check MinIO connection"""
    try:
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        # Check if bucket exists
        client.bucket_exists(settings.MINIO_BUCKET)
        return True
    except Exception as exc:
        logger.error("minio_health_check_failed", error=str(exc))
        return False


def check_celery_workers() -> bool:
    """Check if Celery workers are active"""
    try:
        # Get active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        return active_workers is not None and len(active_workers) > 0
    except Exception as exc:
        logger.error("celery_health_check_failed", error=str(exc))
        return False


@app.on_event("startup")
async def startup_event():
    logger.info("application_startup", service="sgd-ugel-api")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("application_shutdown", service="sgd-ugel-api")
