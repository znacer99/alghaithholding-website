#setup_db.py
from app import app
from core.extensions import db
from core.models import User, Department

with app.app_context():
    db.create_all()
    
    # Create initial data
    it_dept = Department(name='IT Department', description='Technology team')
    db.session.add(it_dept)
    
    it_manager = User(
        email='it@alghaith.com',
        name='IT Manager',
        role='it_manager',
        avatar='IT',
        access_code='IT-001',
        department=it_dept
    )
    it_manager.set_password('SecurePassword123!')
    db.session.add(it_manager)
    
    db.session.commit()
    print('Database initialized successfully!')
