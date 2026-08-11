# modules/leave/services.py
from datetime import datetime, date
from core.extensions import db
from core.models import LeaveRequest, User

def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def create_leave_request(user_id: int, payload: dict) -> LeaveRequest:
    """Create a new leave request"""
    lr = LeaveRequest(
        user_id=user_id,
        approver_id=payload.get('approver_id'),
        type=(payload.get('type') or 'annual').lower(),
        start_date=_parse_date(payload['start_date']),
        end_date=_parse_date(payload['end_date']),
        reason=payload.get('reason', '').strip(),
        status='pending'
    )
    db.session.add(lr)
    db.session.commit()
    return lr


def list_user_requests(user_id: int):
    """Return all leave requests of a specific user"""
    return LeaveRequest.query.filter_by(user_id=user_id).order_by(LeaveRequest.created_at.desc()).all()


def list_pending_requests(current_user: User):
    """Return pending leave requests relevant to the current approver"""
    # Managers / Head of Department: see requests where they are the approver
    if current_user.role in ['manager', 'head_of_department']:
        return LeaveRequest.query.filter_by(status='pending', approver_id=current_user.id)\
            .order_by(LeaveRequest.created_at.asc()).all()

    # IT Manager / General Director: see all pending requests
    elif current_user.role in ['it_manager', 'general_director']:
        return LeaveRequest.query.filter_by(status='pending').order_by(LeaveRequest.created_at.asc()).all()
    
    # Other roles: no access
    return []


def set_leave_status(lr_id: int, approver_id: int, status: str):
    """Approve or reject a leave request"""
    status = status.lower().strip()
    if status not in ('approved', 'rejected'):
        raise ValueError("Status must be 'approved' or 'rejected'")

    lr = LeaveRequest.query.get_or_404(lr_id)
    # Only allow the assigned approver to approve/reject
    if lr.approver_id != approver_id:
        raise PermissionError("You are not authorized to approve/reject this leave request.")

    lr.status = status
    lr.decided_at = datetime.utcnow()
    db.session.commit()
    return lr
