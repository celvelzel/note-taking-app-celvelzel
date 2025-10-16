"""
Database migration script for adding translation and quiz fields to Note model.

This script can be run directly to apply the migration to the database.
Make sure DATABASE_URL environment variable is set before running.

Usage:
    python migrations/migrate_add_fields.py
"""

import os
import sys

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from src.models.user import db
from src.main import app


def apply_migration():
    """Apply the migration to add translation and quiz fields to note table."""
    
    migration_sql = """
    -- Add translation fields
    ALTER TABLE note ADD COLUMN IF NOT EXISTS translations TEXT;
    ALTER TABLE note ADD COLUMN IF NOT EXISTS translation_updated_at TIMESTAMP;
    
    -- Add quiz fields
    ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_question TEXT;
    ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_options TEXT;
    ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_answer VARCHAR(50);
    ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_explanation TEXT;
    ALTER TABLE note ADD COLUMN IF NOT EXISTS quiz_generated_at TIMESTAMP;
    """
    
    print("Starting migration: Add translation and quiz fields to note table")
    print("=" * 70)
    
    with app.app_context():
        try:
            # Get database connection
            connection = db.engine.connect()
            
            # Execute migration in a transaction
            trans = connection.begin()
            try:
                # Split and execute each statement
                for statement in migration_sql.strip().split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        print(f"Executing: {statement[:60]}...")
                        connection.execute(text(statement))
                
                trans.commit()
                print("=" * 70)
                print("✅ Migration completed successfully!")
                print("\nThe following fields have been added to the 'note' table:")
                print("  - translations (TEXT)")
                print("  - translation_updated_at (TIMESTAMP)")
                print("  - quiz_question (TEXT)")
                print("  - quiz_options (TEXT)")
                print("  - quiz_answer (VARCHAR(50))")
                print("  - quiz_explanation (TEXT)")
                print("  - quiz_generated_at (TIMESTAMP)")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {str(e)}")
                raise
            finally:
                connection.close()
                
        except Exception as e:
            print(f"❌ Error connecting to database: {str(e)}")
            print("\nMake sure DATABASE_URL environment variable is set correctly.")
            sys.exit(1)


if __name__ == "__main__":
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        print("\nPlease set DATABASE_URL to your database connection string:")
        print("  Example: postgresql://user:password@host:port/database")
        sys.exit(1)
    
    print(f"Database: {database_url.split('@')[-1] if '@' in database_url else 'local'}")
    print()
    
    # Confirm before proceeding
    response = input("Do you want to proceed with the migration? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        sys.exit(0)
    
    print()
    apply_migration()
