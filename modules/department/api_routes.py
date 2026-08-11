from flask import Blueprint, jsonify, request
from core.extensions import db
from core.models import Department
from modules.auth.jwt_utils import mobile_auth_required

api_department_bp = Blueprint('api_department', __name__, url_prefix='/api/departments')

@api_department_bp.route('', methods=['GET'])
@mobile_auth_required
def get_departments():
    try:
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'employee_count': len(dept.employees)
            } for dept in departments]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_department_bp.route('/<int:id>', methods=['GET'])
@mobile_auth_required
def get_department(id):
    try:
        dept = Department.query.get_or_404(id)
        return jsonify({
            'success': True,
            'department': {
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'created_at': dept.created_at.isoformat(),
                'employees': [{
                    'id': emp.id,
                    'full_name': emp.full_name,
                    'job_title': emp.job_title
                } for emp in dept.employees]
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_department_bp.route('', methods=['POST'])
@mobile_auth_required
def create_department():
    try:
        data = request.json
        dept = Department(
            name=data.get('name'),
            description=data.get('description')
        )
        db.session.add(dept)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Department created',
            'department_id': dept.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_department_bp.route('/<int:id>', methods=['PUT'])
@mobile_auth_required
def update_department(id):
    try:
        dept = Department.query.get_or_404(id)
        data = request.json
        dept.name = data.get('name', dept.name)
        dept.description = data.get('description', dept.description)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Department updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_department_bp.route('/<int:id>', methods=['DELETE'])
@mobile_auth_required
def delete_department(id):
    try:
        dept = Department.query.get_or_404(id)
        db.session.delete(dept)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Department deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
