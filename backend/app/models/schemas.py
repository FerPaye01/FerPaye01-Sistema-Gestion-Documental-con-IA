"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


class DocumentoMetadata(BaseModel):
    """Metadatos extraídos por Gemini LLM"""
    tipo_documento: Optional[str] = None
    tema_principal: Optional[str] = None
    fecha_documento: Optional[date] = None
    entidades_clave: Optional[List[str]] = None
    resumen_corto: Optional[str] = None
    
    @field_validator('tipo_documento')
    @classmethod
    def validate_tipo_documento(cls, v: Optional[str]) -> Optional[str]:
        """Validar que el tipo de documento esté en las categorías permitidas"""
        if v is None:
            return v
        
        allowed_categories = [
            'Oficio', 'Oficio Múltiple', 'Resolución Directorial', 
            'Informe', 'Solicitud', 'Memorándum', 'Acta', 'Varios'
        ]
        
        if v not in allowed_categories:
            raise ValueError(f'tipo_documento must be one of {allowed_categories}')
        return v


class DocumentoCreate(BaseModel):
    """Schema para crear un nuevo documento"""
    filename: str = Field(..., min_length=1, max_length=255)
    minio_url: str = Field(..., min_length=1)
    minio_object_name: str = Field(..., min_length=1, max_length=500)
    file_size_bytes: int = Field(..., gt=0)
    content_type: str = Field(..., min_length=1, max_length=50)
    num_pages: Optional[int] = Field(None, ge=1)
    created_by: Optional[str] = Field(None, max_length=100)
    metadata: DocumentoMetadata
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """Validar que el content_type sea PDF o JPG"""
        allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg']
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of {allowed_types}')
        return v
    
    @field_validator('file_size_bytes')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validar que el tamaño no exceda 50MB"""
        max_size = 50 * 1024 * 1024  # 50MB en bytes
        if v > max_size:
            raise ValueError(f'File size must not exceed {max_size} bytes (50MB)')
        return v


class DocumentoResponse(BaseModel):
    """Schema para respuesta de documento"""
    id: UUID
    filename: str
    minio_url: str
    tipo_documento: Optional[str] = None
    tema_principal: Optional[str] = None
    fecha_documento: Optional[date] = None
    entidades_clave: Optional[List[str]] = None
    resumen_corto: Optional[str] = None
    file_size_bytes: int
    content_type: str
    num_pages: Optional[int] = None
    upload_timestamp: datetime
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentoUpdate(BaseModel):
    """Schema para actualizar un documento existente"""
    tipo_documento: Optional[str] = None
    tema_principal: Optional[str] = None
    fecha_documento: Optional[date] = None
    entidades_clave: Optional[List[str]] = None
    resumen_corto: Optional[str] = None
    
    @field_validator('tipo_documento')
    @classmethod
    def validate_tipo_documento(cls, v: Optional[str]) -> Optional[str]:
        """Validar que el tipo de documento esté en las categorías permitidas"""
        if v is None or v == "":
            return None
        
        allowed_categories = [
            'Oficio', 'Oficio Múltiple', 'Resolución Directorial', 
            'Informe', 'Solicitud', 'Memorándum', 'Acta', 'Varios'
        ]
        
        if v not in allowed_categories:
            raise ValueError(f'tipo_documento must be one of {allowed_categories}')
        return v
    
    @field_validator('tema_principal')
    @classmethod
    def validate_tema_principal(cls, v: Optional[str]) -> Optional[str]:
        """Convertir strings vacíos a None"""
        if v == "":
            return None
        return v
    
    @field_validator('fecha_documento', mode='before')
    @classmethod
    def validate_fecha_documento(cls, v) -> Optional[date]:
        """Convertir strings vacíos a None y parsear fechas válidas"""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            try:
                from datetime import datetime
                return datetime.fromisoformat(v).date()
            except ValueError:
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v
    
    @field_validator('resumen_corto')
    @classmethod
    def validate_resumen_corto(cls, v: Optional[str]) -> Optional[str]:
        """Convertir strings vacíos a None"""
        if v == "":
            return None
        return v


class SearchFilters(BaseModel):
    """Filtros opcionales para búsqueda"""
    tipo_documento: Optional[str] = Field(None, max_length=100)
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    
    @field_validator('fecha_hasta')
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        """Validar que fecha_hasta sea posterior a fecha_desde"""
        if v is not None and 'fecha_desde' in info.data:
            fecha_desde = info.data.get('fecha_desde')
            if fecha_desde and v < fecha_desde:
                raise ValueError('fecha_hasta must be greater than or equal to fecha_desde')
        return v


class SearchRequest(BaseModel):
    """Schema para solicitud de búsqueda semántica"""
    query: str = Field(..., min_length=3, max_length=500)
    filters: Optional[SearchFilters] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    """Resultado individual de búsqueda con score de relevancia"""
    documento: DocumentoResponse
    relevance_score: float = Field(..., ge=0.0, le=2.0)  # Distancia de coseno (0-2, más bajo = más similar)


class SearchResponse(BaseModel):
    """Schema para respuesta de búsqueda"""
    results: List[SearchResult]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    total_pages: int = Field(..., ge=0)


class TaskStatusResponse(BaseModel):
    """Schema para respuesta de estado de tarea"""
    task_id: str
    status: str  # processing, completed, error
    progress: Optional[int] = Field(None, ge=0, le=100)
    stage: Optional[str] = None  # Descripción de la etapa actual
    documento_id: Optional[UUID] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    """Schema para respuesta de upload"""
    task_id: str
    status: str
    message: str


class AuditLogEntry(BaseModel):
    """Schema para entrada de auditoría"""
    id: UUID
    documento_id: UUID
    action: str  # 'CREATE', 'UPDATE', 'DELETE'
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """Schema para respuesta de historial de auditoría"""
    entries: List[AuditLogEntry]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    total_pages: int = Field(..., ge=0)
