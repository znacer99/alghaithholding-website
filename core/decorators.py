# core/decoratos.py
from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from core.permissions import Permission
            
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
                
            if not Permission.check(current_user.role, permission):
                current_app.logger.warning(
                    f"Permission denied for {current_user.email} "
                    f"(role: {current_user.role}) "
                    f"(required: {permission})"
                )
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
                
            # Ensure roles is a list
            required_roles = [r.lower() for r in roles] if isinstance(roles, list) else [roles.lower()]
            if current_user.role.lower() not in required_roles:
                current_app.logger.warning(
                    f"Role access denied for {current_user.email} "
                    f"(role: {current_user.role}) - required: {required_roles}"
                )
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator