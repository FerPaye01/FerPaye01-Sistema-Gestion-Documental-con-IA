"""
Servicio de auditoría para el Sistema de Gestión Documental (SGD)

Este servicio maneja el logging automático de todas las operaciones CRUD
y proporciona funcionalidades para consultar el historial de cambios.
"""
import structlog
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from uuid import UUID

from app.models.documento import AuditLog, Documento
from app.models.schemas import AuditLogEntry, AuditLogResponse

logger = structlog.get_logger()


class AuditService:
    """
    Servicio para gestión de auditoría y logging de operaciones CRUD.
    
    Responsabilidades:
    - Registrar automáticamente todas las operaciones CRUD
    - Proporcionar consultas de historial de cambios
    - Mantener integridad de registros de auditoría
    """
    
    def __init__(self, db: Session):
        """
        Inicializar el servicio de auditoría.
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def log_create(
        self,
        documento_id: UUID,
        new_values: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AuditLog:
        """
        Registrar la creación de un documento.
        
        Args:
            documento_id: ID del documento creado
            new_values: Valores del documento creado
            user_id: ID del usuario que realizó la acción
        
        Returns:
            Entrada de auditoría creada
        """
        try:
            audit_entry = AuditLog(
                documento_id=documento_id,
                action='CREATE',
                old_values=None,
                new_values=new_values,
                user_id=user_id or 'system'
            )
            
            self.db.add(audit_entry)
            self.db.flush()  # Obtener el ID sin hacer commit
            
            logger.info(
                "audit_create_logged",
                documento_id=str(documento_id),
                user_id=user_id,
                audit_id=str(audit_entry.id)
            )
            
            return audit_entry
            
        except Exception as exc:
            logger.error(
                "audit_create_logging_failed",
                documento_id=str(documento_id),
                user_id=user_id,
                error=str(exc)
            )
            raise
    
    def log_update(
        self,
        documento_id: UUID,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AuditLog:
        """
        Registrar la actualización de un documento.
        
        Args:
            documento_id: ID del documento actualizado
            old_values: Valores anteriores del documento
            new_values: Valores nuevos del documento
            user_id: ID del usuario que realizó la acción
        
        Returns:
            Entrada de auditoría creada
        """
        try:
            audit_entry = AuditLog(
                documento_id=documento_id,
                action='UPDATE',
                old_values=old_values,
                new_values=new_values,
                user_id=user_id or 'system'
            )
            
            self.db.add(audit_entry)
            self.db.flush()  # Obtener el ID sin hacer commit
            
            logger.info(
                "audit_update_logged",
                documento_id=str(documento_id),
                user_id=user_id,
                audit_id=str(audit_entry.id),
                changed_fields=list(self._get_changed_fields(old_values, new_values))
            )
            
            return audit_entry
            
        except Exception as exc:
            logger.error(
                "audit_update_logging_failed",
                documento_id=str(documento_id),
                user_id=user_id,
                error=str(exc)
            )
            raise
    
    def log_delete(
        self,
        documento_id: UUID,
        old_values: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> AuditLog:
        """
        Registrar la eliminación de un documento.
        
        Args:
            documento_id: ID del documento eliminado
            old_values: Valores del documento antes de eliminar
            user_id: ID del usuario que realizó la acción
        
        Returns:
            Entrada de auditoría creada
        """
        try:
            audit_entry = AuditLog(
                documento_id=documento_id,
                action='DELETE',
                old_values=old_values,
                new_values=None,
                user_id=user_id or 'system'
            )
            
            self.db.add(audit_entry)
            self.db.flush()  # Obtener el ID sin hacer commit
            
            logger.info(
                "audit_delete_logged",
                documento_id=str(documento_id),
                user_id=user_id,
                audit_id=str(audit_entry.id)
            )
            
            return audit_entry
            
        except Exception as exc:
            logger.error(
                "audit_delete_logging_failed",
                documento_id=str(documento_id),
                user_id=user_id,
                error=str(exc)
            )
            raise
    
    def get_document_history(
        self,
        documento_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> AuditLogResponse:
        """
        Obtener el historial de cambios de un documento específico.
        
        Args:
            documento_id: ID del documento
            page: Número de página (empezando en 1)
            page_size: Tamaño de página (máximo 100)
        
        Returns:
            Respuesta con historial paginado de auditoría
        """
        try:
            # Validar parámetros de paginación
            page = max(1, page)
            page_size = min(100, max(1, page_size))
            
            # Consultar entradas de auditoría ordenadas por timestamp descendente
            query = self.db.query(AuditLog).filter(
                AuditLog.documento_id == documento_id
            ).order_by(desc(AuditLog.timestamp))
            
            # Contar total de entradas
            total = query.count()
            
            # Aplicar paginación
            offset = (page - 1) * page_size
            entries = query.offset(offset).limit(page_size).all()
            
            # Calcular total de páginas
            total_pages = (total + page_size - 1) // page_size
            
            # Convertir a schemas de respuesta
            audit_entries = [
                AuditLogEntry.model_validate(entry) for entry in entries
            ]
            
            logger.info(
                "document_history_retrieved",
                documento_id=str(documento_id),
                total_entries=total,
                page=page,
                page_size=page_size
            )
            
            return AuditLogResponse(
                entries=audit_entries,
                total=total,
                page=page,
                total_pages=total_pages
            )
            
        except Exception as exc:
            logger.error(
                "document_history_retrieval_failed",
                documento_id=str(documento_id),
                page=page,
                page_size=page_size,
                error=str(exc)
            )
            raise
    
    def get_all_audit_history(
        self,
        page: int = 1,
        page_size: int = 20,
        action_filter: Optional[str] = None,
        user_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> AuditLogResponse:
        """
        Obtener historial completo de auditoría con filtros opcionales.
        
        Args:
            page: Número de página (empezando en 1)
            page_size: Tamaño de página (máximo 100)
            action_filter: Filtrar por tipo de acción ('CREATE', 'UPDATE', 'DELETE')
            user_filter: Filtrar por ID de usuario
            date_from: Fecha de inicio del rango
            date_to: Fecha de fin del rango
        
        Returns:
            Respuesta con historial paginado de auditoría
        """
        try:
            # Validar parámetros de paginación
            page = max(1, page)
            page_size = min(100, max(1, page_size))
            
            # Construir consulta base
            query = self.db.query(AuditLog)
            
            # Aplicar filtros
            if action_filter:
                valid_actions = ['CREATE', 'UPDATE', 'DELETE']
                if action_filter.upper() in valid_actions:
                    query = query.filter(AuditLog.action == action_filter.upper())
            
            if user_filter:
                query = query.filter(AuditLog.user_id == user_filter)
            
            if date_from:
                query = query.filter(AuditLog.timestamp >= date_from)
            
            if date_to:
                query = query.filter(AuditLog.timestamp <= date_to)
            
            # Ordenar por timestamp descendente
            query = query.order_by(desc(AuditLog.timestamp))
            
            # Contar total de entradas
            total = query.count()
            
            # Aplicar paginación
            offset = (page - 1) * page_size
            entries = query.offset(offset).limit(page_size).all()
            
            # Calcular total de páginas
            total_pages = (total + page_size - 1) // page_size
            
            # Convertir a schemas de respuesta
            audit_entries = [
                AuditLogEntry.model_validate(entry) for entry in entries
            ]
            
            logger.info(
                "audit_history_retrieved",
                total_entries=total,
                page=page,
                page_size=page_size,
                filters={
                    "action": action_filter,
                    "user": user_filter,
                    "date_from": date_from.isoformat() if date_from else None,
                    "date_to": date_to.isoformat() if date_to else None
                }
            )
            
            return AuditLogResponse(
                entries=audit_entries,
                total=total,
                page=page,
                total_pages=total_pages
            )
            
        except Exception as exc:
            logger.error(
                "audit_history_retrieval_failed",
                page=page,
                page_size=page_size,
                error=str(exc)
            )
            raise
    
    def _get_changed_fields(
        self,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any]
    ) -> List[str]:
        """
        Identificar los campos que cambiaron entre valores antiguos y nuevos.
        
        Args:
            old_values: Valores anteriores
            new_values: Valores nuevos
        
        Returns:
            Lista de nombres de campos que cambiaron
        """
        changed_fields = []
        
        # Obtener todas las claves únicas
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changed_fields.append(key)
        
        return changed_fields
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de auditoría del sistema.
        
        Returns:
            Diccionario con estadísticas de auditoría
        """
        try:
            # Contar entradas por acción
            action_counts = self.db.query(
                AuditLog.action,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.action).all()
            
            # Contar entradas por usuario (top 10)
            user_counts = self.db.query(
                AuditLog.user_id,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.user_id).order_by(
                desc(func.count(AuditLog.id))
            ).limit(10).all()
            
            # Contar entradas por día (últimos 30 días)
            daily_counts = self.db.query(
                func.date(AuditLog.timestamp).label('date'),
                func.count(AuditLog.id).label('count')
            ).filter(
                AuditLog.timestamp >= func.now() - func.interval('30 days')
            ).group_by(
                func.date(AuditLog.timestamp)
            ).order_by(desc('date')).all()
            
            # Total de entradas
            total_entries = self.db.query(AuditLog).count()
            
            statistics = {
                "total_entries": total_entries,
                "actions": {action: count for action, count in action_counts},
                "top_users": [
                    {"user_id": user, "count": count} 
                    for user, count in user_counts
                ],
                "daily_activity": [
                    {"date": date.isoformat(), "count": count}
                    for date, count in daily_counts
                ]
            }
            
            logger.info(
                "audit_statistics_generated",
                total_entries=total_entries,
                actions_count=len(action_counts),
                users_count=len(user_counts)
            )
            
            return statistics
            
        except Exception as exc:
            logger.error(
                "audit_statistics_generation_failed",
                error=str(exc)
            )
            raise