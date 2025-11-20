"""
Tareas Celery para procesamiento asíncrono de documentos.
"""
import os
import traceback
from datetime import datetime
from typing import Optional
import structlog
from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.documento import Documento, Fragmento
from app.models.schemas import DocumentoMetadata
from app.services.storage_service import StorageService
from app.services.ocr_service import OCRService
from app.services.text_service import TextService
from app.services.ai_service import AIService
from app.services.audit_service import AuditService

# Configurar logging estructurado
logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, temp_path: str, filename: str, content_type: str) -> str:
    """
    Tarea principal de procesamiento de documentos.
    
    Pipeline completo:
    1. Storage: Subir archivo a MinIO
    2. Text Extraction: OCR híbrido (PyMuPDF → pytesseract)
    3. Text Cleaning: Normalización y limpieza
    4. Chunking: Fragmentación con overlap
    5. Metadata Extraction: Llamada a Gemini
    6. Embedding Generation: Llamada a text-embedding-004
    7. Database Storage: Insertar en PostgreSQL
    
    Args:
        temp_path: Ruta temporal del archivo
        filename: Nombre original del archivo
        content_type: Tipo MIME del archivo
    
    Returns:
        ID del documento procesado (UUID como string)
    
    Raises:
        Exception: Si falla el procesamiento (se reintentará automáticamente)
    """
    documento_id: Optional[str] = None
    db: Optional[Session] = None
    
    try:
        logger.info(
            "document_processing_started",
            filename=filename,
            content_type=content_type,
            task_id=self.request.id
        )
        
        # Actualizar progreso: Iniciando
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0, 'stage': 'Iniciando procesamiento'}
        )
        
        # Inicializar servicios
        storage_service = StorageService()
        ocr_service = OCRService()
        text_service = TextService()
        ai_service = AIService()
        
        # Obtener sesión de base de datos
        db = SessionLocal()
        
        # PASO 1: Subir archivo a MinIO
        logger.info("storage_upload_started", filename=filename)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'stage': 'Subiendo archivo a almacenamiento'}
        )
        
        minio_url, object_name = storage_service.upload_file(
            temp_path,
            filename,
            content_type
        )
        
        # Obtener tamaño del archivo
        file_size_bytes = os.path.getsize(temp_path)
        
        logger.info(
            "storage_upload_completed",
            filename=filename,
            object_name=object_name,
            file_size_bytes=file_size_bytes
        )
        
        # PASO 2: Extraer texto (OCR)
        logger.info("text_extraction_started", filename=filename)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 20, 'stage': 'Extrayendo texto del documento'}
        )
        
        raw_text = ocr_service.extract_text(temp_path, content_type)
        
        if not raw_text or len(raw_text.strip()) < 10:
            raise ValueError(f"No se pudo extraer texto suficiente del documento: {filename}")
        
        logger.info(
            "text_extraction_completed",
            filename=filename,
            text_length=len(raw_text)
        )
        
        # PASO 3: Limpiar texto
        logger.info("text_cleaning_started", filename=filename)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'stage': 'Limpiando y normalizando texto'}
        )
        
        cleaned_text = text_service.clean_text(raw_text)
        
        logger.info(
            "text_cleaning_completed",
            filename=filename,
            cleaned_length=len(cleaned_text)
        )
        
        # PASO 4: Fragmentar texto
        logger.info("text_chunking_started", filename=filename)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 40, 'stage': 'Fragmentando texto'}
        )
        
        chunks = text_service.chunk_text(cleaned_text, chunk_size=800, overlap=100)
        
        logger.info(
            "text_chunking_completed",
            filename=filename,
            num_chunks=len(chunks)
        )
        
        # PASO 5: Extraer metadatos con Gemini
        logger.info("metadata_extraction_started", filename=filename)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 50, 'stage': 'Extrayendo metadatos con IA'}
        )
        
        # Usar los primeros 4000 caracteres para extracción de metadatos
        text_for_metadata = cleaned_text[:4000]
        metadata_dict = ai_service.extract_metadata(text_for_metadata)
        
        # Convertir a objeto Pydantic para validación
        metadata = DocumentoMetadata(**metadata_dict)
        
        logger.info(
            "metadata_extraction_completed",
            filename=filename,
            tipo_documento=metadata.tipo_documento,
            tema_principal=metadata.tema_principal
        )
        
        # PASO 6: Crear registro de documento en DB
        logger.info("database_insert_started", filename=filename)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 60, 'stage': 'Guardando documento en base de datos'}
        )
        
        # Determinar número de páginas (solo para PDFs)
        num_pages = None
        if content_type == 'application/pdf':
            try:
                import fitz
                doc = fitz.open(temp_path)
                num_pages = len(doc)
                doc.close()
            except Exception as e:
                logger.warning("could_not_determine_page_count", error=str(e))
        
        # Crear documento
        documento = Documento(
            filename=filename,
            minio_url=minio_url,
            minio_object_name=object_name,
            tipo_documento=metadata.tipo_documento,
            tema_principal=metadata.tema_principal,
            fecha_documento=metadata.fecha_documento,
            entidades_clave=metadata.entidades_clave,
            resumen_corto=metadata.resumen_corto,
            file_size_bytes=file_size_bytes,
            content_type=content_type,
            num_pages=num_pages,
            status='processing'
        )
        
        db.add(documento)
        db.flush()  # Obtener el ID sin hacer commit
        
        documento_id = str(documento.id)
        
        logger.info(
            "database_insert_completed",
            filename=filename,
            documento_id=documento_id
        )
        
        # PASO 7: Generar embeddings y guardar fragmentos
        logger.info("embedding_generation_started", filename=filename, num_chunks=len(chunks))
        
        for idx, chunk in enumerate(chunks):
            # Actualizar progreso (60-90% para embeddings)
            progress = 60 + int((idx / len(chunks)) * 30)
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'stage': f'Generando embeddings ({idx + 1}/{len(chunks)})'
                }
            )
            
            # Generar embedding para el fragmento
            embedding = ai_service.generate_embedding(chunk)
            
            # Crear fragmento
            fragmento = Fragmento(
                documento_id=documento.id,
                texto=chunk,
                posicion=idx,
                embedding=embedding
            )
            
            db.add(fragmento)
            
            logger.debug(
                "fragment_created",
                documento_id=documento_id,
                posicion=idx,
                chunk_length=len(chunk)
            )
        
        logger.info(
            "embedding_generation_completed",
            filename=filename,
            documento_id=documento_id,
            num_fragments=len(chunks)
        )
        
        # PASO 8: Actualizar estado del documento a completado
        self.update_state(
            state='PROGRESS',
            meta={'progress': 95, 'stage': 'Finalizando procesamiento'}
        )
        
        documento.status = 'completed'
        documento.processed_at = datetime.utcnow()
        
        # Crear entrada de auditoría para la creación del documento
        audit_service = AuditService(db)
        documento_info = {
            "id": str(documento.id),
            "filename": documento.filename,
            "tipo_documento": documento.tipo_documento,
            "tema_principal": documento.tema_principal,
            "fecha_documento": documento.fecha_documento.isoformat() if documento.fecha_documento else None,
            "entidades_clave": documento.entidades_clave,
            "resumen_corto": documento.resumen_corto,
            "file_size_bytes": documento.file_size_bytes,
            "content_type": documento.content_type,
            "num_pages": documento.num_pages,
            "upload_timestamp": documento.upload_timestamp.isoformat(),
            "status": documento.status
        }
        
        audit_service.log_create(
            documento_id=documento.id,
            new_values=documento_info,
            user_id='system'  # Sistema automático de procesamiento
        )
        
        # Commit de todos los cambios
        db.commit()
        
        logger.info(
            "document_processing_completed",
            filename=filename,
            documento_id=documento_id,
            task_id=self.request.id
        )
        
        # Limpiar archivo temporal
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.debug("temp_file_deleted", temp_path=temp_path)
        except Exception as e:
            logger.warning("temp_file_deletion_failed", temp_path=temp_path, error=str(e))
        
        return documento_id
        
    except Exception as exc:
        # Logging estructurado del error
        logger.error(
            "document_processing_failed",
            filename=filename,
            documento_id=documento_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
            retry_count=self.request.retries,
            task_id=self.request.id
        )
        
        # Actualizar estado del documento a error si ya fue creado
        if documento_id and db:
            try:
                documento = db.query(Documento).filter(Documento.id == documento_id).first()
                if documento:
                    documento.status = 'error'
                    documento.error_message = f"{type(exc).__name__}: {str(exc)}"
                    documento.processed_at = datetime.utcnow()
                    db.commit()
            except Exception as db_error:
                logger.error(
                    "error_status_update_failed",
                    documento_id=documento_id,
                    error=str(db_error)
                )
                if db:
                    db.rollback()
        
        # Limpiar archivo temporal en caso de error
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass
        
        # Calcular delay de reintento exponencial: 60s, 300s (5min), 900s (15min)
        retry_delay = 60 * (5 ** self.request.retries)
        
        logger.info(
            "task_retry_scheduled",
            filename=filename,
            retry_count=self.request.retries + 1,
            retry_delay_seconds=retry_delay
        )
        
        # Reintentar con delay exponencial
        raise self.retry(exc=exc, countdown=retry_delay)
        
    finally:
        # Cerrar sesión de base de datos
        if db:
            db.close()
