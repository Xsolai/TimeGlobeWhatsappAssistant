"""
Run Alembic migrations to update the database schema.
"""

import subprocess
import sys
import os

def run_migration():
    print("Running database migrations...")
    try:
        # Run Alembic upgrade command
        result = subprocess.run(
            ["alembic", "upgrade", "head"], 
            capture_output=True, 
            text=True,
            check=True
        )
        print("Migration output:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
            
        print("Migration completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Migration failed with error code {e.returncode}")
        print("Error output:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1) 