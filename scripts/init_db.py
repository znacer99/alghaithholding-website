#!/usr/bin/env python3
from app import create_app, initialize_database
from core.extensions import db

app = create_app()

def init_only():
    with app.app_context():
        db.create_all()
        initialize_database(app)
        print("✅ Database initialized and seeded (non-destructive).")

if __name__ == "__main__":
    init_only()
