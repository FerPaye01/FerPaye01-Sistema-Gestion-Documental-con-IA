"""
SQLAlchemy ORM models for documentos, fragmentos, and audit_log
"""
from sqlalchemy import Column, String, Text, BigInteger, Integer, Date, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from pgvector.sqlalchemy import Vector

from app.models.base import Base


class Documento(Base):
    """
    Modelo ORM para la tabla documentos
    Almacena metadatos de documentos procesados
    """
    __tablename__ = 'documentos'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Información del archivo
    filename = Column(String(255), nullable=False)
    minio_url = Column(Text, nullable=False)
    minio_object_name = Column(String(500), nullable=False)
    
    # Metadatos extraídos por Gemini
    tipo_documento = Column(String(100), nullable=True)
    tema_principal = Column(Text, nullable=True)
    fecha_documento = Column(Date, nullable=True)
    entidades_clave = Column(ARRAY(Text), nullable=True)
    resumen_corto = Column(Text, nullable=True)
    
    # Metadatos del sistema
    file_size_bytes = Column(BigInteger, nullable=False)
    content_type = Column(String(50), nullable=False)
    num_pages = Column(Integer, nullable=True)
    
    # Timestamps y estado extendidos
    upload_timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(TIMESTAMP, nullable=True)
    created_by = Column(String(100), nullable=True)
    status = Column(String(20), server_default='processing', nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Constraints para validar status y categorías
    __table_args__ = (
        CheckConstraint("status IN ('processing', 'completed', 'error')", name='valid_status'),
        CheckConstraint(
            "tipo_documento IN ('Oficio', 'Oficio Múltiple', 'Resolución Directorial', 'Informe', 'Solicitud', 'Memorándum', 'Acta', 'Varios') OR tipo_documento IS NULL",
            name='valid_tipo_documento'
        ),
    )
    
    # Relaciones
    fragmentos = relationship(
        "Fragmento",
        back_populates="documento",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    audit_entries = relationship(
        "AuditLog",
        back_populates="documento",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    def __repr__(self):
        return f"<Documento(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class Fragmento(Base):
    """
    Modelo ORM para la tabla fragmentos
    Almacena fragmentos de texto con sus embeddings para búsqueda vectorial
    """
    __tablename__ = 'fragmentos'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key a documentos (ON DELETE CASCADE)
    documento_id = Column(
        UUID(as_uuid=True),
        ForeignKey('documentos.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Contenido del fragmento
    texto = Column(Text, nullable=False)
    posicion = Column(Integer, nullable=False)  # Orden del fragmento en el documento
    
    # Vector de embedding (768 dimensiones para text-embedding-004)
    embedding = Column(Vector(768), nullable=False)
    
    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relación con documento
    documento = relationship("Documento", back_populates="fragmentos")
    
    def __repr__(self):
        return f"<Fragmento(id={self.id}, documento_id={self.documento_id}, posicion={self.posicion})>"


class AuditLog(Base):
    """
    Modelo ORM para la tabla audit_log
    Almacena el historial de cambios en documentos para trazabilidad
    """
    __tablename__ = 'audit_log'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key a documentos (ON DELETE CASCADE)
    documento_id = Column(
        UUID(as_uuid=True),
        ForeignKey('documentos.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Información de la acción
    action = Column(String(20), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE'
    old_values = Column(JSONB, nullable=True)  # Valores anteriores (para UPDATE/DELETE)
    new_values = Column(JSONB, nullable=True)  # Valores nuevos (para CREATE/UPDATE)
    user_id = Column(String(100), nullable=True)  # Usuario que realizó la acción
    
    # Timestamp
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    
    # Constraint para validar action
    __table_args__ = (
        CheckConstraint("action IN ('CREATE', 'UPDATE', 'DELETE')", name='valid_audit_action'),
    )
    
    # Relación con documento
    documento = relationship("Documento", back_populates="audit_entries")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, documento_id={self.documento_id}, action='{self.action}')>"
