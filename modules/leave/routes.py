# modules/leave/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import leave_bp
from .services import (
    create_leave_request,
    list_user_requests,
    list_pending_requests,
    set_leave_status,
)
from core.decorators import role_required
from core.forms import LeaveForm
from core.models import User


# --- UNIFIED LEAVES DASHBOARD ---
@leave_bp.route('/', methods=['GET', 'POST'])
@login_required
def leaves_dashboard():
    """Unified Leaves page with tabs (New Request, My Requests, Pending Requests)"""
    form = LeaveForm()

    # Approver choices depend on user's role
    if current_user.role in ['it_manager', 'general_director']:
        approvers = User.query.filter(User.id != current_user.id).all()
    else:
        approvers = User.query.filter(
            User.department_id == current_user.department_id,
            User.role.in_(['manager', 'head_of_department', 'it_manager', 'general_director'])
        ).all()

    form.approver_id.choices = [(u.id, f"{u.name} ({u.role.replace('_', ' ').title()})") for u in approvers]

    # Handle submission in the same page
    if request.method == "POST" and form.validate_on_submit():
        payload = {
            'type': form.type.data,
            'start_date': form.start_date.data.strftime("%Y-%m-%d"),
            'end_date': form.end_date.data.strftime("%Y-%m-%d"),
            'reason': form.reason.data,
            'approver_id': form.approver_id.data,
        }
        create_leave_request(current_user.id, payload)
        flash("Leave request submitted successfully!", "success")
        return redirect(url_for('leave.leaves_dashboard'))

    # Load data for the other tabs
    my_requests = list_user_requests(current_user.id)
    pending = list_pending_requests(current_user) if current_user.role in ['manager', 'head_of_department', 'it_manager', 'general_director'] else []

    return render_template(
        'dashboard/leaves.html',
        form=form,
        requests=my_requests,
        pending_requests=pending
    )


# --- APPROVE / REJECT REQUEST ---
@leave_bp.route('/<int:lr_id>/<action>', methods=['POST'])
@login_required
@role_required(['manager', 'head_of_department', 'it_manager', 'general_director'])
def set_status(lr_id, action):
    """Approve or reject a leave request assigned to current approver"""
    if action not in ["approve", "reject"]:
        flash("Invalid action", "danger")
        return redirect(url_for('leave.leaves_dashboard'))

    status_map = {"approve": "approved", "reject": "rejected"}
    status = status_map[action]

    lr = set_leave_status(lr_id, current_user.id, status)
    flash(f"Leave request #{lr.id} {status}", "success")
    return redirect(url_for('leave.leaves_dashboard'))
