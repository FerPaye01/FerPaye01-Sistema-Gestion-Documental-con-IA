"""
Script to verify database schema and pgvector setup
Run this after applying migrations to ensure everything is configured correctly
"""
import sys
from sqlalchemy import create_engine, text, inspect
from app.config import settings

def verify_schema():
    """Verify that the database schema is correctly set up"""
    print("=" * 70)
    print("SGD UGEL Ilo - Database Schema Verification")
    print("=" * 70)
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # 1. Check pgvector extension
            print("\n1. Checking pgvector extension...")
            result = conn.execute(text(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            ))
            extension = result.fetchone()
            if extension:
                print("   ✓ pgvector extension is installed")
            else:
                print("   ✗ pgvector extension is NOT installed")
                return False
            
            # 2. Check documentos table
            print("\n2. Checking documentos table...")
            inspector = inspect(engine)
            if 'documentos' in inspector.get_table_names():
                print("   ✓ documentos table exists")
                
                # Check columns
                columns = {col['name'] for col in inspector.get_columns('documentos')}
                required_columns = {
                    'id', 'filename', 'minio_url', 'minio_object_name',
                    'tipo_documento', 'tema_principal', 'fecha_documento',
                    'entidades_clave', 'resumen_corto', 'file_size_bytes',
                    'content_type', 'num_pages', 'created_at', 'processed_at',
                    'status', 'error_message'
                }
                
                if required_columns.issubset(columns):
                    print(f"   ✓ All required columns present ({len(required_columns)} columns)")
                else:
                    missing = required_columns - columns
                    print(f"   ✗ Missing columns: {missing}")
                    return False
                
                # Check indexes
                indexes = {idx['name'] for idx in inspector.get_indexes('documentos')}
                required_indexes = {
                    'idx_documentos_tipo', 'idx_documentos_fecha',
                    'idx_documentos_status', 'idx_documentos_created'
                }
                
                if required_indexes.issubset(indexes):
                    print(f"   ✓ All required indexes present ({len(required_indexes)} indexes)")
                else:
                    missing = required_indexes - indexes
                    print(f"   ✗ Missing indexes: {missing}")
                    return False
            else:
                print("   ✗ documentos table does NOT exist")
                return False
            
            # 3. Check fragmentos table
            print("\n3. Checking fragmentos table...")
            if 'fragmentos' in inspector.get_table_names():
                print("   ✓ fragmentos table exists")
                
                # Check columns
                columns = {col['name'] for col in inspector.get_columns('fragmentos')}
                required_columns = {
                    'id', 'documento_id', 'texto', 'posicion', 'embedding', 'created_at'
                }
                
                if required_columns.issubset(columns):
                    print(f"   ✓ All required columns present ({len(required_columns)} columns)")
                else:
                    missing = required_columns - columns
                    print(f"   ✗ Missing columns: {missing}")
                    return False
                
                # Check embedding column type
                result = conn.execute(text("""
                    SELECT data_type, udt_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'fragmentos' AND column_name = 'embedding'
                """))
                col_info = result.fetchone()
                if col_info and col_info[1] == 'vector':
                    print("   ✓ embedding column is of type vector")
                else:
                    print(f"   ✗ embedding column type is incorrect: {col_info}")
                    return False
                
                # Check indexes
                indexes = {idx['name'] for idx in inspector.get_indexes('fragmentos')}
                if 'idx_fragmentos_documento' in indexes:
                    print("   ✓ B-tree index on documento_id exists")
                else:
                    print("   ✗ Missing B-tree index on documento_id")
                    return False
                
                # Check HNSW index (requires raw SQL)
                result = conn.execute(text("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = 'fragmentos' AND indexname = 'idx_fragmentos_embedding'
                """))
                hnsw_index = result.fetchone()
                if hnsw_index and 'hnsw' in hnsw_index[1].lower():
                    print("   ✓ HNSW index on embedding exists")
                else:
                    print("   ✗ HNSW index on embedding does NOT exist")
                    return False
            else:
                print("   ✗ fragmentos table does NOT exist")
                return False
            
            # 4. Check foreign key constraint
            print("\n4. Checking foreign key constraints...")
            fks = inspector.get_foreign_keys('fragmentos')
            has_cascade = False
            for fk in fks:
                if fk['referred_table'] == 'documentos' and fk['options'].get('ondelete') == 'CASCADE':
                    has_cascade = True
                    break
            
            if has_cascade:
                print("   ✓ Foreign key with CASCADE DELETE exists")
            else:
                print("   ✗ Foreign key with CASCADE DELETE is missing")
                return False
            
            # 5. Test vector operations
            print("\n5. Testing vector operations...")
            try:
                # Create a test vector
                test_vector = '[' + ','.join(['0.1'] * 768) + ']'
                result = conn.execute(text(f"SELECT '{test_vector}'::vector(768) <=> '{test_vector}'::vector(768) AS distance"))
                distance = result.fetchone()[0]
                if distance == 0.0:
                    print("   ✓ Vector operations working correctly")
                else:
                    print(f"   ✗ Vector distance calculation incorrect: {distance}")
                    return False
            except Exception as e:
                print(f"   ✗ Vector operations failed: {e}")
                return False
        
        print("\n" + "=" * 70)
        print("✓ All schema verification checks passed!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_schema()
    sys.exit(0 if success else 1)
