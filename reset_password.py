# reset_password.py
from core.extensions import db
from core.models import User
from core.extensions import set_password

def reset_passwords():
    # Create app context manually
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Reset admin password
        admin = User.query.filter_by(email='admin@alghaith.com').first()
        if admin:
            admin.password_hash = set_password('SecureAdmin123!')
            print(f"✅ Reset password for {admin.email}")
        
        # Add any other users here
        # user2 = User.query.filter_by(email='...').first()
        # if user2: ...
        
        db.session.commit()
        print("✅ All passwords reset successfully!")

if __name__ == "__main__":
    reset_passwords()