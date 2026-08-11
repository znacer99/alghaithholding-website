from flask import Blueprint, request, jsonify
from core.models import User
from core.extensions import db
import jwt
from datetime import datetime, timedelta
from config import Config

api_mobile_auth_bp = Blueprint('api_mobile_auth', __name__, url_prefix='/api/mobile/auth')

@api_mobile_auth_bp.route('/login', methods=['POST'])
def mobile_login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    token = jwt.encode(
        {
            "id": user.id,
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        Config.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        }
    }), 200
