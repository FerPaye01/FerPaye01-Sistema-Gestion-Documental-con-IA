"""Initial schema with documentos and fragmentos tables

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create documentos table
    op.create_table(
        'documentos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('minio_url', sa.Text(), nullable=False),
        sa.Column('minio_object_name', sa.String(500), nullable=False),
        
        # Metadatos extraídos por Gemini
        sa.Column('tipo_documento', sa.String(100), nullable=True),
        sa.Column('tema_principal', sa.Text(), nullable=True),
        sa.Column('fecha_documento', sa.Date(), nullable=True),
        sa.Column('entidades_clave', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('resumen_corto', sa.Text(), nullable=True),
        
        # Metadatos del sistema
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('num_pages', sa.Integer(), nullable=True),
        
        # Timestamps y estado
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('status', sa.String(20), server_default='processing', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        
        sa.CheckConstraint("status IN ('processing', 'completed', 'error')", name='valid_status')
    )
    
    # Create indexes for documentos table
    op.create_index('idx_documentos_tipo', 'documentos', ['tipo_documento'])
    op.create_index('idx_documentos_fecha', 'documentos', ['fecha_documento'])
    op.create_index('idx_documentos_status', 'documentos', ['status'])
    op.create_index('idx_documentos_created', 'documentos', [sa.text('created_at DESC')])
    
    # Create fragmentos table
    op.create_table(
        'fragmentos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('documento_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Contenido del fragmento
        sa.Column('texto', sa.Text(), nullable=False),
        sa.Column('posicion', sa.Integer(), nullable=False),
        
        # Vector de embedding (768 dimensiones para text-embedding-004)
        sa.Column('embedding', Vector(768), nullable=False),
        
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        
        sa.ForeignKeyConstraint(['documento_id'], ['documentos.id'], ondelete='CASCADE')
    )
    
    # Create indexes for fragmentos table
    # HNSW index for vector similarity search (faster than IVFFlat for medium datasets)
    op.execute('CREATE INDEX idx_fragmentos_embedding ON fragmentos USING hnsw (embedding vector_cosine_ops)')
    
    # B-tree index for documento_id lookups
    op.create_index('idx_fragmentos_documento', 'fragmentos', ['documento_id'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_fragmentos_documento', table_name='fragmentos')
    op.execute('DROP INDEX IF EXISTS idx_fragmentos_embedding')
    
    # Drop tables
    op.drop_table('fragmentos')
    
    op.drop_index('idx_documentos_created', table_name='documentos')
    op.drop_index('idx_documentos_status', table_name='documentos')
    op.drop_index('idx_documentos_fecha', table_name='documentos')
    op.drop_index('idx_documentos_tipo', table_name='documentos')
    op.drop_table('documentos')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS vector')
