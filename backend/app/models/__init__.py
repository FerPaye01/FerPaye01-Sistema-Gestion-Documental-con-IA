"""
Models package
Exports all SQLAlchemy ORM models and Pydantic schemas
"""
from app.models.base import Base
from app.models.documento import Documento, Fragmento, AuditLog
from app.models.schemas import (
    DocumentoMetadata,
    DocumentoCreate,
    DocumentoUpdate,
    DocumentoResponse,
    SearchFilters,
    SearchRequest,
    SearchResult,
    SearchResponse,
    TaskStatusResponse,
    UploadResponse,
    AuditLogEntry,
    AuditLogResponse
)

__all__ = [
    'Base',
    'Documento',
    'Fragmento',
    'AuditLog',
    'DocumentoMetadata',
    'DocumentoCreate',
    'DocumentoUpdate',
    'DocumentoResponse',
    'SearchFilters',
    'SearchRequest',
    'SearchResult',
    'SearchResponse',
    'TaskStatusResponse',
    'UploadResponse',
    'AuditLogEntry',
    'AuditLogResponse'
]
