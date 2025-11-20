"""
Script de verificación para AIService.
Prueba la extracción de metadatos y generación de embeddings.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService
from app.config import settings


def test_extract_metadata():
    """Prueba la extracción de metadatos con Gemini."""
    print("=" * 60)
    print("TEST 1: Extracción de Metadatos con Gemini")
    print("=" * 60)
    
    # Texto de ejemplo de un documento administrativo
    sample_text = """
    OFICIO MÚLTIPLE N° 045-2024-UGEL-ILO
    
    Ilo, 15 de marzo de 2024
    
    SEÑOR(A) DIRECTOR(A) DE LA I.E.
    PRESENTE.-
    
    ASUNTO: Convocatoria a Reunión de Coordinación
    
    Es grato dirigirme a usted para saludarle cordialmente y a la vez comunicarle
    que se ha programado una reunión de coordinación con todos los directores de
    las instituciones educativas de la jurisdicción de la UGEL Ilo.
    
    La reunión se llevará a cabo el día 20 de marzo de 2024 a las 9:00 AM en el
    auditorio de la UGEL Ilo. El tema principal será la planificación del año
    escolar 2024 y la implementación de nuevas políticas educativas.
    
    Se solicita su puntual asistencia.
    
    Atentamente,
    
    Prof. Juan Pérez García
    Director de la UGEL Ilo
    """
    
    try:
        ai_service = AIService()
        print("\n✓ AIService inicializado correctamente")
        print(f"✓ Modelo Gemini: {ai_service.gemini_model._model_name}")
        print(f"✓ Modelo Embedding: {ai_service.embedding_model}")
        
        print("\n📄 Extrayendo metadatos del documento...")
        metadata = ai_service.extract_metadata(sample_text)
        
        print("\n✅ Metadatos extraídos exitosamente:")
        print(f"  • Tipo de documento: {metadata.get('tipo_documento')}")
        print(f"  • Tema principal: {metadata.get('tema_principal')}")
        print(f"  • Fecha del documento: {metadata.get('fecha_documento')}")
        print(f"  • Entidades clave: {metadata.get('entidades_clave')}")
        print(f"  • Resumen: {metadata.get('resumen_corto')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al extraer metadatos: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False


def test_generate_embedding():
    """Prueba la generación de embeddings."""
    print("\n" + "=" * 60)
    print("TEST 2: Generación de Embeddings")
    print("=" * 60)
    
    sample_text = "Convocatoria a reunión de coordinación para directores de instituciones educativas"
    
    try:
        ai_service = AIService()
        
        print("\n📊 Generando embedding para documento...")
        embedding = ai_service.generate_embedding(sample_text)
        
        print(f"\n✅ Embedding generado exitosamente:")
        print(f"  • Dimensiones: {len(embedding)}")
        print(f"  • Primeros 5 valores: {embedding[:5]}")
        print(f"  • Tipo de datos: {type(embedding[0])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al generar embedding: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False


def test_generate_query_embedding():
    """Prueba la generación de embeddings para queries."""
    print("\n" + "=" * 60)
    print("TEST 3: Generación de Query Embeddings")
    print("=" * 60)
    
    sample_query = "reunión directores instituciones educativas"
    
    try:
        ai_service = AIService()
        
        print("\n🔍 Generando embedding para query de búsqueda...")
        query_embedding = ai_service.generate_query_embedding(sample_query)
        
        print(f"\n✅ Query embedding generado exitosamente:")
        print(f"  • Dimensiones: {len(query_embedding)}")
        print(f"  • Primeros 5 valores: {query_embedding[:5]}")
        print(f"  • Tipo de datos: {type(query_embedding[0])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al generar query embedding: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("\n🚀 VERIFICACIÓN DEL SERVICIO DE IA (AIService)")
    print("=" * 60)
    
    # Verificar que la API key esté configurada
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_api_key_here":
        print("\n⚠️  ADVERTENCIA: GOOGLE_API_KEY no está configurada")
        print("   Por favor, configura la variable de entorno GOOGLE_API_KEY")
        print("   en el archivo .env antes de ejecutar las pruebas.")
        return
    
    print(f"\n✓ GOOGLE_API_KEY configurada (longitud: {len(settings.GOOGLE_API_KEY)} caracteres)")
    
    # Ejecutar pruebas
    results = []
    
    results.append(("Extracción de Metadatos", test_extract_metadata()))
    results.append(("Generación de Embeddings", test_generate_embedding()))
    results.append(("Generación de Query Embeddings", test_generate_query_embedding()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} pruebas exitosas")
    
    if total_passed == total_tests:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")


if __name__ == "__main__":
    main()
