#core/utils.py
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user
from core.extensions import db
from core.models import ActivityLog

def track_activity(f):
    """Decorator to track user activity"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real system, we'd log the activity
        # For now, just pass
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action, target):
    log = ActivityLog(user_id=user_id, action=action, target=target)
    db.session.add(log)
    db.session.commit()