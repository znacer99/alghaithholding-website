# reset_db.py
from app import create_app
from core.extensions import db
from core.models import User, Department

app = create_app()

with app.app_context():
    # Drop all tables (fresh start)
    db.drop_all()
    db.create_all()
    print("✅ Tables dropped and recreated")

    # ---------------- Departments ----------------
    departments_data = [
        {"name": "Executive Leadership", "description": "Company executives"},
        {"name": "IT Department", "description": "Technology team"},
        {"name": "Human Resources", "description": "HR team"},
        {"name": "Operations", "description": "Company operations"},
    ]

    departments = {}
    for d in departments_data:
        dept = Department(name=d["name"], description=d["description"])
        db.session.add(dept)
        db.session.flush()  # flush to assign dept.id
        departments[d["name"]] = dept
    db.session.commit()
    print("✅ Departments initialized")

    # ---------------- Users ----------------
    users_data = [
        {"email": "it@alghaith.com", "name": "IT Manager", "role": "it_manager", "dept": "IT Department", "access_code": "IT-001", "password": "SecurePassword123!"},
        {"email": "director@alghaith.com", "name": "General Director", "role": "general_director", "dept": "Executive Leadership", "access_code": "GD-001", "password": "DirectorPass123!"},
        {"email": "manager@alghaith.com", "name": "General Manager", "role": "general_manager", "dept": "Operations", "access_code": "GM-001", "password": "ManagerPass123!"},
        {"email": "hr@alghaith.com", "name": "Head of HR", "role": "head_of_department", "dept": "Human Resources", "access_code": "HR-001", "password": "HRPass123!"},
        {"email": "dept@alghaith.com", "name": "Department Manager", "role": "manager", "dept": "Operations", "access_code": "DM-001", "password": "DeptPass123!"},
        {"email": "employee@alghaith.com", "name": "Regular Employee", "role": "employee", "dept": "Operations", "access_code": "EE-001", "password": "EmployeePass123!"}
    ]

    for u in users_data:
        dept = departments[u["dept"]]
        user = User(
            email=u["email"],
            name=u["name"],
            role=u["role"],
            access_code=u["access_code"],
            department_id=dept.id,  # <-- use department_id to avoid TypeError
            avatar=u["name"][0] + u["name"].split()[-1][0],
            is_active=True,
            position="",
            phone=""
        )
        user.set_password(u["password"])
        db.session.add(user)

    db.session.commit()
    print("✅ Users initialized successfully!")
