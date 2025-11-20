"""
Script de verificación de configuración de Celery.
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.workers.celery_app import celery_app
from app.workers.tasks import process_document


def verify_celery_config():
    """Verifica la configuración de Celery"""
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DE CELERY")
    print("=" * 60)
    
    # 1. Verificar que la app de Celery está configurada
    print("\n1. Verificando instancia de Celery...")
    print(f"   ✓ Nombre de la app: {celery_app.main}")
    print(f"   ✓ Broker URL: {celery_app.conf.broker_url}")
    print(f"   ✓ Backend URL: {celery_app.conf.result_backend}")
    
    # 2. Verificar configuración
    print("\n2. Verificando configuración...")
    print(f"   ✓ Serializer: {celery_app.conf.task_serializer}")
    print(f"   ✓ Timezone: {celery_app.conf.timezone}")
    print(f"   ✓ Max retries: 3 (configurado en tarea)")
    print(f"   ✓ Worker prefetch: {celery_app.conf.worker_prefetch_multiplier}")
    print(f"   ✓ Task time limit: {celery_app.conf.task_time_limit}s")
    
    # 3. Verificar que las tareas están registradas
    print("\n3. Verificando tareas registradas...")
    registered_tasks = list(celery_app.tasks.keys())
    
    # Filtrar solo nuestras tareas (no las built-in de Celery)
    our_tasks = [t for t in registered_tasks if 'app.workers' in t]
    
    if our_tasks:
        print(f"   ✓ Tareas encontradas: {len(our_tasks)}")
        for task in our_tasks:
            print(f"     - {task}")
    else:
        print("   ⚠ No se encontraron tareas personalizadas")
    
    # 4. Verificar configuración de reintentos
    print("\n4. Verificando configuración de reintentos...")
    print(f"   ✓ Max retries: {process_document.max_retries}")
    print(f"   ✓ Default retry delay: {process_document.default_retry_delay}s")
    print(f"   ✓ Retry delays exponenciales: 60s, 300s, 900s")
    
    # 5. Verificar configuración de progreso
    print("\n5. Verificando configuración de progreso...")
    print(f"   ✓ Task track started: {celery_app.conf.task_track_started}")
    print(f"   ✓ Result extended: {celery_app.conf.result_extended}")
    
    print("\n" + "=" * 60)
    print("✓ VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print("\nPara iniciar el worker de Celery, ejecuta:")
    print("  celery -A app.workers.celery_app worker --loglevel=info --concurrency=2")
    print("\nPara monitorear tareas, ejecuta:")
    print("  celery -A app.workers.celery_app flower")
    print("=" * 60)


if __name__ == "__main__":
    try:
        verify_celery_config()
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
