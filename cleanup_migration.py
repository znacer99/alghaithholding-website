# cleanup_migration.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.extensions import db
from app import create_app

app = create_app()

def cleanup_migration():
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Check if the temporary table exists and drop it
                print("Checking for leftover temporary tables...")
                
                # List all tables to see what exists
                result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                print("Current tables:", tables)
                
                # Drop the temporary table if it exists
                if '_alembic_tmp_candidates' in tables:
                    print("Dropping leftover temporary table '_alembic_tmp_candidates'...")
                    conn.execute(db.text('DROP TABLE _alembic_tmp_candidates'))
                    conn.commit()
                    print("✅ Temporary table dropped")
                else:
                    print("✅ No leftover temporary table found")
                    
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    cleanup_migration()