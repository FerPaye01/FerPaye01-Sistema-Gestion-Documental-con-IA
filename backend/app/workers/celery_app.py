"""
Configuración de Celery para procesamiento asíncrono de documentos.
"""
from celery import Celery
import structlog

from app.config import settings

# Configurar logging estructurado
logger = structlog.get_logger()

# Crear instancia de Celery
celery_app = Celery(
    "sgd_ugel_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.workers.tasks']  # Módulos con tareas
)

# Configuración de Celery
celery_app.conf.update(
    # Serialización
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='America/Lima',
    enable_utc=True,
    
    # Configuración de tareas
    task_track_started=True,
    task_time_limit=3600,  # 1 hora máximo por tarea
    task_soft_time_limit=3300,  # 55 minutos soft limit
    
    # Configuración de resultados
    result_expires=86400,  # Resultados expiran en 24 horas
    result_extended=True,  # Incluir metadata adicional en resultados
    
    # Configuración de workers
    worker_prefetch_multiplier=1,  # Tomar 1 tarea a la vez
    worker_max_tasks_per_child=50,  # Reiniciar worker cada 50 tareas (prevenir memory leaks)
    worker_disable_rate_limits=False,
    
    # Configuración de reintentos
    task_acks_late=True,  # Confirmar tarea solo después de completarla
    task_reject_on_worker_lost=True,  # Re-encolar si worker muere
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

logger.info(
    "celery_configured",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    timezone='America/Lima'
)
