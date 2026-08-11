import os
from sqlalchemy import create_engine, inspect, text
from config import Config

# Show which DB we're touching
db_path = Config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
print(f"🔍 Using DB file: {db_path}")

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

def has_column(table, column):
    # Recreate inspector each time to avoid stale cache after ALTER TABLE
    cols = [c['name'] for c in inspect(engine).get_columns(table)]
    return column in cols

def add_column(table, column, ddl):
    if has_column(table, column):
        print(f"👌 Column '{column}' already exists in {table}.")
        return
    print(f"➕ Adding missing column '{column}' to {table}...")
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
    print(f"✅ Column '{column}' added to {table}.")

# Ensure columns on tables that your app queries
# users
add_column("users", "employee_id", "INTEGER")

# user_documents (based on your query log)
add_column("user_documents", "folder_id", "INTEGER")
add_column("user_documents", "user_id", "INTEGER", nullable=False, foreign_key="users.id")
add_column("user_documents", "visibility_type", "TEXT")
# SQLite allows DEFAULT in ADD COLUMN; we'll keep it nullable to be safe
add_column("user_documents", "uploaded_at", "DATETIME")

# Optional: backfill sane defaults where NULLs might exist
with engine.begin() as conn:
    # Set visibility_type if NULL
    conn.execute(text("""
        UPDATE user_documents
        SET visibility_type = 'private'
        WHERE visibility_type IS NULL
    """))
    # Set uploaded_at if NULL
    conn.execute(text("""
        UPDATE user_documents
        SET uploaded_at = CURRENT_TIMESTAMP
        WHERE uploaded_at IS NULL
    """))

# Show final schema for quick verification
def print_table_info(table):
    with engine.connect() as conn:
        rows = conn.execute(text(f"PRAGMA table_info('{table}')")).fetchall()
        print(f"\n📋 {table} columns:")
        for cid, name, ctype, notnull, dflt, pk in rows:
            print(f"  - {name} {ctype}")

print_table_info("users")
print_table_info("user_documents")

print("\n🎉 Schema check complete.")
