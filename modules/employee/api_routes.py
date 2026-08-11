from flask import Blueprint, jsonify, request
from core.extensions import db
from core.models import Employee, Department, User
from datetime import datetime
from modules.auth.jwt_utils import mobile_auth_required

api_employee_bp = Blueprint('api_employee', __name__, url_prefix='/api/employees')

# Helper to get user from JWT token
def get_current_user():
    user_id = getattr(request, "user_id", None)
    if not user_id:
        return None
    return User.query.get(user_id)


# --------------------------------------------------------
# GET ALL EMPLOYEES
# --------------------------------------------------------
@api_employee_bp.route('', methods=['GET'])
@mobile_auth_required
def get_employees():
    try:
        employees = Employee.query.all()
        return jsonify({
            'success': True,
            'employees': [{
                'id': emp.id,
                'full_name': emp.full_name,
                'job_title': emp.job_title,
                'phone': emp.phone,
                'department': {
                    'id': emp.department.id,
                    'name': emp.department.name
                } if emp.department else None,
                'country': emp.country,
                'nationality': emp.nationality
            } for emp in employees]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# --------------------------------------------------------
# GET SINGLE EMPLOYEE
# --------------------------------------------------------
@api_employee_bp.route('/<int:id>', methods=['GET'])
@mobile_auth_required
def get_employee(id):
    try:
        emp = Employee.query.get_or_404(id)
        return jsonify({
            'success': True,
            'employee': {
                'id': emp.id,
                'full_name': emp.full_name,
                'job_title': emp.job_title,
                'phone': emp.phone,
                'actual_address': emp.actual_address,
                'mother_country_address': emp.mother_country_address,
                'country': emp.country,
                'state': emp.state,
                'birth_date': emp.birth_date.isoformat() if emp.birth_date else None,
                'id_number': emp.id_number,
                'nationality': emp.nationality,
                'department': {
                    'id': emp.department.id,
                    'name': emp.department.name
                } if emp.department else None,
                'created_at': emp.created_at.isoformat() if emp.created_at else None
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# --------------------------------------------------------
# CREATE EMPLOYEE
# --------------------------------------------------------
@api_employee_bp.route('', methods=['POST'])
@mobile_auth_required
def create_employee():
    try:
        data = request.json
        
        emp = Employee(
            full_name=data.get('full_name'),
            job_title=data.get('job_title'),
            phone=data.get('phone'),
            actual_address=data.get('actual_address'),
            mother_country_address=data.get('mother_country_address'),
            country=data.get('country'),
            state=data.get('state'),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                if data.get('birth_date') else None,
            id_number=data.get('id_number'),
            nationality=data.get('nationality'),
            department_id=data.get('department_id')
        )
        
        db.session.add(emp)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Employee created successfully',
            'employee_id': emp.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# --------------------------------------------------------
# UPDATE EMPLOYEE
# --------------------------------------------------------
@api_employee_bp.route('/<int:id>', methods=['PUT'])
@mobile_auth_required
def update_employee(id):
    try:
        emp = Employee.query.get_or_404(id)
        data = request.json
        
        emp.full_name = data.get('full_name', emp.full_name)
        emp.job_title = data.get('job_title', emp.job_title)
        emp.phone = data.get('phone', emp.phone)
        emp.actual_address = data.get('actual_address', emp.actual_address)
        emp.mother_country_address = data.get('mother_country_address', emp.mother_country_address)
        emp.country = data.get('country', emp.country)
        emp.state = data.get('state', emp.state)
        emp.id_number = data.get('id_number', emp.id_number)
        emp.nationality = data.get('nationality', emp.nationality)
        emp.department_id = data.get('department_id', emp.department_id)
        
        if data.get('birth_date'):
            emp.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Employee updated successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# --------------------------------------------------------
# DELETE EMPLOYEE
# --------------------------------------------------------
@api_employee_bp.route('/<int:id>', methods=['DELETE'])
@mobile_auth_required
def delete_employee(id):
    try:
        emp = Employee.query.get_or_404(id)
        db.session.delete(emp)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Employee deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
