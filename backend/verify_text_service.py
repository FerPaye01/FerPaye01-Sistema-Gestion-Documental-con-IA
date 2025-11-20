"""
Script de verificación para TextService.
"""
from app.services.text_service import TextService


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
    # El overlap debe estar presente entre chunks consecutivos
    if len(chunks) > 1:
        # Los últimos 100 caracteres del primer chunk deben ser los primeros del segundo
        overlap_check = chunks[0][-100:] == chunks[1][:100]
        assert overlap_check, "Overlap de 100 caracteres no se mantiene correctamente"
    print("✓ Test 4: Verificación de overlap de 100 caracteres - PASSED")
    
    # Test 5: Texto vacío
    chunks = service.chunk_text("")
    assert chunks == [], f"Expected empty list, got {chunks}"
    print("✓ Test 5: Texto vacío - PASSED")


def test_process_text():
    """Verifica el procesamiento completo."""
    service = TextService()
    
    # Test 1: Texto corto con limpieza
    dirty_short = "Texto   con    espacios\x00\x01extras"
    chunks = service.process_text(dirty_short)
    assert len(chunks) == 1, f"Expected 1 chunk, got {len(chunks)}"
    assert "espacios" in chunks[0], f"Expected cleaned text, got: {chunks[0]}"
    print("✓ Test 1: Procesamiento de texto corto - PASSED")
    
    # Test 2: Texto largo con limpieza y fragmentación
    dirty_long = ("Documento   administrativo\x00\x01con muchos espacios " * 100)
    chunks = service.process_text(dirty_long)
    assert len(chunks) > 1, f"Expected multiple chunks, got {len(chunks)}"
    for chunk in chunks:
        assert len(chunk) <= 800, f"Chunk exceeds 800 chars: {len(chunk)}"
    print(f"✓ Test 2: Procesamiento de texto largo - PASSED ({len(chunks)} chunks)")


if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE TEXT SERVICE")
    print("=" * 60)
    
    print("\n[1] Probando clean_text()...")
    test_clean_text()
    
    print("\n[2] Probando chunk_text()...")
    test_chunk_text()
    
    print("\n[3] Probando process_text()...")
    test_process_text()
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("=" * 60)
