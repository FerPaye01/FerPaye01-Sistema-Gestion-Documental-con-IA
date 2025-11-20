"""
Script de verificación standalone para TextService.
"""
import re
import sys
from typing import List


class TextService:
    """
    Servicio para limpiar y fragmentar texto extraído de documentos.
    """
    
    def __init__(self):
        self.chunk_size = 800
        self.overlap = 100
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Eliminar caracteres no imprimibles
        # Incluye: ª (U+00AA), º (U+00BA), ° (U+00B0), ñ, Ñ, acentos, etc.
        text = re.sub(r'[^\x20-\x7E\u00A0-\u024F\u1E00-\u1EFF\n\r\t]', '', text)
        
        # Normalizar espacios en blanco
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalizar saltos de línea
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Eliminar espacios al inicio y final
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        if not text:
            return []
        
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.overlap
        
        if chunk_size <= overlap:
            raise ValueError(
                f"chunk_size ({chunk_size}) debe ser mayor que overlap ({overlap})"
            )
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            
            if end >= text_length:
                break
            
            start = end - overlap
        
        return chunks


def test_clean_text():
    """Verifica la limpieza de texto."""
    service = TextService()
    
    # Test 1: Caracteres no imprimibles
    dirty_text = "Hola\x00\x01mundo\x02con\x03caracteres\x04raros"
    clean = service.clean_text(dirty_text)
    assert clean == "Holamundoconcaracteresraros", f"Expected clean text, got: {clean}"
    print("✓ Test 1: Limpieza de caracteres no imprimibles - PASSED")
    
    # Test 2: Normalización de espacios
    spaced_text = "Texto   con    muchos     espacios"
    clean = service.clean_text(spaced_text)
    assert clean == "Texto con muchos espacios", f"Expected normalized spaces, got: {clean}"
    print("✓ Test 2: Normalización de espacios - PASSED")
    
    # Test 3: Caracteres latinos
    latin_text = "Año 2024: Resolución Nº 123-UGEL-Ilo"
    clean = service.clean_text(latin_text)
    assert "Año" in clean and "Nº" in clean, f"Expected latin chars preserved, got: {clean}"
    print("✓ Test 3: Preservación de caracteres latinos - PASSED")
    
    # Test 4: Texto vacío
    clean = service.clean_text("")
    assert clean == "", f"Expected empty string, got: {clean}"
    print("✓ Test 4: Texto vacío - PASSED")


def test_chunk_text():
    """Verifica la fragmentación de texto."""
    service = TextService()
    
    # Test 1: Texto corto (no requiere fragmentación)
    short_text = "a" * 500
    chunks = service.chunk_text(short_text)
    assert len(chunks) == 1, f"Expected 1 chunk, got {len(chunks)}"
    assert len(chunks[0]) == 500, f"Expected chunk of 500 chars, got {len(chunks[0])}"
    print("✓ Test 1: Texto corto - PASSED")
    
    # Test 2: Texto largo con overlap
    long_text = "a" * 1500
    chunks = service.chunk_text(long_text, chunk_size=800, overlap=100)
    assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
    assert len(chunks[0]) == 800, f"Expected first chunk of 800 chars, got {len(chunks[0])}"
    print("✓ Test 2: Texto largo con overlap - PASSED")
    
    # Test 3: Validar que chunks no excedan 800 caracteres
    very_long_text = "b" * 5000
    chunks = service.chunk_text(very_long_text)
    for i, chunk in enumerate(chunks):
        assert len(chunk) <= 800, f"Chunk {i} exceeds 800 chars: {len(chunk)}"
    print(f"✓ Test 3: Validación de tamaño máximo (800 chars) - PASSED ({len(chunks)} chunks)")
    
    # Test 4: Verificar overlap de 100 caracteres
    text = "x" * 1600
    chunks = service.chunk_text(text, chunk_size=800, overlap=100)
    if len(chunks) > 1:
        overlap_check = chunks[0][-100:] == chunks[1][:100]
        assert overlap_check, "Overlap de 100 caracteres no se mantiene correctamente"
    print("✓ Test 4: Verificación de overlap de 100 caracteres - PASSED")
    
    # Test 5: Texto vacío
    chunks = service.chunk_text("")
    assert chunks == [], f"Expected empty list, got {chunks}"
    print("✓ Test 5: Texto vacío - PASSED")


def test_requirements():
    """Verifica que se cumplan los requisitos específicos de la tarea."""
    service = TextService()
    
    print("\n[VERIFICACIÓN DE REQUISITOS]")
    
    # Requisito 2.4: Limpieza de caracteres no imprimibles y normalización
    req_2_4_text = "Documento\x00\x01con   espacios    múltiples\x02y\x03caracteres\x04raros"
    cleaned = service.clean_text(req_2_4_text)
    assert "\x00" not in cleaned, "Caracteres no imprimibles no fueron eliminados"
    assert "  " not in cleaned, "Espacios múltiples no fueron normalizados"
    print("✓ Requisito 2.4: Limpieza y normalización - CUMPLIDO")
    
    # Requisito 2.5: Fragmentación con overlap de 100 caracteres, máx 800 caracteres
    req_2_5_text = "x" * 3000
    chunks = service.chunk_text(req_2_5_text)
    
    # Verificar que ningún chunk exceda 800 caracteres
    max_chunk_size = max(len(chunk) for chunk in chunks)
    assert max_chunk_size <= 800, f"Chunks exceden 800 caracteres: {max_chunk_size}"
    
    # Verificar overlap de 100 caracteres entre chunks consecutivos
    for i in range(len(chunks) - 1):
        if len(chunks[i]) == 800 and len(chunks[i+1]) >= 100:
            overlap_match = chunks[i][-100:] == chunks[i+1][:100]
            assert overlap_match, f"Overlap incorrecto entre chunks {i} y {i+1}"
    
    print(f"✓ Requisito 2.5: Fragmentación (máx 800 chars, overlap 100) - CUMPLIDO")
    print(f"  - Texto de 3000 caracteres generó {len(chunks)} chunks")
    print(f"  - Tamaño máximo de chunk: {max_chunk_size} caracteres")


if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE TEXT SERVICE")
    print("=" * 60)
    
    try:
        print("\n[1] Probando clean_text()...")
        test_clean_text()
        
        print("\n[2] Probando chunk_text()...")
        test_chunk_text()
        
        print("\n[3] Verificando requisitos de la tarea...")
        test_requirements()
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        sys.exit(1)
