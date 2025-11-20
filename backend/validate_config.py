#!/usr/bin/env python3
"""
Configuration Validation Script for SGD UGEL Ilo

This script validates that all required environment variables are properly set
and that external services (PostgreSQL, Redis, MinIO) are accessible.

Usage:
    python validate_config.py
    
Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import os
import sys
from typing import Dict, List, Tuple
from urllib.parse import urlparse

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")


def check_required_env_vars() -> Tuple[bool, List[str]]:
    """Check if all required environment variables are set"""
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string',
        'REDIS_URL': 'Redis connection URL',
        'MINIO_ENDPOINT': 'MinIO server endpoint',
        'MINIO_ACCESS_KEY': 'MinIO access key',
        'MINIO_SECRET_KEY': 'MinIO secret key',
        'MINIO_BUCKET': 'MinIO bucket name',
        'GOOGLE_API_KEY': 'Google API key for Gemini and embeddings',
    }
    
    missing_vars = []
    invalid_vars = []
    
    print_header("CHECKING REQUIRED ENVIRONMENT VARIABLES")
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print_error(f"{var} is not set ({description})")
            missing_vars.append(var)
        elif value == f"your_{var.lower()}_here" or value == "your_google_api_key_here":
            print_error(f"{var} has placeholder value ({description})")
            invalid_vars.append(var)
        else:
            print_success(f"{var} is set")
    
    return len(missing_vars) == 0 and len(invalid_vars) == 0, missing_vars + invalid_vars


def check_optional_env_vars() -> Dict[str, bool]:
    """Check optional environment variables and provide warnings"""
    optional_vars = {
        'POSTGRES_POOL_SIZE': '20',
        'LOG_LEVEL': 'INFO',
        'MAX_UPLOAD_SIZE_MB': '50',
        'CELERY_WORKER_CONCURRENCY': '2',
        'CHUNK_SIZE': '800',
        'CHUNK_OVERLAP': '100',
    }
    
    print_header("CHECKING OPTIONAL ENVIRONMENT VARIABLES")
    
    results = {}
    for var, default in optional_vars.items():
        value = os.getenv(var)
        if not value:
            print_warning(f"{var} not set, will use default: {default}")
            results[var] = False
        else:
            print_success(f"{var} = {value}")
            results[var] = True
    
    return results


def validate_database_url() -> bool:
    """Validate DATABASE_URL format"""
    print_header("VALIDATING DATABASE CONFIGURATION")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print_error("DATABASE_URL not set")
        return False
    
    try:
        parsed = urlparse(db_url)
        if parsed.scheme not in ['postgresql', 'postgres']:
            print_error(f"Invalid database scheme: {parsed.scheme} (expected postgresql)")
            return False
        
        if not parsed.hostname:
            print_error("Database hostname not specified")
            return False
        
        if not parsed.path or parsed.path == '/':
            print_error("Database name not specified")
            return False
        
        print_success(f"Database URL format is valid")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port or 5432}")
        print(f"  Database: {parsed.path[1:]}")
        print(f"  User: {parsed.username}")
        
        return True
    except Exception as e:
        print_error(f"Failed to parse DATABASE_URL: {e}")
        return False


def validate_redis_url() -> bool:
    """Validate REDIS_URL format"""
    print_header("VALIDATING REDIS CONFIGURATION")
    
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print_error("REDIS_URL not set")
        return False
    
    try:
        parsed = urlparse(redis_url)
        if parsed.scheme != 'redis':
            print_error(f"Invalid Redis scheme: {parsed.scheme} (expected redis)")
            return False
        
        if not parsed.hostname:
            print_error("Redis hostname not specified")
            return False
        
        print_success(f"Redis URL format is valid")
        print(f"  Host: {parsed.hostname}")
        print(f"  Port: {parsed.port or 6379}")
        print(f"  Database: {parsed.path[1:] if parsed.path else '0'}")
        
        return True
    except Exception as e:
        print_error(f"Failed to parse REDIS_URL: {e}")
        return False


def validate_minio_config() -> bool:
    """Validate MinIO configuration"""
    print_header("VALIDATING MINIO CONFIGURATION")
    
    endpoint = os.getenv('MINIO_ENDPOINT')
    access_key = os.getenv('MINIO_ACCESS_KEY')
    secret_key = os.getenv('MINIO_SECRET_KEY')
    bucket = os.getenv('MINIO_BUCKET')
    secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
    
    all_valid = True
    
    if not endpoint:
        print_error("MINIO_ENDPOINT not set")
        all_valid = False
    else:
        print_success(f"MinIO endpoint: {endpoint}")
    
    if not access_key or access_key == 'minioadmin':
        print_warning("Using default MinIO access key (change in production!)")
    else:
        print_success("MinIO access key is set")
    
    if not secret_key or secret_key == 'minioadmin':
        print_warning("Using default MinIO secret key (change in production!)")
    else:
        print_success("MinIO secret key is set")
    
    if not bucket:
        print_error("MINIO_BUCKET not set")
        all_valid = False
    else:
        print_success(f"MinIO bucket: {bucket}")
    
    print(f"  Secure connection: {secure}")
    
    return all_valid


def validate_google_api_key() -> bool:
    """Validate Google API key"""
    print_header("VALIDATING GOOGLE AI CONFIGURATION")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print_error("GOOGLE_API_KEY not set")
        return False
    
    if api_key == 'your_google_api_key_here':
        print_error("GOOGLE_API_KEY has placeholder value")
        print("  Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    if len(api_key) < 20:
        print_warning("GOOGLE_API_KEY seems too short, verify it's correct")
    
    print_success("Google API key is set")
    print(f"  Key length: {len(api_key)} characters")
    
    gemini_model = os.getenv('GEMINI_MODEL', 'gemini-pro')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'models/text-embedding-004')
    
    print(f"  Gemini model: {gemini_model}")
    print(f"  Embedding model: {embedding_model}")
    
    return True


def test_database_connection() -> bool:
    """Test actual database connection"""
    print_header("TESTING DATABASE CONNECTION")
    
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print_error("DATABASE_URL not set, skipping connection test")
            return False
        
        print("Attempting to connect to PostgreSQL...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_success("Connected to PostgreSQL")
        print(f"  Version: {version.split(',')[0]}")
        
        # Check pgvector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cursor.fetchone():
            print_success("pgvector extension is installed")
        else:
            print_warning("pgvector extension not found (run: CREATE EXTENSION vector;)")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print_warning("psycopg2 not installed, skipping database connection test")
        print("  Install with: pip install psycopg2-binary")
        return True  # Don't fail if library not installed
    except OperationalError as e:
        print_error(f"Failed to connect to database: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error testing database: {e}")
        return False


def test_redis_connection() -> bool:
    """Test actual Redis connection"""
    print_header("TESTING REDIS CONNECTION")
    
    try:
        import redis
        
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print_error("REDIS_URL not set, skipping connection test")
            return False
        
        print("Attempting to connect to Redis...")
        r = redis.from_url(redis_url)
        r.ping()
        
        print_success("Connected to Redis")
        
        # Get Redis info
        info = r.info()
        print(f"  Version: {info.get('redis_version', 'unknown')}")
        print(f"  Used memory: {info.get('used_memory_human', 'unknown')}")
        
        return True
        
    except ImportError:
        print_warning("redis library not installed, skipping Redis connection test")
        print("  Install with: pip install redis")
        return True  # Don't fail if library not installed
    except Exception as e:
        print_error(f"Failed to connect to Redis: {e}")
        return False


def test_minio_connection() -> bool:
    """Test actual MinIO connection"""
    print_header("TESTING MINIO CONNECTION")
    
    try:
        from minio import Minio
        
        endpoint = os.getenv('MINIO_ENDPOINT')
        access_key = os.getenv('MINIO_ACCESS_KEY')
        secret_key = os.getenv('MINIO_SECRET_KEY')
        bucket = os.getenv('MINIO_BUCKET')
        secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        
        if not all([endpoint, access_key, secret_key, bucket]):
            print_error("MinIO configuration incomplete, skipping connection test")
            return False
        
        print("Attempting to connect to MinIO...")
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        # Check if bucket exists
        if client.bucket_exists(bucket):
            print_success(f"Connected to MinIO and bucket '{bucket}' exists")
        else:
            print_warning(f"Connected to MinIO but bucket '{bucket}' does not exist")
            print(f"  Bucket will be created automatically on first upload")
        
        return True
        
    except ImportError:
        print_warning("minio library not installed, skipping MinIO connection test")
        print("  Install with: pip install minio")
        return True  # Don't fail if library not installed
    except Exception as e:
        print_error(f"Failed to connect to MinIO: {e}")
        return False


def main():
    """Main validation function"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{'SGD UGEL ILO - CONFIGURATION VALIDATOR'.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")
    
    all_passed = True
    
    # Check environment variables
    env_valid, missing = check_required_env_vars()
    all_passed = all_passed and env_valid
    
    check_optional_env_vars()
    
    # Validate configuration formats
    all_passed = all_passed and validate_database_url()
    all_passed = all_passed and validate_redis_url()
    all_passed = all_passed and validate_minio_config()
    all_passed = all_passed and validate_google_api_key()
    
    # Test actual connections (optional, may fail if services not running)
    print("\n" + "=" * 80)
    print("TESTING SERVICE CONNECTIONS (optional - services may not be running)")
    print("=" * 80)
    
    db_connected = test_database_connection()
    redis_connected = test_redis_connection()
    minio_connected = test_minio_connection()
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    if all_passed:
        print_success("All required configuration checks passed!")
        if not all([db_connected, redis_connected, minio_connected]):
            print_warning("Some service connections failed (services may not be running)")
            print("  Start services with: docker-compose up -d")
    else:
        print_error("Configuration validation failed!")
        if missing:
            print("\nMissing or invalid variables:")
            for var in missing:
                print(f"  - {var}")
        print("\nPlease fix the issues above and run validation again.")
    
    print()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
