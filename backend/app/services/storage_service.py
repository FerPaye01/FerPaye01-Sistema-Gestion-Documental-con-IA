"""
Servicio de almacenamiento de archivos usando MinIO.
"""
from datetime import timedelta
from typing import BinaryIO
from minio import Minio
from minio.error import S3Error
import structlog
from uuid import uuid4
from datetime import datetime

from app.config import settings

logger = structlog.get_logger()


class StorageService:
    """
    Servicio para gestionar el almacenamiento de archivos en MinIO.
    """
    
    def __init__(self):
        """
        Inicializa el cliente MinIO con credenciales de entorno.
        """
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
        self.internal_endpoint = settings.MINIO_ENDPOINT
        self.external_endpoint = settings.MINIO_EXTERNAL_ENDPOINT
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        Crea el bucket si no existe.
        """
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(
                    "bucket_created",
                    bucket=self.bucket
                )
            else:
                logger.info(
                    "bucket_exists",
                    bucket=self.bucket
                )
        except S3Error as exc:
            logger.error(
                "bucket_creation_failed",
                bucket=self.bucket,
                error=str(exc)
            )
            raise
    
    def _replace_internal_hostname(self, url: str) -> str:
        """
        Reemplaza el hostname interno con el externo en una URL presigned.
        
        Args:
            url: URL con hostname interno (ej: http://minio:9000/...)
            
        Returns:
            URL con hostname externo (ej: http://localhost:9000/...)
        """
        # Construir los patrones de URL con y sin protocolo
        internal_url_http = f"http://{self.internal_endpoint}"
        internal_url_https = f"https://{self.internal_endpoint}"
        external_url_http = f"http://{self.external_endpoint}"
        external_url_https = f"https://{self.external_endpoint}"
        
        # Reemplazar hostname interno con externo (mantener el protocolo)
        if internal_url_https in url:
            replaced_url = url.replace(internal_url_https, external_url_https)
            logger.debug(
                "hostname_replaced",
                original_url=url,
                replaced_url=replaced_url,
                protocol="https"
            )
            return replaced_url
        elif internal_url_http in url:
            replaced_url = url.replace(internal_url_http, external_url_http)
            logger.debug(
                "hostname_replaced",
                original_url=url,
                replaced_url=replaced_url,
                protocol="http"
            )
            return replaced_url
        else:
            # La URL ya tiene el hostname correcto o no contiene el hostname interno
            logger.debug(
                "hostname_already_correct",
                url=url,
                internal_endpoint=self.internal_endpoint
            )
            return url
    
    def upload_file(self, file_path: str, filename: str, content_type: str) -> tuple[str, str]:
        """
        Sube un archivo a MinIO y devuelve la URL pre-firmada y el nombre del objeto.
        
        Args:
            file_path: Ruta local del archivo a subir
            filename: Nombre original del archivo
            content_type: Tipo MIME del archivo (ej: application/pdf)
        
        Returns:
            Tupla con (url_prefirmada, object_name)
        
        Raises:
            S3Error: Si falla la subida del archivo
        """
        try:
            # Generar nombre único con estructura de carpetas por año
            year = datetime.now().year
            unique_id = uuid4()
            object_name = f"{year}/{unique_id}_{filename}"
            
            # Subir archivo a MinIO
            self.client.fput_object(
                self.bucket,
                object_name,
                file_path,
                content_type=content_type
            )
            
            logger.info(
                "file_uploaded",
                object_name=object_name,
                filename=filename,
                content_type=content_type
            )
            
            # Generar URL pre-firmada válida por 7 días con hostname externo
            url = self.get_file_url(object_name)
            
            logger.info(
                "file_upload_complete",
                object_name=object_name,
                url=url,
                external_endpoint=self.external_endpoint
            )
            
            return url, object_name
            
        except S3Error as exc:
            logger.error(
                "file_upload_failed",
                filename=filename,
                error=str(exc)
            )
            raise
    
    def get_file_url(self, object_name: str, expires_days: int = 7) -> str:
        """
        Genera una URL pre-firmada para acceder a un archivo con hostname externo.
        
        Args:
            object_name: Nombre del objeto en MinIO
            expires_days: Días de validez de la URL (default: 7)
        
        Returns:
            URL pre-firmada con hostname externo accesible desde el navegador
        
        Raises:
            S3Error: Si falla la generación de la URL
        """
        try:
            # Generar URL presigned con hostname interno
            internal_url = self.client.presigned_get_object(
                self.bucket,
                object_name,
                expires=timedelta(days=expires_days)
            )
            
            # Reemplazar hostname interno con externo
            external_url = self._replace_internal_hostname(internal_url)
            
            logger.debug(
                "presigned_url_generated",
                object_name=object_name,
                expires_days=expires_days,
                internal_url=internal_url,
                external_url=external_url
            )
            
            return external_url
            
        except S3Error as exc:
            logger.error(
                "presigned_url_generation_failed",
                object_name=object_name,
                error=str(exc)
            )
            raise
    
    def delete_file(self, object_name: str):
        """
        Elimina un archivo de MinIO.
        
        Args:
            object_name: Nombre del objeto en MinIO
        
        Raises:
            S3Error: Si falla la eliminación
        """
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(
                "file_deleted",
                object_name=object_name
            )
        except S3Error as exc:
            logger.error(
                "file_deletion_failed",
                object_name=object_name,
                error=str(exc)
            )
            raise
