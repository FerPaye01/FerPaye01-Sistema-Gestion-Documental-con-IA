# Database Setup Guide

## Prerequisites

- PostgreSQL 15+ with pgvector extension installed
- Python environment with dependencies from requirements.txt
- Docker and Docker Compose (recommended for development)

## Quick Start with Docker

The easiest way to set up the database is using Docker Compose:

```bash
# Start all services (PostgreSQL, Redis, MinIO)
docker-compose up -d postgres redis minio

# Wait for PostgreSQL to be ready (check health status)
docker-compose ps

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify schema
docker-compose exec backend python verify_schema.py
```

## Manual Setup (Without Docker)

### 1. Install PostgreSQL with pgvector

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-15 postgresql-15-pgvector
```

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew install pgvector
```

**Windows:**
Download PostgreSQL 15+ from https://www.postgresql.org/download/windows/
Then install pgvector extension manually.

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE sgd_ugel;
CREATE USER sgd_user WITH PASSWORD 'sgd_pass';
GRANT ALL PRIVILEGES ON DATABASE sgd_ugel TO sgd_user;

# Connect to the new database
\c sgd_ugel

# Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Exit psql
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://sgd_user:sgd_pass@localhost:5432/sgd_ugel
POSTGRES_POOL_SIZE=20

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=documentos-ugel
MINIO_SECURE=false

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Application Configuration
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE_MB=50
```

### 4. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Run Database Migrations

Apply the initial schema migration:

```bash
# From the backend directory
alembic upgrade head
```

This will:
- Enable the pgvector extension (if not already enabled)
- Create the `documentos` table with metadata fields
- Create the `fragmentos` table with vector embeddings (768 dimensions)
- Create all necessary indexes:
  - HNSW index on embeddings for fast cosine similarity search
  - B-tree indexes on tipo_documento, fecha_documento, status, created_at
  - B-tree index on documento_id in fragmentos table

### 6. Verify Setup

Run the verification script:

```bash
python verify_schema.py
```

Or manually verify using psql:

```sql
-- Connect to your database
psql -U sgd_user -d sgd_ugel

-- Check tables
\dt

-- Check pgvector extension
\dx vector

-- Verify documentos table structure
\d documentos

-- Verify fragmentos table structure
\d fragmentos

-- Check indexes
\di

