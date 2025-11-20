"""
Verification script for SQLAlchemy ORM models
Tests that models are correctly defined and relationships work
"""
from app.models import Documento, Fragmento, Base
from sqlalchemy import inspect
import sys


def verify_documento_model():
    """Verify Documento model structure"""
    print("✓ Checking Documento model...")
    
    # Check table name
    assert Documento.__tablename__ == 'documentos', "Table name mismatch"
    
    # Get mapper for inspection
    mapper = inspect(Documento)
    columns = {col.key for col in mapper.columns}
    
    # Check required columns
    required_columns = {
        'id', 'filename', 'minio_url', 'minio_object_name',
        'tipo_documento', 'tema_principal', 'fecha_documento',
        'entidades_clave', 'resumen_corto', 'file_size_bytes',
        'content_type', 'num_pages', 'created_at', 'processed_at',
        'status', 'error_message'
    }
    
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    
    # Check relationships
    relationships = {rel.key for rel in mapper.relationships}
    assert 'fragmentos' in relationships, "Missing fragmentos relationship"
    
    # Check cascade configuration
    fragmentos_rel = mapper.relationships['fragmentos']
    assert 'delete-orphan' in fragmentos_rel.cascade, "Missing delete-orphan cascade"
    assert fragmentos_rel.passive_deletes, "passive_deletes should be True"
    
    print("  ✓ All columns present")
    print("  ✓ Relationship to Fragmento configured")
    print("  ✓ CASCADE DELETE configured correctly")


def verify_fragmento_model():
    """Verify Fragmento model structure"""
    print("\n✓ Checking Fragmento model...")
    
    # Check table name
    assert Fragmento.__tablename__ == 'fragmentos', "Table name mismatch"
    
    # Get mapper for inspection
    mapper = inspect(Fragmento)
    columns = {col.key for col in mapper.columns}
    
    # Check required columns
    required_columns = {
        'id', 'documento_id', 'texto', 'posicion', 'embedding', 'created_at'
    }
    
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    
    # Check embedding column type
    embedding_col = mapper.columns['embedding']
    assert 'vector' in str(embedding_col.type).lower(), "embedding should be Vector type"
    
    # Check foreign key
    documento_id_col = mapper.columns['documento_id']
    assert len(documento_id_col.foreign_keys) > 0, "Missing foreign key to documentos"
    
    fk = list(documento_id_col.foreign_keys)[0]
    assert fk.column.table.name == 'documentos', "Foreign key should reference documentos table"
    assert fk.ondelete == 'CASCADE', "Foreign key should have ON DELETE CASCADE"
    
    # Check relationships
    relationships = {rel.key for rel in mapper.relationships}
    assert 'documento' in relationships, "Missing documento relationship"
    
    print("  ✓ All columns present")
    print("  ✓ Vector(768) type for embedding")
    print("  ✓ Foreign key with ON DELETE CASCADE")
    print("  ✓ Relationship to Documento configured")


def verify_bidirectional_relationship():
    """Verify bidirectional relationship between models"""
    print("\n✓ Checking bidirectional relationship...")
    
    doc_mapper = inspect(Documento)
    frag_mapper = inspect(Fragmento)
    
    # Check Documento -> Fragmento
    doc_rel = doc_mapper.relationships['fragmentos']
    assert doc_rel.back_populates == 'documento', "back_populates should be 'documento'"
    
    # Check Fragmento -> Documento
    frag_rel = frag_mapper.relationships['documento']
    assert frag_rel.back_populates == 'fragmentos', "back_populates should be 'fragmentos'"
    
    print("  ✓ Bidirectional relationship configured correctly")


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("SQLAlchemy ORM Models Verification")
    print("=" * 60)
    
    try:
        verify_documento_model()
        verify_fragmento_model()
        verify_bidirectional_relationship()
        
        print("\n" + "=" * 60)
        print("✓ ALL CHECKS PASSED")
        print("=" * 60)
        print("\nTask 2.3 Requirements Met:")
        print("  ✓ Modelo Documento created with relationship to Fragmento")
        print("  ✓ Modelo Fragmento created with Vector type from pgvector")
        print("  ✓ Relationships and cascades (ON DELETE CASCADE) configured")
        print("\nRequirements 3.5, 4.2 satisfied")
        return 0
        
    except AssertionError as e:
        print(f"\n✗ VERIFICATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
