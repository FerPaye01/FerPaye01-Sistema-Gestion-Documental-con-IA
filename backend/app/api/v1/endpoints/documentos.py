"""
Endpoints para gestión de documentos
"""
import os
import tempfile
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import structlog
import math

from app.config import settings
from app.models.schemas import (
    UploadResponse, 
    TaskStatusResponse, 
    SearchRequest, 
    SearchResponse, 
    SearchResult,
    DocumentoResponse,
    DocumentoUpdate,
    AuditLogResponse
)
from app.models.documento import Documento, Fragmento, AuditLog
from app.database import get_db
from app.services.ai_service import AIService
from app.services.audit_service import AuditService
from app.workers.celery_app import celery_app

logger = structlog.get_logger()

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Endpoint para subir documentos (PDF o JPG).
    
    Este endpoint NO procesa el archivo de forma síncrona.
    En su lugar, crea una tarea asíncrona de Celery que ejecuta
    el flujo completo de ingestión (Flujo 1):
    
    1. Storage: Subir archivo a MinIO
    2. Text Extraction: OCR híbrido (PyMuPDF → pytesseract)
    3. Text Cleaning: Normalización y limpieza
    4. Chunking: Fragmentación con overlap
    5. Metadata Extraction: Llamada a Gemini
    6. Embedding Generation: Llamada a text-embedding-004
    7. Database Storage: Insertar en PostgreSQL
    
    Args:
        file: Archivo PDF o JPG (máx 50MB)
    
    Returns:
        HTTP 202 Accepted con task_id para seguimiento
    
    Raises:
        HTTPException 400: Si el archivo no es válido
        HTTPException 413: Si el archivo excede el tamaño máximo
    """
    try:
        # Validar tipo de archivo
        content_type = file.content_type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg']
        
        if content_type not in allowed_types:
            logger.warning(
                "invalid_file_type",
                filename=file.filename,
                content_type=content_type
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no soportado. Tipos permitidos: {', '.join(allowed_types)}"
            )
        
        # Leer archivo en memoria para validar tamaño
        file_content = await file.read()
        file_size_bytes = len(file_content)
        
        # Validar tamaño máximo (50MB)
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size_bytes > max_size_bytes:
            logger.warning(
                "file_too_large",
                filename=file.filename,
                file_size_bytes=file_size_bytes,
                max_size_bytes=max_size_bytes
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Guardar archivo temporalmente
        # Crear directorio temporal si no existe
        temp_dir = "/tmp/sgd-uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Crear archivo temporal con extensión correcta
        file_extension = ".pdf" if content_type == "application/pdf" else ".jpg"
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
            dir=temp_dir
        )
        
        try:
            # Escribir contenido al archivo temporal
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = temp_file.name
            
            logger.info(
                "file_saved_temporarily",
                filename=file.filename,
                temp_path=temp_path,
                file_size_bytes=file_size_bytes,
                content_type=content_type
            )
            
        finally:
            temp_file.close()
        
        # Encolar tarea de Celery (NO esperar resultado)
        from app.workers.tasks import process_document
        task = process_document.apply_async(
            args=[temp_path, file.filename, content_type]
        )
        
        logger.info(
            "document_processing_task_queued",
            filename=file.filename,
            task_id=task.id,
            file_size_bytes=file_size_bytes
        )
        
        # Retornar HTTP 202 Accepted con task_id
        return UploadResponse(
            task_id=task.id,
            status="processing",
            message=f"Documento '{file.filename}' encolado para procesamiento"
        )
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    
    except Exception as exc:
        logger.error(
            "upload_endpoint_error",
            filename=file.filename if file else "unknown",
            error=str(exc),
            error_type=type(exc).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la solicitud"
        )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Obtiene el estado de una tarea de procesamiento de documento.
    
    Args:
        task_id: ID de la tarea de Celery
    
    Returns:
        Estado actual de la tarea con progreso y resultado
    
    Raises:
        HTTPException 404: Si la tarea no existe
    """
    try:
        # Obtener resultado de Celery
        task_result = AsyncResult(task_id, app=celery_app)
        
        # Determinar estado
        if task_result.state == 'PENDING':
            # Tarea no encontrada o aún no iniciada
            return TaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress=0
            )
        
        elif task_result.state == 'PROGRESS':
            # Tarea en progreso
            info = task_result.info or {}
            progress = info.get('progress', 0)
            stage = info.get('stage', 'Procesando...')
            
            logger.debug(
                "task_progress_status",
                task_id=task_id,
                progress=progress,
                stage=stage,
                info=info
            )
            
            return TaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=progress,
                stage=stage
            )
        
        elif task_result.state == 'SUCCESS':
            # Tarea completada exitosamente
            documento_id = task_result.result
            return TaskStatusResponse(
                task_id=task_id,
                status="completed",
                progress=100,
                documento_id=documento_id
            )
        
        elif task_result.state == 'FAILURE':
            # Tarea falló
            error_message = str(task_result.info) if task_result.info else "Error desconocido"
            return TaskStatusResponse(
                task_id=task_id,
                status="error",
                error=error_message
            )
        
        else:
            # Estado desconocido
            return TaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower()
            )
    
    except Exception as exc:
        logger.error(
            "task_status_error",
            task_id=task_id,
            error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estado de la tarea"
        )



