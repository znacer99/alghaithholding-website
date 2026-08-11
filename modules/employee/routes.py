import os
from flask import Blueprint, request, redirect, url_for, flash, current_app, send_file, render_template
from flask_login import login_required, current_user
from core.decorators import permission_required
from core.permissions import Permission
from .services import (
    create_employee,
    update_employee,
    delete_employee,
    _save_employee_documents,
    create_folder_for_employee,
)
from core.models import UserDocument
from core.extensions import db

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------
# Employee CRUD Routes
# ------------------------
@employee_bp.route('/create', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def create():
    try:
        files = request.files.getlist('documents') or []
        single = request.files.get('document')
        if single and getattr(single, "filename", ""):
            files.append(single)

        employee = create_employee(request.form, files)
        flash(f'✅ Employee {employee.full_name} created successfully.', 'success')
        return redirect(url_for('dashboard.employee_management'))
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating employee: {str(e)}', 'danger')
        return redirect(url_for('dashboard.employee_form'))

@employee_bp.route('/<int:employee_id>/update', methods=['POST'])
@login_required
@permission_required(Permission.EDIT)
def update(employee_id):
    try:
        # Only pass form data to update_employee
        employee = update_employee(employee_id, request.form)

        flash(f'✅ Employee {employee.full_name} updated successfully.', 'success')
        return redirect(url_for('dashboard.employee_profile', id=employee.id))
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error updating employee: {str(e)}', 'danger')
        return redirect(url_for('dashboard.edit_employee', id=employee_id))


@employee_bp.route('/<int:employee_id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.ADMIN)
def delete(employee_id):
    try:
        employee = delete_employee(employee_id)
        flash(f'🗑️ Employee {employee.full_name} deleted successfully.', 'success')
        return redirect(url_for('dashboard.employee_management'))
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting employee: {str(e)}', 'danger')
        return redirect(url_for('dashboard.employee_profile', id=employee_id))

# ------------------------
# Document Routes
# ------------------------
@employee_bp.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = (request.form.get('folder_name') or '').strip()
    if not folder_name:
        flash('❌ Folder name cannot be empty', 'danger')
        return redirect(url_for('dashboard.role_dashboard'))

    try:
        create_folder_for_employee(current_user, folder_name)
        db.session.commit()
        flash(f'📁 Folder "{folder_name}" created.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Could not create folder: {str(e)}', 'danger')

    return redirect(url_for('dashboard.role_dashboard'))

@employee_bp.route('/upload-document', methods=['POST'])
@login_required
def upload_document():
    files = request.files.getlist('documents') or []
    single = request.files.get('document')
    if single and getattr(single, "filename", ""):
        files.append(single)

    valid_files = [f for f in files if f and allowed_file(getattr(f, "filename", ""))]
    if not valid_files:
        flash('❌ No valid files uploaded', 'error')
        return redirect(url_for('dashboard.role_dashboard'))

    folder_name = request.form.get("folder_name") or None
    visibility_type = (request.form.get("visibility_type") or "private").lower()
    allowed_users = request.form.get("allowed_users")
    allowed_roles = request.form.get("allowed_roles")
    allowed_departments = request.form.get("allowed_departments")

    if current_user.role == 'employee':
        visibility_type = 'roles'
        allowed_roles = 'it_manager,general_director'

    _save_employee_documents(
        current_user,
        valid_files,
        folder_name=folder_name,
        visibility_type=visibility_type,
        allowed_users=allowed_users,
        allowed_roles=allowed_roles,
        allowed_departments=allowed_departments,
    )

    try:
        db.session.commit()
        flash('✅ Document uploaded successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error saving document: {str(e)}', 'danger')

    if current_user.role == 'employee':
        return redirect(url_for('dashboard.employee_dashboard'))
    return redirect(url_for('dashboard.role_dashboard'))

@employee_bp.route('/document/<int:doc_id>')
@login_required
def download_document(doc_id):
    doc = UserDocument.query.get_or_404(doc_id)
    if not doc.can_user_access(current_user):
        flash("❌ You are not allowed to access this document.", "danger")
        return redirect(url_for('dashboard.employee_dashboard') if current_user.role == 'employee' else 'dashboard.role_dashboard')

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filepath)
    if not os.path.exists(full_path):
        flash("❌ File not found.", "danger")
        return redirect(url_for('dashboard.employee_dashboard') if current_user.role == 'employee' else 'dashboard.role_dashboard')

    return send_file(full_path, as_attachment=True)

@employee_bp.route('/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = UserDocument.query.get_or_404(doc_id)
    if not doc.can_user_access(current_user) or current_user.id != doc.owner_id:
        flash("❌ You cannot delete this document.", "danger")
        return redirect(url_for('dashboard.employee_dashboard') if current_user.role == 'employee' else 'dashboard.role_dashboard')

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filepath)
    if os.path.exists(full_path):
        os.remove(full_path)

    db.session.delete(doc)
    try:
        db.session.commit()
        flash(f'🗑️ Document "{doc.filename}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting document: {str(e)}', 'danger')

    return redirect(url_for('dashboard.employee_dashboard') if current_user.role == 'employee' else 'dashboard.role_dashboard')

# ------------------------
# Employee List Page
# ------------------------
@employee_bp.route('/list')
@login_required
@permission_required(Permission.VIEW)
def list_employees():
    from core.models import Employee  # ensure Employee model is imported
    employees = Employee.query.all()
    employee_data = []

    for emp in employees:
        employee_data.append({
            'id': emp.id,
            'full_name': emp.full_name,
            'job_title': emp.job_title,
            'phone': emp.phone,
            'department': emp.department.name if emp.department else '-'
        })

    return render_template('dashboard/employees/list.html', employees=employee_data)
