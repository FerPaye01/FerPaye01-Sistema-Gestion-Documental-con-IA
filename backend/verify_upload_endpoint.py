"""
Script de verificación para el endpoint de upload de documentos.
"""
import sys
import os
import io

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verifica que la API esté funcionando"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")
    print(f"  Response: {data}")


def test_upload_endpoint_exists():
    """Verifica que el endpoint de upload exista"""
    print("\n" + "=" * 60)
    print("TEST 2: Upload Endpoint Exists")
    print("=" * 60)
    
    # Intentar hacer una petición sin archivo (debe fallar con 422, no 404)
    response = client.post("/api/v1/documentos/upload")
    
    # 422 significa que el endpoint existe pero falta el parámetro
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✓ Upload endpoint exists at /api/v1/documentos/upload")


def test_upload_invalid_file_type():
    """Verifica validación de tipo de archivo"""
    print("\n" + "=" * 60)
    print("TEST 3: Invalid File Type Validation")
    print("=" * 60)
    
    # Crear un archivo de texto (no permitido)
    file_content = b"This is a text file"
    files = {
        "file": ("test.txt", io.BytesIO(file_content), "text/plain")
    }
    
    response = client.post("/api/v1/documentos/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "no soportado" in data["detail"].lower()
    print("✓ Invalid file type rejected")
    print(f"  Response: {data['detail']}")


def test_upload_file_too_large():
    """Verifica validación de tamaño de archivo"""
    print("\n" + "=" * 60)
    print("TEST 4: File Size Validation")
    print("=" * 60)
    
    # Crear un archivo PDF falso de 51MB (excede el límite de 50MB)
    large_content = b"x" * (51 * 1024 * 1024)
    files = {
        "file": ("large.pdf", io.BytesIO(large_content), "application/pdf")
    }
    
    response = client.post("/api/v1/documentos/upload", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert "demasiado grande" in data["detail"].lower()
    print("✓ Large file rejected")
    print(f"  Response: {data['detail']}")


def test_upload_valid_pdf():
    """Verifica upload exitoso de PDF"""
    print("\n" + "=" * 60)
    print("TEST 5: Valid PDF Upload")
    print("=" * 60)
    
    # Crear un PDF mínimo válido
    # Este es un PDF vacío pero válido
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF"""
    
    files = {
        "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    
    response = client.post("/api/v1/documentos/upload", files=files)
    
    # Debe retornar 202 Accepted
    assert response.status_code == 202, f"Expected 202, got {response.status_code}"
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "task_id" in data
    assert "status" in data
    assert "message" in data
    assert data["status"] == "processing"
    
    print("✓ Valid PDF upload accepted")
    print(f"  Task ID: {data['task_id']}")
    print(f"  Status: {data['status']}")
    print(f"  Message: {data['message']}")
    
    return data["task_id"]


def test_task_status_endpoint(task_id: str):
    """Verifica el endpoint de estado de tarea"""
    print("\n" + "=" * 60)
    print("TEST 6: Task Status Endpoint")
    print("=" * 60)
    
    response = client.get(f"/api/v1/documentos/tasks/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura de respuesta
    assert "task_id" in data
    assert "status" in data
    assert data["task_id"] == task_id
    
    print("✓ Task status endpoint working")
    print(f"  Task ID: {data['task_id']}")
    print(f"  Status: {data['status']}")
    if "progress" in data and data["progress"] is not None:
        print(f"  Progress: {data['progress']}%")


def test_upload_valid_jpg():
    """Verifica upload exitoso de JPG"""
    print("\n" + "=" * 60)
    print("TEST 7: Valid JPG Upload")
    print("=" * 60)
    
    # Crear un JPG mínimo válido (1x1 pixel rojo)
    jpg_content = bytes.fromhex(
        'ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707'
        '07090909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c23'
        '1c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c18'
        '0d0d1832211c213232323232323232323232323232323232323232323232323232323232'
        '32323232323232323232323232323232323232323232ffc00011080001000103012200'
        '021101031101ffc4001500010100000000000000000000000000000000ffc400140101'
        '0000000000000000000000000000000000ffda000c03010002110311003f00bf800000'
        'ffd9'
    )
    
    files = {
        "file": ("test.jpg", io.BytesIO(jpg_content), "image/jpeg")
    }
    
    response = client.post("/api/v1/documentos/upload", files=files)
    
    assert response.status_code == 202
    data = response.json()
    
    assert "task_id" in data
    assert data["status"] == "processing"
    
    print("✓ Valid JPG upload accepted")
    print(f"  Task ID: {data['task_id']}")


def main():
    """Ejecuta todas las pruebas"""
    print("\n🚀 VERIFICACIÓN DEL ENDPOINT DE UPLOAD")
    print("=" * 60)
    
    try:
        test_health_check()
        test_upload_endpoint_exists()
        test_upload_invalid_file_type()
        test_upload_file_too_large()
        task_id = test_upload_valid_pdf()
        test_task_status_endpoint(task_id)
        test_upload_valid_jpg()
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("\nVerificación completada:")
        print("  ✓ Endpoint POST /api/v1/documentos/upload existe")
        print("  ✓ Valida tipo de archivo (PDF/JPG)")
        print("  ✓ Valida tamaño máximo (50MB)")
        print("  ✓ Retorna HTTP 202 Accepted")
        print("  ✓ Encola tarea de Celery")
        print("  ✓ Retorna task_id para seguimiento")
        print("  ✓ Endpoint GET /api/v1/documentos/tasks/{task_id} funciona")
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