@router.get("/{documento_id}", response_model=DocumentoResponse)
async def get_documento(
    documento_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene un documento específico por su ID.
    
    Args:
        documento_id: ID del documento
        db: Sesión de base de datos
    
    Returns:
        Datos completos del documento
    
    Raises:
        HTTPException 404: Si el documento no existe
    """
    try:
        documento = db.query(Documento).filter(
            Documento.id == documento_id,
            Documento.status == 'completed'
        ).first()
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Generate a download URL that points to our backend endpoint
        documento_response = DocumentoResponse.model_validate(documento)
        # Replace MinIO URL with our backend download endpoint
        documento_response.minio_url = f"{settings.API_BASE_URL}/api/v1/documentos/{documento_id}/download"
        
        return documento_response
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "get_documento_error",
            documento_id=documento_id,
            error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el documento"
        )


@router.put("/{documento_id}", response_model=DocumentoResponse)
async def update_documento(
    documento_id: str,
    update_data: DocumentoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los metadatos de un documento existente.
    
    Args:
        documento_id: ID del documento a actualizar
        update_data: Datos de actualización (metadatos editables)
        db: Sesión de base de datos
    
    Returns:
        Documento actualizado con nuevos metadatos
    
    Raises:
        HTTPException 404: Si el documento no existe
        HTTPException 400: Si los datos de actualización son inválidos
    """
    try:
        # Buscar el documento existente
        documento = db.query(Documento).filter(
            Documento.id == documento_id,
            Documento.status == 'completed'
        ).first()
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Guardar valores anteriores para auditoría
        old_values = {
            "tipo_documento": documento.tipo_documento,
            "tema_principal": documento.tema_principal,
            "fecha_documento": documento.fecha_documento.isoformat() if documento.fecha_documento else None,
            "entidades_clave": documento.entidades_clave,
            "resumen_corto": documento.resumen_corto
        }
        
        # Actualizar solo los campos proporcionados (no None)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(documento, field):
                setattr(documento, field, value)
        
        # Actualizar timestamp de modificación
        documento.updated_at = func.now()
        
        # Preparar nuevos valores para auditoría
        new_values = {
            "tipo_documento": documento.tipo_documento,
            "tema_principal": documento.tema_principal,
            "fecha_documento": documento.fecha_documento.isoformat() if documento.fecha_documento else None,
            "entidades_clave": documento.entidades_clave,
            "resumen_corto": documento.resumen_corto
        }
        
        # Crear entrada de auditoría usando el servicio
        audit_service = AuditService(db)
        audit_service.log_update(
            documento_id=documento.id,
            old_values=old_values,
            new_values=new_values,
            user_id='system'  # TODO: Obtener del contexto de autenticación
        )
        
        # Confirmar cambios
        db.commit()
        db.refresh(documento)
        
        logger.info(
            "documento_updated",
            documento_id=documento_id,
            updated_fields=list(update_dict.keys()),
            user_id='system'
        )
        
        # Generar respuesta con URL de descarga actualizada
        documento_response = DocumentoResponse.model_validate(documento)
        documento_response.minio_url = f"{settings.API_BASE_URL}/api/v1/documentos/{documento_id}/download"
        
        return documento_response
        
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error(
            "update_documento_error",
            documento_id=documento_id,
            error=str(exc),
            error_type=type(exc).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el documento"
        )


@router.delete("/{documento_id}")
async def delete_documento(
    documento_id: str,
    confirm: bool = False,
    db: Session = Depends(get_db)
):
    """
    Elimina un documento de forma segura del sistema.
    
    Elimina tanto el archivo de MinIO como el registro de la base de datos.
    Requiere confirmación explícita para prevenir eliminaciones accidentales.
    
    Args:
        documento_id: ID del documento a eliminar
        confirm: Parámetro de confirmación (debe ser True)
        db: Sesión de base de datos
    
    Returns:
        Mensaje de confirmación de eliminación
    
    Raises:
        HTTPException 400: Si no se proporciona confirmación
        HTTPException 404: Si el documento no existe
        HTTPException 500: Si falla la eliminación del archivo o base de datos
    """
    try:
        # Validar confirmación
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Eliminación requiere confirmación explícita. Use confirm=true"
            )
        
        # Buscar el documento existente
        documento = db.query(Documento).filter(
            Documento.id == documento_id
        ).first()
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Guardar información del documento para auditoría
        documento_info = {
            "id": str(documento.id),
            "filename": documento.filename,
            "tipo_documento": documento.tipo_documento,
            "tema_principal": documento.tema_principal,
            "fecha_documento": documento.fecha_documento.isoformat() if documento.fecha_documento else None,
            "entidades_clave": documento.entidades_clave,
            "resumen_corto": documento.resumen_corto,
            "minio_object_name": documento.minio_object_name,
            "file_size_bytes": documento.file_size_bytes,
            "upload_timestamp": documento.upload_timestamp.isoformat(),
            "status": documento.status
        }
        
        # Crear entrada de auditoría antes de eliminar usando el servicio
        audit_service = AuditService(db)
        audit_service.log_delete(
            documento_id=documento.id,
            old_values=documento_info,
            user_id='system'  # TODO: Obtener del contexto de autenticación
        )
        
        # Eliminar archivo de MinIO
        from app.services.storage_service import StorageService
        storage_service = StorageService()
        
        try:
            # Intentar eliminar el archivo de MinIO
            storage_service.client.remove_object(
                storage_service.bucket,
                documento.minio_object_name
            )
            
            logger.info(
                "minio_file_deleted",
                documento_id=documento_id,
                object_name=documento.minio_object_name
            )
            
        except Exception as storage_exc:
            # Log el error pero continuar con la eliminación de la base de datos
            # El archivo podría no existir o haber sido eliminado previamente
            logger.warning(
                "minio_file_deletion_failed",
                documento_id=documento_id,
                object_name=documento.minio_object_name,
                error=str(storage_exc)
            )
        
        # Eliminar registro de la base de datos
        # Los fragmentos y audit_log se eliminan automáticamente por CASCADE
        db.delete(documento)
        db.commit()
        
        logger.info(
            "documento_deleted",
            documento_id=documento_id,
            filename=documento_info["filename"],
            user_id='system'
        )
        
        from datetime import datetime
        
        return {
            "message": f"Documento '{documento_info['filename']}' eliminado exitosamente",
            "documento_id": documento_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error(
            "delete_documento_error",
            documento_id=documento_id,
            error=str(exc),
            error_type=type(exc).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el documento"
        )


@router.get("/{documento_id}/download")
@router.head("/{documento_id}/download")
async def download_documento(
    documento_id: str,
    db: Session = Depends(get_db)
):
    """
    Descarga un documento específico.
    
    Args:
        documento_id: ID del documento
        db: Sesión de base de datos
    
    Returns:
        Archivo del documento
    
    Raises:
        HTTPException 404: Si el documento no existe
    """
    from fastapi.responses import StreamingResponse, Response
    from fastapi import Request
    from app.services.storage_service import StorageService
    import io
    
    try:
        documento = db.query(Documento).filter(
            Documento.id == documento_id,
            Documento.status == 'completed'
        ).first()
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Determine content type
        content_type = "application/pdf" if documento.filename.lower().endswith('.pdf') else "image/jpeg"
        
        # For HEAD requests, just return headers without body
        request = db.info.get('request')  # This won't work, let me fix it
        
        # Get file from MinIO using internal connection
        storage_service = StorageService()
        
        try:
            # Get file stats for content-length
            stat = storage_service.client.stat_object(
                storage_service.bucket,
                documento.minio_object_name
            )
            
            headers = {
                "Content-Type": content_type,
                "Content-Length": str(stat.size),
                "Content-Disposition": f"attachment; filename={documento.filename}"
            }
            
            # For HEAD requests, return just headers
            # Note: FastAPI automatically handles HEAD by returning GET response without body
            
            # Get the file data from MinIO
            response = storage_service.client.get_object(
                storage_service.bucket,
                documento.minio_object_name
            )
            
            # Create a streaming response
            def generate():
                try:
                    for chunk in response.stream(8192):
                        yield chunk
                finally:
                    response.close()
                    response.release_conn()
            
            return StreamingResponse(
                generate(),
                media_type=content_type,
                headers=headers
            )
            
        except Exception as storage_exc:
            logger.error(
                "file_download_error",
                documento_id=documento_id,
                object_name=documento.minio_object_name,
                error=str(storage_exc)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al descargar el archivo"
            )
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "download_documento_error",
            documento_id=documento_id,
            error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la descarga"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documentos(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de búsqueda semántica de documentos.
    
    Implementa búsqueda vectorial usando pgvector siguiendo Steering 2:
    1. Convierte el query en un vector usando text-embedding-004
    2. Busca los 5 fragmentos más similares usando similitud de coseno (<=>)
    3. Recupera los metadatos completos de los documentos
    4. Aplica filtros adicionales (tipo_documento, fecha_desde, fecha_hasta)
    5. Pagina los resultados
    
    Args:
        request: Solicitud de búsqueda con query, filtros y paginación
        db: Sesión de base de datos
    
    Returns:
        Respuesta con lista de documentos ordenados por relevancia
    
    Raises:
        HTTPException 400: Si el query es inválido
        HTTPException 500: Si falla la generación de embeddings o la búsqueda
    """
    try:
        logger.info(
            "search_request_received",
            query=request.query,
            filters=request.filters.model_dump() if request.filters else None,
            page=request.page,
            page_size=request.page_size
        )
        
        # 1. Generar embedding del query usando AIService
        ai_service = AIService()
        
        try:
            query_vector = ai_service.generate_query_embedding(request.query)
            logger.info(
                "query_embedding_generated",
                query=request.query,
                embedding_dimensions=len(query_vector)
            )
        except Exception as exc:
            logger.error(
                "query_embedding_generation_failed",
                query=request.query,
                error=str(exc)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar embedding de búsqueda"
            )
        
        # 2. Búsqueda vectorial usando pgvector (NO usar LIKE)
        # Usar operador <=> para similitud de coseno (0 = idéntico, 2 = opuesto)
        # Ordenar ASC para obtener los más similares primero
        vector_str = "[" + ",".join(map(str, query_vector)) + "]"
        
        # Usar f-string para insertar el vector directamente en la consulta
        # ya que pgvector no soporta bien parámetros nombrados para vectores
        sql_query = text(f"""
            SELECT DISTINCT 
                f.documento_id,
                (f.embedding <=> '{vector_str}'::vector) AS similitud
            FROM fragmentos f
            INNER JOIN documentos d ON f.documento_id = d.id
            WHERE d.status = 'completed'
            ORDER BY similitud ASC
            LIMIT 50
        """)
        
        try:
            results = db.execute(sql_query).fetchall()
            logger.info(
                "vector_search_completed",
                num_results=len(results)
            )
        except Exception as exc:
            logger.error(
                "vector_search_failed",
                error=str(exc),
                error_type=type(exc).__name__
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al ejecutar búsqueda vectorial"
            )
        
        # 3. Obtener documento_ids únicos
        documento_ids = [row.documento_id for row in results]
        
        if not documento_ids:
            # No se encontraron resultados
            logger.info("no_search_results_found", query=request.query)
            return SearchResponse(
                results=[],
                total=0,
                page=request.page,
                total_pages=0
            )
        
        # Crear mapa de similitudes por documento_id
        similitud_map = {row.documento_id: row.similitud for row in results}
        
        # Filtrar por umbral de similitud (cosine distance: 0=idéntico, 2=opuesto)
        # Valores menores = más similares. Threshold de 1.0 es razonable para búsqueda semántica
        SIMILARITY_THRESHOLD = 1.0
        documento_ids_filtrados = [
            doc_id for doc_id in documento_ids 
            if similitud_map.get(doc_id, 999) <= SIMILARITY_THRESHOLD
        ]
        
        if not documento_ids_filtrados:
            # No hay resultados relevantes
            logger.info("no_relevant_results_found", query=request.query, threshold=SIMILARITY_THRESHOLD)
            return SearchResponse(
                results=[],
                total=0,
                page=request.page,
                total_pages=0
            )
        
        # 4. Consultar metadatos completos de documentos
        query_documentos = db.query(Documento).filter(
            Documento.id.in_(documento_ids_filtrados),
            Documento.status == 'completed'
        )
        
        # 5. Aplicar filtros adicionales
        if request.filters:
            if request.filters.tipo_documento:
                query_documentos = query_documentos.filter(
                    Documento.tipo_documento == request.filters.tipo_documento
                )
            
            if request.filters.fecha_desde:
                query_documentos = query_documentos.filter(
                    Documento.fecha_documento >= request.filters.fecha_desde
                )
            
            if request.filters.fecha_hasta:
                query_documentos = query_documentos.filter(
                    Documento.fecha_documento <= request.filters.fecha_hasta
                )
        
        # Obtener todos los documentos que cumplen los filtros
        documentos = query_documentos.all()
        
        logger.info(
            "documents_retrieved",
            num_documents=len(documentos),
            filters_applied=request.filters is not None
        )
        
        # Ordenar documentos por similitud (usando el mapa)
        documentos_ordenados = sorted(
            documentos,
            key=lambda d: similitud_map.get(d.id, 999)  # 999 para documentos sin similitud
        )
        
        # 6. Paginar resultados
        total = len(documentos_ordenados)
        total_pages = math.ceil(total / request.page_size)
        
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        
        documentos_pagina = documentos_ordenados[start_idx:end_idx]
        
        # Construir respuesta con SearchResult
        search_results = []
        for doc in documentos_pagina:
            documento_response = DocumentoResponse.model_validate(doc)
            # Replace MinIO URL with our backend download endpoint
            documento_response.minio_url = f"{settings.API_BASE_URL}/api/v1/documentos/{doc.id}/download"
            
            search_results.append(SearchResult(
                documento=documento_response,
                relevance_score=similitud_map.get(doc.id, 999)
            ))
        
        
        logger.info(
            "search_completed",
            query=request.query,
            total_results=total,
            page=request.page,
            results_in_page=len(search_results)
        )
        
        return SearchResponse(
            results=search_results,
            total=total,
            page=request.page,
            total_pages=total_pages
        )
        
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    
    except Exception as exc:
        logger.error(
            "search_endpoint_error",
            query=request.query if request else "unknown",
            error=str(exc),
            error_type=type(exc).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la búsqueda"
        )


@router.get("/{documento_id}/audit", response_model=AuditLogResponse)
async def get_document_audit_history(
    documento_id: str,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de auditoría de un documento específico.
    
    Args:
        documento_id: ID del documento
        page: Número de página (empezando en 1)
        page_size: Tamaño de página (máximo 100)
        db: Sesión de base de datos
    
    Returns:
        Historial paginado de cambios del documento
    
    Raises:
        HTTPException 404: Si el documento no existe
        HTTPException 400: Si los parámetros de paginación son inválidos
    """
    try:
        # Verificar que el documento existe
        documento = db.query(Documento).filter(
            Documento.id == documento_id
        ).first()
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Validar parámetros de paginación
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de página debe ser mayor a 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tamaño de página debe estar entre 1 y 100"
            )
        
        # Obtener historial usando el servicio de auditoría
        audit_service = AuditService(db)
        history = audit_service.get_document_history(
            documento_id=documento.id,
            page=page,
            page_size=page_size
        )
        
        logger.info(
            "document_audit_history_retrieved",
            documento_id=documento_id,
            total_entries=history.total,
            page=page
        )
        
        return history
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "document_audit_history_error",
            documento_id=documento_id,
            error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el historial de auditoría"
        )


