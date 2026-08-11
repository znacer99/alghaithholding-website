from flask import Blueprint, jsonify
from core.models import Employee, Department, LeaveRequest
from modules.auth.jwt_utils import mobile_auth_required

api_dashboard_bp = Blueprint('api_dashboard', __name__, url_prefix='/api/dashboard')

@api_dashboard_bp.route('/stats', methods=['GET'])
@mobile_auth_required
def get_stats():
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()
    
    return jsonify({
        'success': True,
        'stats': {
            'employees': total_employees,
            'departments': total_departments,
            'pending_leaves': pending_leaves
        }
    }), 200
