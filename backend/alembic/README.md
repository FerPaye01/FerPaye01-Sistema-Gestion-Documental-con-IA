# Alembic Migrations

This directory contains database migration scripts for the SGD UGEL Ilo project.

## Migration Files

- `env.py`: Alembic environment configuration
- `script.py.mako`: Template for generating new migration files
- `versions/`: Directory containing migration scripts

## Current Migrations

### 001_initial_schema.py

**Revision ID:** 001  
**Created:** 2024-01-15

**Changes:**
- Enables pgvector extension
- Creates `documentos` table with metadata fields
- Creates `fragmentos` table with vector embeddings
- Creates all necessary indexes:
  - B-tree indexes on documentos (tipo, fecha, status, created_at)
  - HNSW index on fragmentos.embedding for vector similarity search
  - B-tree index on fragmentos.documento_id

## Running Migrations

### Apply All Pending Migrations

```bash
alembic upgrade head
```

### Rollback Last Migration

```bash
alembic downgrade -1
```

### Rollback All Migrations

```bash
alembic downgrade base
```

### View Migration History

```bash
alembic history
```

### View Current Migration

```bash
alembic current
```

## Creating New Migrations

### Auto-generate Migration from Model Changes

```bash
# After modifying models in app/models/
alembic revision --autogenerate -m "Description of changes"
```

This will:
1. Compare current database schema with SQLAlchemy models
2. Generate a new migration file in `versions/`
3. Include detected changes (new tables, columns, indexes, etc.)

**Important:** Always review auto-generated migrations before applying them!

### Create Empty Migration

```bash
alembic revision -m "Description of changes"
```

Then manually edit the generated file to add upgrade/downgrade logic.

## Migration Best Practices

1. **Always review auto-generated migrations** - Alembic may not detect all changes correctly
2. **Test migrations on a copy of production data** before applying to production
3. **Write reversible migrations** - Always implement both upgrade() and downgrade()
4. **Use transactions** - Migrations run in a transaction by default
5. **Avoid data migrations in schema migrations** - Separate data changes from schema changes
6. **Document complex migrations** - Add comments explaining non-obvious changes

## Common Migration Patterns

### Adding a Column

```python
def upgrade():
    op.add_column('table_name', 
        sa.Column('new_column', sa.String(100), nullable=True)
    )

def downgrade():
    op.drop_column('table_name', 'new_column')
```

### Adding an Index

```python
def upgrade():
    op.create_index('idx_name', 'table_name', ['column_name'])

def downgrade():
    op.drop_index('idx_name', table_name='table_name')
```

### Modifying a Column

```python
def upgrade():
    op.alter_column('table_name', 'column_name',
        type_=sa.String(200),
        existing_type=sa.String(100)
    )

def downgrade():
    op.alter_column('table_name', 'column_name',
        type_=sa.String(100),
        existing_type=sa.String(200)
    )
```

## Troubleshooting

### "Target database is not up to date"

```bash
# Check current version
alembic current

# Stamp database to specific version
alembic stamp head
```

### "Can't locate revision identified by 'xxx'"

This usually means the migration file was deleted or the database has a reference to a non-existent migration.

```bash
# Reset to base and re-apply
alembic downgrade base
alembic upgrade head
```

### Migration Fails Midway

If a migration fails, Alembic will rollback the transaction. Fix the issue and run `alembic upgrade head` again.

For migrations that can't be rolled back automatically:
1. Manually fix the database state
2. Stamp the database to the correct version: `alembic stamp <revision>`

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