@router.get("/audit/all", response_model=AuditLogResponse)
async def get_all_audit_history(
    page: int = 1,
    page_size: int = 20,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial completo de auditoría del sistema con filtros opcionales.
    
    Args:
        page: Número de página (empezando en 1)
        page_size: Tamaño de página (máximo 100)
        action: Filtrar por tipo de acción ('CREATE', 'UPDATE', 'DELETE')
        user_id: Filtrar por ID de usuario
        date_from: Fecha de inicio del rango (formato ISO: YYYY-MM-DD)
        date_to: Fecha de fin del rango (formato ISO: YYYY-MM-DD)
        db: Sesión de base de datos
    
    Returns:
        Historial paginado de auditoría del sistema
    
    Raises:
        HTTPException 400: Si los parámetros son inválidos
    """
    try:
        # Validar parámetros de paginación
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de página debe ser mayor a 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tamaño de página debe estar entre 1 y 100"
            )
        
        # Validar acción si se proporciona
        if action and action.upper() not in ['CREATE', 'UPDATE', 'DELETE']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La acción debe ser CREATE, UPDATE o DELETE"
            )
        
        # Parsear fechas si se proporcionan
        parsed_date_from = None
        parsed_date_to = None
        
        if date_from:
            try:
                from datetime import datetime
                parsed_date_from = datetime.fromisoformat(date_from)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_desde inválido. Use YYYY-MM-DD"
                )
        
        if date_to:
            try:
                from datetime import datetime
                parsed_date_to = datetime.fromisoformat(date_to)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_hasta inválido. Use YYYY-MM-DD"
                )
        
        # Validar rango de fechas
        if parsed_date_from and parsed_date_to and parsed_date_from > parsed_date_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha_desde debe ser anterior a fecha_hasta"
            )
        
        # Obtener historial usando el servicio de auditoría
        audit_service = AuditService(db)
        history = audit_service.get_all_audit_history(
            page=page,
            page_size=page_size,
            action_filter=action,
            user_filter=user_id,
            date_from=parsed_date_from,
            date_to=parsed_date_to
        )
        
        logger.info(
            "all_audit_history_retrieved",
            total_entries=history.total,
            page=page,
            filters={
                "action": action,
                "user_id": user_id,
                "date_from": date_from,
                "date_to": date_to
            }
        )
        
        return history
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "all_audit_history_error",
            error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el historial de auditoría"
        )


@router.get("/audit/statistics")
async def get_audit_statistics(
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de auditoría del sistema.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Estadísticas de auditoría incluyendo conteos por acción, usuarios y actividad diaria
    """
    try:
        audit_service = AuditService(db)
        statistics = audit_service.get_audit_statistics()
        
        logger.info(
            "audit_statistics_retrieved",
            total_entries=statistics.get("total_entries", 0)
        )
        
        return statistics
        
    except Exception as exc:
        logger.error(
            "audit_statistics_error",
            error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas de auditoría"
        )
