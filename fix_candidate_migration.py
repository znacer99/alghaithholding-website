# fix_candidate_migration.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.extensions import db
from app import create_app

app = create_app()

def fix_candidate_migration():
    with app.app_context():
        try:
            # Step 1: Handle existing NULL values in id_document_filepath
            print("Step 1: Handling NULL values in id_document_filepath...")
            
            # Use SQLAlchemy 2.0 syntax
            with db.engine.connect() as conn:
                # Update NULL values
                result = conn.execute(
                    db.text("UPDATE candidates SET id_document_filepath = 'pending_upload' WHERE id_document_filepath IS NULL")
                )
                conn.commit()
                print(f"✅ Updated {result.rowcount} records with NULL id_document_filepath")
                
                # Step 2: Verify no NULL values remain
                print("Step 2: Verifying no NULL values remain...")
                result = conn.execute(
                    db.text("SELECT COUNT(*) FROM candidates WHERE id_document_filepath IS NULL")
                )
                null_count = result.scalar()
                if null_count == 0:
                    print("✅ No NULL values remain in id_document_filepath")
                else:
                    print(f"❌ Still have {null_count} NULL values. Please check manually.")
                    return False
                    
            print("✅ Migration fix completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    fix_candidate_migration()