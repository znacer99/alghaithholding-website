# seed_database.py
from app import create_app
from core.extensions import db
from core.models import User, Department
from datetime import datetime

app = create_app()

with app.app_context():
    # Create departments
    departments = [
        Department(name="IT", description="Information Technology"),
        Department(name="Executive", description="Executive Leadership"),
        Department(name="HR", description="Human Resources"),
        Department(name="Operations", description="Company Operations")
    ]
    
    for dept in departments:
        existing = Department.query.filter_by(name=dept.name).first()
        if not existing:
            db.session.add(dept)
    
    db.session.commit()
    
    # Create test users
    users = [
        {
            "email": "it@alghaith.com",
            "password": "SecurePassword123!",
            "name": "IT Manager",
            "role": "IT Manager",
            "access_code": "IT-001",
            "department": "IT"
        },
        {
            "email": "director@alghaith.com",
            "password": "DirectorPass123!",
            "name": "General Director",
            "role": "General Director",
            "access_code": "GD-001",
            "department": "Executive"
        },
        {
            "email": "employee@alghaith.com",
            "password": "EmployeePass123!",
            "name": "John Employee",
            "role": "Employee",
            "access_code": "EE-001",
            "department": "Operations"
        }
    ]
    
    for user_data in users:
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            dept = Department.query.filter_by(name=user_data["department"]).first()
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                role=user_data["role"],
                access_code=user_data["access_code"],
                department_id=dept.id if dept else None,
                avatar=user_data["name"][0] + user_data["name"].split()[1][0]
            )
            user.set_password(user_data["password"])
            db.session.add(user)
    
    db.session.commit()
    print("Database seeded successfully!")