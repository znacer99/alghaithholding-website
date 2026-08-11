# rebuild_db.py
from app import create_app, db
from core.models import User, Department, ActivityLog, LeaveRequest, EmployeeDocument

app = create_app()

with app.app_context():
    # Drop any existing broken tables (optional)
    db.drop_all()
    print("Dropped old tables (if any).")

    # Create all tables from models
    db.create_all()
    print("Created all tables successfully!")

    # Initialize default departments
    departments = [
        Department(name="Executive Leadership", description="Company executives"),
        Department(name="IT Department", description="Technology team"),
        Department(name="Human Resources", description="HR team"),
        Department(name="Operations", description="Company operations")
    ]
    for dept in departments:
        if not Department.query.filter_by(name=dept.name).first():
            db.session.add(dept)
    db.session.commit()
    print("Departments added!")

print("✅ Database rebuilt successfully!")

