# modules/department/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.extensions import db
from core.models import Department, Employee, Candidate
from flask_login import login_required
from modules.department.forms import DepartmentForm, DeleteForm

department_bp = Blueprint('department', __name__, url_prefix='/department')


# -------------------- LIST DEPARTMENTS --------------------
@department_bp.route('/')
@login_required
def list_departments():
    departments = Department.query.order_by(Department.name).all()
    summary = []

    for dept in departments:
        employees = Employee.query.filter_by(department_id=dept.id).all()
        # Only include employee fields, no user data
        serialized_employees = [
            {
                'id': emp.id,
                'full_name': emp.full_name,
                'job_title': emp.job_title,
                'phone': emp.phone,
                'actual_address': emp.actual_address,
                'mother_country_address': emp.mother_country_address,
                'nationality': emp.nationality,
                'id_number': emp.id_number
            } for emp in employees
        ]
        summary.append({
            'department': {
                'id': dept.id,
                'name': dept.name,
                'description': dept.description
            },
            'employee_count': len(employees),
            'employees': serialized_employees
        })

    delete_form = DeleteForm()
    return render_template('dashboard/departments/list.html', summary=summary, delete_form=delete_form)


# -------------------- CREATE DEPARTMENT --------------------
@department_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        description = form.description.data.strip() if form.description.data else None

        if Department.query.filter_by(name=name).first():
            flash('Department with this name already exists', 'danger')
            return redirect(url_for('department.create_department'))

        dept = Department(name=name, description=description)
        db.session.add(dept)
        db.session.commit()
        flash('Department created successfully', 'success')
        return redirect(url_for('department.list_departments'))

    return render_template('dashboard/departments/form.html', form=form, department=None)


# -------------------- EDIT DEPARTMENT --------------------
@department_bp.route('/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    form = DepartmentForm(obj=dept)

    if form.validate_on_submit():
        dept.name = form.name.data.strip()
        dept.description = form.description.data.strip() if form.description.data else None
        db.session.commit()
        flash('Department updated successfully', 'success')
        return redirect(url_for('department.list_departments'))

    return render_template('dashboard/departments/form.html', form=form, department=dept)


# -------------------- DELETE DEPARTMENT --------------------
@department_bp.route('/<int:dept_id>/delete', methods=['POST'])
@login_required
def delete_department(dept_id):
    form = DeleteForm()
    if form.validate_on_submit():
        dept = Department.query.get_or_404(dept_id)
        db.session.delete(dept)
        db.session.commit()
        flash('Department deleted successfully', 'success')
    else:
        flash('Invalid CSRF token.', 'danger')
    return redirect(url_for('department.list_departments'))


# -------------------- VIEW DEPARTMENT TEAM --------------------
from flask import render_template
from flask_login import login_required
from modules.department.forms import DeleteForm
from core.models import Department, Employee, Candidate, EmployeeDocument
from sqlalchemy.orm import joinedload

@department_bp.route('/<int:dept_id>/view')
@login_required
def view_department(dept_id):
    # Get department
    dept = Department.query.get_or_404(dept_id)

    # Get all employees in this department, eager load documents
    employees = Employee.query.options(joinedload(Employee.documents)) \
        .filter_by(department_id=dept.id).all()

    # Prepare a mapping of employee_id -> documents
    employee_docs = {e.id: e.documents for e in employees}

    # Get candidates
    candidates = Candidate.query.filter_by(department_id=dept.id).all()

    # Delete form for CSRF protection
    delete_form = DeleteForm()

    # Render template
    return render_template(
        'dashboard/departments/team.html',
        department={
            'id': dept.id,
            'name': dept.name,
            'description': dept.description
        },
        employees=employees,
        candidates=candidates,
        employee_docs=employee_docs,
        delete_form=delete_form
    )




# -------------------- DEPARTMENT SUMMARY --------------------
@department_bp.route('/summary')
@login_required
def department_summary():
    departments = Department.query.order_by(Department.name).all()
    summary = []

    for dept in departments:
        employees = Employee.query.filter_by(department_id=dept.id).all()
        serialized_employees = [
            {
                'id': emp.id,
                'full_name': emp.full_name,
                'job_title': emp.job_title,
                'phone': emp.phone,
                'actual_address': emp.actual_address,
                'mother_country_address': emp.mother_country_address,
                'country': emp.country,
                'state': emp.state,
                'birth_date': emp.birth_date.strftime('%Y-%m-%d') if emp.birth_date else None,
                'nationality': emp.nationality,
                'id_number': emp.id_number
            } for emp in employees
        ]

        summary.append({
            'department': {
                'id': dept.id,
                'name': dept.name,
                'description': dept.description
            },
            'employee_count': len(employees),
            'employees': serialized_employees
        })

    delete_form = DeleteForm()
    return render_template('dashboard/departments/list.html', summary=summary, delete_form=delete_form)
