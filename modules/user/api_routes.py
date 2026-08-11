from flask import Blueprint, jsonify, request
from core.extensions import db
from core.models import User
from datetime import datetime
from modules.auth.jwt_utils import mobile_auth_required

api_user_bp = Blueprint('api_user', __name__, url_prefix='/api/users')

# Helper to get user from JWT
def get_current_user_obj():
    user_id = getattr(request, "user_id", None)
    if not user_id:
        return None
    return User.query.get(user_id)


# ------------------------------------------------------------
# GET ALL ACTIVE USERS
# ------------------------------------------------------------
@api_user_bp.route('', methods=['GET'])
@mobile_auth_required
def get_users():
    try:
        users = User.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'users': [{
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'phone': u.phone,
                'position': u.position,
                'created_at': u.created_at.isoformat(),
                'last_login': u.last_login.isoformat() if u.last_login else None
            } for u in users]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ------------------------------------------------------------
# GET A SPECIFIC USER
# ------------------------------------------------------------
@api_user_bp.route('/<int:id>', methods=['GET'])
@mobile_auth_required
def get_user(id):
    try:
        u = User.query.get_or_404(id)
        return jsonify({
            'success': True,
            'user': {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'phone': u.phone,
                'position': u.position,
                'access_code': u.access_code,
                'is_active': u.is_active,
                'login_count': u.login_count,
                'created_at': u.created_at.isoformat(),
                'last_login': u.last_login.isoformat() if u.last_login else None
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ------------------------------------------------------------
# GET LOGGED-IN USER (PROFILE)
# ------------------------------------------------------------
@api_user_bp.route('/me', methods=['GET'])
@mobile_auth_required
def get_current_user():
    try:
        u = get_current_user_obj()

        return jsonify({
            'success': True,
            'user': {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'phone': u.phone,
                'position': u.position
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
