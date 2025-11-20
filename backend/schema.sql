-- ============================================================================
-- SGD UGEL Ilo - Database Schema
-- PostgreSQL 15+ with pgvector extension
-- ============================================================================

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Table: documentos
-- Purpose: Store document metadata and processing status
-- ============================================================================

CREATE TABLE documentos (
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
    
    -- Enhanced timestamps and tracking
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMP,
    created_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'processing' NOT NULL,
    error_message TEXT,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('processing', 'completed', 'error')),
    CONSTRAINT valid_tipo_documento CHECK (tipo_documento IN (
        'Oficio', 'Oficio Múltiple', 'Resolución Directorial', 
        'Informe', 'Solicitud', 'Memorándum', 'Acta', 'Varios'
    ) OR tipo_documento IS NULL)
);

-- Indexes for documentos table
CREATE INDEX idx_documentos_tipo ON documentos(tipo_documento);
CREATE INDEX idx_documentos_fecha ON documentos(fecha_documento);
CREATE INDEX idx_documentos_status ON documentos(status);
CREATE INDEX idx_documentos_created ON documentos(created_at DESC);
CREATE INDEX idx_documentos_updated ON documentos(updated_at DESC);

-- ============================================================================
-- Table: fragmentos
-- Purpose: Store text fragments with vector embeddings for semantic search
-- ============================================================================

CREATE TABLE fragmentos (
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

-- Indexes for fragmentos table
-- HNSW index for fast vector similarity search (cosine distance)
CREATE INDEX idx_fragmentos_embedding ON fragmentos 
USING hnsw (embedding vector_cosine_ops);

-- B-tree index for documento_id lookups
CREATE INDEX idx_fragmentos_documento ON fragmentos(documento_id);

-- ============================================================================
-- Table: audit_log
-- Purpose: Store audit trail of document changes for traceability
-- ============================================================================

CREATE TABLE audit_log (
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

-- Indexes for audit_log table
CREATE INDEX idx_audit_log_documento ON audit_log(documento_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- ============================================================================
-- Example Queries
-- ============================================================================

-- Search for similar documents using cosine similarity
-- Note: Lower distance = more similar (0 = identical)
/*
SELECT 
    f.documento_id,
    d.filename,
    d.tipo_documento,
    d.tema_principal,
    (f.embedding <=> :query_vector) AS similitud
FROM fragmentos f
JOIN documentos d ON f.documento_id = d.id
WHERE d.status = 'completed'
ORDER BY similitud ASC
LIMIT 5;
*/

-- Get all fragments for a specific document
/*
SELECT 
    id,
    texto,
    posicion
FROM fragmentos
WHERE documento_id = :documento_id
ORDER BY posicion ASC;
*/

-- Get documents by type and date range
/*
SELECT 
    id,
    filename,
    tipo_documento,
    tema_principal,
    fecha_documento,
    created_at
FROM documentos
WHERE status = 'completed'
    AND tipo_documento = 'Oficio Múltiple'
    AND fecha_documento BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY fecha_documento DESC;
*/

-- Get processing statistics
/*
SELECT 
    status,
    COUNT(*) as count,
    AVG(file_size_bytes) as avg_size_bytes
FROM documentos
GROUP BY status;
*/
