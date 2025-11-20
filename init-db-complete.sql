-- ============================================================================
-- SGD UGEL Ilo - Complete Database Initialization
-- PostgreSQL 15+ with pgvector extension
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: documentos (Enhanced with SGD Enhancements)
-- ============================================================================

CREATE TABLE IF NOT EXISTS documentos (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- File information
    filename VARCHAR(255) NOT NULL,
    minio_url TEXT NOT NULL,
    minio_object_name VARCHAR(500) NOT NULL,
    
    -- Metadata extracted by Gemini LLM
    tipo_documento VARCHAR(100),
    tema_principal TEXT,
    fecha_documento DATE,
    entidades_clave TEXT[],  -- Array of strings
    resumen_corto TEXT,
    
    -- System metadata
    file_size_bytes BIGINT NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    num_pages INTEGER,
    
    -- Enhanced timestamps and tracking (SGD Enhancements)
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMP,
    created_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'processing' NOT NULL,
    error_message TEXT,
    
    -- Constraints (Enhanced with strict category validation)
    CONSTRAINT valid_status CHECK (status IN ('processing', 'completed', 'error')),
    CONSTRAINT valid_tipo_documento CHECK (tipo_documento IN (
        'Oficio', 'Oficio Múltiple', 'Resolución Directorial', 
        'Informe', 'Solicitud', 'Memorándum', 'Acta', 'Varios'
    ) OR tipo_documento IS NULL)
);

-- ============================================================================
-- Table: fragmentos
-- ============================================================================

CREATE TABLE IF NOT EXISTS fragmentos (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to documentos (CASCADE DELETE)
    documento_id UUID NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    
    -- Fragment content
    texto TEXT NOT NULL,
    posicion INTEGER NOT NULL,  -- Order/position in the document
    
    -- Vector embedding (768 dimensions for text-embedding-004)
    embedding vector(768) NOT NULL,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================================================
-- Table: audit_log (New from SGD Enhancements)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to documentos (CASCADE DELETE)
    documento_id UUID NOT NULL REFERENCES documentos(id) ON DELETE CASCADE,
    
    -- Action information
    action VARCHAR(20) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
    old_values JSONB,           -- Previous values (for UPDATE/DELETE)
    new_values JSONB,           -- New values (for CREATE/UPDATE)
    user_id VARCHAR(100),       -- User who performed the action
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT valid_audit_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE'))
);

-- ============================================================================
-- Indexes
-- ============================================================================

-- Indexes for documentos table
CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_documentos_fecha ON documentos(fecha_documento);
CREATE INDEX IF NOT EXISTS idx_documentos_status ON documentos(status);
CREATE INDEX IF NOT EXISTS idx_documentos_created ON documentos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documentos_updated ON documentos(updated_at DESC);

-- Indexes for fragmentos table
-- HNSW index for fast vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_fragmentos_embedding ON fragmentos 
USING hnsw (embedding vector_cosine_ops);

-- B-tree index for documento_id lookups
CREATE INDEX IF NOT EXISTS idx_fragmentos_documento ON fragmentos(documento_id);

-- Indexes for audit_log table
CREATE INDEX IF NOT EXISTS idx_audit_log_documento ON audit_log(documento_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);

-- ============================================================================
-- Permissions
-- ============================================================================

-- Grant permissions to sgd_user
GRANT ALL PRIVILEGES ON DATABASE sgd_ugel TO sgd_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO sgd_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sgd_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sgd_user;

-- Message
SELECT 'SGD Database initialized with all enhancements' as status;