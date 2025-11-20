#!/usr/bin/env python3
"""
Script to run Alembic migrations
"""
import sys
import os

def run_migration():
    """Run alembic upgrade head"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Import alembic after setting up the path
        from alembic import command
        from alembic.config import Config
        
        # Create alembic config
        alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))
        
        # Run upgrade
        command.upgrade(alembic_cfg, "head")
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()