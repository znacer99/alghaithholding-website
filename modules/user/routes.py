from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from core.models import User, db
from core.decorators import role_required
from modules.user.services import create_user as create_user_service, update_user as update_user_service, delete_user as delete_user_service
from flask_wtf.csrf import CSRFProtect

user_bp = Blueprint('user', __name__, template_folder='templates')

# -------------------------------
# List Users
# -------------------------------
@user_bp.route('/users')
@login_required
@role_required(['it_manager', 'general_director'])
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('dashboard/users.html', users=users)

# -------------------------------
# Create User
# -------------------------------
@user_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required(['it_manager', 'general_director'])
def user_create():
    if request.method == 'POST':
        form = request.form.to_dict()
        form['csrf_token'] = request.form.get('csrf_token')  # include CSRF token
        try:
            create_user_service(form)
            flash("User created successfully!", "success")
            return redirect(url_for('user.list_users'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            flash(f"Error creating user: {str(e)}", "danger")
    return render_template('dashboard/user_form.html', user=None)

# -------------------------------
# Edit User
# -------------------------------
@user_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['it_manager', 'general_director'])
def user_edit(user_id):
    user = User.query.get_or_404(user_id)    
    if request.method == 'POST':
        form = request.form.to_dict()
        form['csrf_token'] = request.form.get('csrf_token')  # include CSRF token

        # --- DEBUG LOGGING ---
        current_app.logger.info(f"Received form data for user update (id={user_id}): {form}")
        required_fields = ['name', 'email', 'role']
        missing_fields = [f for f in required_fields if not form.get(f)]
        if missing_fields:
            flash(f"Missing required fields: {', '.join(missing_fields)}", "danger")
            current_app.logger.warning(f"Missing fields in user update (id={user_id}): {missing_fields}")
            return render_template('dashboard/user_form.html', user=user)

        try:
            update_user_service(user_id, form)
            flash("User updated successfully!", "success")
            return redirect(url_for('user.list_users'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user (id={user_id}): {str(e)}")
            flash(f"Error updating user: {str(e)}", "danger")
            return render_template('dashboard/user_form.html', user=user), 500

    return render_template('dashboard/user_form.html', user=user)

# -------------------------------
# Delete User
# -------------------------------
@user_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required(['it_manager', 'general_director'])
def user_delete(user_id):
    try:
        delete_user_service(user_id)
        flash("User deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user (id={user_id}): {str(e)}")
        flash(f"Error deleting user: {str(e)}", "danger")
    return redirect(url_for('user.list_users'))
