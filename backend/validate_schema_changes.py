#!/usr/bin/env python3
"""
Script to validate schema changes without connecting to database
"""
import sys
import os

def validate_models():
    """Validate that the models can be imported and are syntactically correct"""
    try:
        # Add the app directory to Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        
        # Import models to check for syntax errors
        from app.models.documento import Documento, Fragmento, AuditLog
        from app.models.schemas import (
            DocumentoMetadata, DocumentoCreate, DocumentoUpdate, 
            DocumentoResponse, AuditLogEntry, AuditLogResponse
        )
        
        print("✓ All models imported successfully")
        
        # Check that the models have the expected attributes
        expected_documento_fields = [
            'id', 'filename', 'minio_url', 'minio_object_name',
            'tipo_documento', 'tema_principal', 'fecha_documento', 
            'entidades_clave', 'resumen_corto', 'file_size_bytes',
            'content_type', 'num_pages', 'upload_timestamp', 
            'created_at', 'updated_at', 'processed_at', 'created_by',
            'status', 'error_message'
        ]
        
        for field in expected_documento_fields:
            if not hasattr(Documento, field):
                raise AttributeError(f"Documento model missing field: {field}")
        
        print("✓ Documento model has all expected fields")
        
        # Check AuditLog model
        expected_audit_fields = ['id', 'documento_id', 'action', 'old_values', 'new_values', 'user_id', 'timestamp']
        for field in expected_audit_fields:
            if not hasattr(AuditLog, field):
                raise AttributeError(f"AuditLog model missing field: {field}")
        
        print("✓ AuditLog model has all expected fields")
        
        # Validate schema constraints
        documento_constraints = Documento.__table_args__
        constraint_names = [c.name for c in documento_constraints if hasattr(c, 'name')]
        
        if 'valid_status' not in constraint_names:
            raise ValueError("Missing valid_status constraint")
        if 'valid_tipo_documento' not in constraint_names:
            raise ValueError("Missing valid_tipo_documento constraint")
            
        print("✓ Documento model has required constraints")
        
        # Check that schemas can be instantiated
        metadata = DocumentoMetadata(tipo_documento="Oficio", tema_principal="Test")
        print("✓ DocumentoMetadata schema works")
        
        update_schema = DocumentoUpdate(tipo_documento="Informe")
        print("✓ DocumentoUpdate schema works")
        
        print("\n🎉 All validations passed! Schema changes are correct.")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_migration_file():
    """Validate that the migration file is syntactically correct"""
    try:
        migration_path = os.path.join(os.path.dirname(__file__), 'alembic', 'versions', '002_sgd_enhancements.py')
        
        if not os.path.exists(migration_path):
            raise FileNotFoundError(f"Migration file not found: {migration_path}")
        
        # Try to compile the migration file
        with open(migration_path, 'r', encoding='utf-8') as f:
            migration_code = f.read()
        
        compile(migration_code, migration_path, 'exec')
        print("✓ Migration file is syntactically correct")
        
        # Check for required functions
        if 'def upgrade()' not in migration_code:
            raise ValueError("Migration missing upgrade() function")
        if 'def downgrade()' not in migration_code:
            raise ValueError("Migration missing downgrade() function")
            
        print("✓ Migration file has required functions")
        
        # Check for key operations
        required_operations = [
            'add_column',
            'create_check_constraint', 
            'create_table',
            'create_index'
        ]
        
        for op in required_operations:
            if op not in migration_code:
                print(f"⚠️  Warning: Migration may be missing {op} operation")
        
        print("✓ Migration file structure looks good")
        return True
        
    except Exception as e:
        print(f"❌ Migration validation failed: {e}")
        return False

def main():
    """Run all validations"""
    print("Validating SGD schema changes...\n")
    
    models_ok = validate_models()
    migration_ok = validate_migration_file()
    
    if models_ok and migration_ok:
        print("\n✅ All schema changes validated successfully!")
        print("The database schema updates are ready to be applied.")
        return 0
    else:
        print("\n❌ Schema validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())