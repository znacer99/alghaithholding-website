# scripts/reset_db.py
from app import create_app, initialize_database
from core.extensions import db
from core.models import *  # import all models

app = create_app()

with app.app_context():
    print("⚠️ Dropping all tables...")
    db.drop_all()

    print("✅ Creating all tables...")
    db.create_all()

    print("🌱 Initializing default data...")
    initialize_database()

    print("🎉 Database reset complete!")
