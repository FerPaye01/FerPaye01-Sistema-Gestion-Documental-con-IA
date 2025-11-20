"""SGD Enhancements: Add timestamp fields, category validation, and audit log

Revision ID: 002
Revises: 001
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to documentos table
    op.add_column('documentos', sa.Column('upload_timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False))
    op.add_column('documentos', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False))
    op.add_column('documentos', sa.Column('created_by', sa.String(100), nullable=True))
    
    # Update existing records to have upload_timestamp = created_at
    op.execute('UPDATE documentos SET upload_timestamp = created_at WHERE upload_timestamp IS NULL')
    op.execute('UPDATE documentos SET updated_at = created_at WHERE updated_at IS NULL')
    
    # Drop the old status constraint
    op.drop_constraint('valid_status', 'documentos', type_='check')
    
    # Add new constraint for tipo_documento with allowed categories
    op.create_check_constraint(
        'valid_tipo_documento',
        'documentos',
        "tipo_documento IN ('Oficio', 'Oficio Múltiple', 'Resolución Directorial', 'Informe', 'Solicitud', 'Memorándum', 'Acta', 'Varios') OR tipo_documento IS NULL"
    )
    
    # Re-add the status constraint
    op.create_check_constraint(
        'valid_status',
        'documentos',
        "status IN ('processing', 'completed', 'error')"
    )
    
    # Create audit_log table for change tracking
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('documento_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),  # 'CREATE', 'UPDATE', 'DELETE'
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        
        sa.ForeignKeyConstraint(['documento_id'], ['documentos.id'], ondelete='CASCADE'),
        sa.CheckConstraint("action IN ('CREATE', 'UPDATE', 'DELETE')", name='valid_audit_action')
    )
    
    # Create indexes for audit_log table
    op.create_index('idx_audit_log_documento', 'audit_log', ['documento_id'])
    op.create_index('idx_audit_log_timestamp', 'audit_log', [sa.text('timestamp DESC')])
    op.create_index('idx_audit_log_action', 'audit_log', ['action'])
    
    # Create index for updated_at to support ordering by last modified
    op.create_index('idx_documentos_updated', 'documentos', [sa.text('updated_at DESC')])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_documentos_updated', table_name='documentos')
    op.drop_index('idx_audit_log_action', table_name='audit_log')
    op.drop_index('idx_audit_log_timestamp', table_name='audit_log')
    op.drop_index('idx_audit_log_documento', table_name='audit_log')
    
    # Drop audit_log table
    op.drop_table('audit_log')
    
    # Drop constraints
    op.drop_constraint('valid_tipo_documento', 'documentos', type_='check')
    op.drop_constraint('valid_status', 'documentos', type_='check')
    
    # Re-add original status constraint
    op.create_check_constraint(
        'valid_status',
        'documentos',
        "status IN ('processing', 'completed', 'error')"
    )
    
    # Drop new columns
    op.drop_column('documentos', 'created_by')
    op.drop_column('documentos', 'updated_at')
    op.drop_column('documentos', 'upload_timestamp')