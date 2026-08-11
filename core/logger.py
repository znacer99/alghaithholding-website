#core/logger.py
from core.models import ActivityLog, db
from datetime import datetime

def audit_log(message, user_id=None, action="system"):
    if not user_id:
        from flask_login import current_user
        user_id = current_user.id if current_user.is_authenticated else None
    
    log_entry = ActivityLog(
        user_id=user_id,
        action=action,
        details=message,
        timestamp=datetime.utcnow()
    )
    db.session.add(log_entry)
    db.session.commit()