-- Test vector operations
SELECT '[0.1,0.2,0.3]'::vector(3) <=> '[0.1,0.2,0.3]'::vector(3);
```

## Database Schema

### documentos Table

Stores document metadata and processing status:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key (auto-generated) |
| `filename` | VARCHAR(255) | NO | Original filename |
| `minio_url` | TEXT | NO | Pre-signed URL for file access |
| `minio_object_name` | VARCHAR(500) | NO | Object key in MinIO |
| `tipo_documento` | VARCHAR(100) | YES | Document type (extracted by Gemini) |
| `tema_principal` | TEXT | YES | Main topic (extracted by Gemini) |
| `fecha_documento` | DATE | YES | Document date (extracted by Gemini) |
| `entidades_clave` | TEXT[] | YES | Key entities array (extracted by Gemini) |
| `resumen_corto` | TEXT | YES | Short summary (extracted by Gemini) |
| `file_size_bytes` | BIGINT | NO | File size in bytes |
| `content_type` | VARCHAR(50) | NO | MIME type (application/pdf, image/jpeg) |
| `num_pages` | INTEGER | YES | Number of pages (for PDFs) |
| `created_at` | TIMESTAMP | NO | Upload timestamp |
| `processed_at` | TIMESTAMP | YES | Processing completion timestamp |
| `status` | VARCHAR(20) | NO | Processing status (processing/completed/error) |
| `error_message` | TEXT | YES | Error details if processing failed |

**Constraints:**
- CHECK constraint on status: must be 'processing', 'completed', or 'error'

**Indexes:**
- `idx_documentos_tipo`: B-tree on tipo_documento
- `idx_documentos_fecha`: B-tree on fecha_documento
- `idx_documentos_status`: B-tree on status
- `idx_documentos_created`: B-tree on created_at DESC

### fragmentos Table

Stores text chunks with vector embeddings for semantic search:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key (auto-generated) |
| `documento_id` | UUID | NO | Foreign key to documentos (CASCADE DELETE) |
| `texto` | TEXT | NO | Text content of the fragment |
| `posicion` | INTEGER | NO | Position/order in the document |
| `embedding` | vector(768) | NO | 768-dimensional embedding (text-embedding-004) |
| `created_at` | TIMESTAMP | NO | Creation timestamp |

**Constraints:**
- Foreign key to documentos.id with ON DELETE CASCADE

**Indexes:**
- `idx_fragmentos_embedding`: HNSW index on embedding using vector_cosine_ops
- `idx_fragmentos_documento`: B-tree on documento_id

### Index Details

**HNSW Index (Hierarchical Navigable Small World):**
- Used for fast approximate nearest neighbor search
- Optimized for cosine similarity (<=> operator)
- Better performance than IVFFlat for medium-sized datasets
- Trade-off: slightly larger index size for faster queries

**Why HNSW over IVFFlat:**
- No need for training data
- Better recall at similar query speeds
- More consistent performance across different query patterns
- Recommended for datasets with < 1M vectors

## Example Queries

### Semantic Search Query

```sql
-- Search for documents similar to a query vector
-- Note: Lower distance = more similar (0 = identical)
SELECT 
    f.documento_id,
    d.filename,
    d.tipo_documento,
    d.tema_principal,
    d.resumen_corto,
    (f.embedding <=> :query_vector) AS similitud
FROM fragmentos f
JOIN documentos d ON f.documento_id = d.id
WHERE d.status = 'completed'
ORDER BY similitud ASC
LIMIT 5;
```

### Filter by Document Type and Date

```sql
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
```

### Get Processing Statistics

```sql
SELECT 
    status,
    COUNT(*) as count,
    AVG(file_size_bytes) as avg_size_bytes,
    AVG(num_pages) as avg_pages
FROM documentos
GROUP BY status;
```

### Get All Fragments for a Document

```sql
SELECT 
    id,
    texto,
    posicion
FROM fragmentos
WHERE documento_id = :documento_id
ORDER BY posicion ASC;
```

## Future Migrations

To create a new migration after model changes:

```bash
# Generate migration automatically based on model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Apply the migration
alembic upgrade head
```

## Rollback

To rollback the last migration:

```bash
alembic downgrade -1
```

To rollback all migrations:

```bash
alembic downgrade base
```

To see migration history:

```bash
alembic history
alembic current
```

## Troubleshooting

### pgvector Extension Not Found

If you get an error about pgvector not being installed:

```bash
# Check if extension is available
psql -U sgd_user -d sgd_ugel -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# If not available, install pgvector for your PostgreSQL version
# See: https://github.com/pgvector/pgvector#installation
```

### Migration Conflicts

If you have migration conflicts:

```bash
# Check current migration state
alembic current

# Stamp the database to a specific revision
alembic stamp head

# Or start fresh (WARNING: drops all data)
alembic downgrade base
alembic upgrade head
```

### Connection Issues

If you can't connect to the database:

```bash
# Test connection
psql -U sgd_user -d sgd_ugel -h localhost -p 5432

# Check if PostgreSQL is running
docker-compose ps postgres  # If using Docker
# or
sudo systemctl status postgresql  # If using system PostgreSQL
```

### Performance Issues

If vector searches are slow:

```sql
-- Check index usage
EXPLAIN ANALYZE
SELECT embedding <=> '[0.1,0.2,...]'::vector(768) AS distance
FROM fragmentos
ORDER BY distance
LIMIT 5;

-- Rebuild HNSW index if needed
REINDEX INDEX idx_fragmentos_embedding;

-- Analyze table statistics
ANALYZE fragmentos;
```
