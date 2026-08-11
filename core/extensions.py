#core/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash  # Correct import
from flask import current_app
from flask_babel import Babel

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
babel = Babel()

# Password hashing
ph = PasswordHasher()

def set_password(password):
    return ph.hash(password)

def verify_password(password_hash, password):
    try:
        return ph.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHash):  # Fixed exception name
        return False
    except Exception as e:
        # Log unexpected errors
        current_app.logger.error(f"Password verification error: {str(e)}")
        return False

@login_manager.user_loader
def load_user(user_id):
    from core.models import User  # Avoid circular import
    return User.query.get(int(user_id))