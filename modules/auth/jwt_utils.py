import jwt
from flask import request, jsonify
from functools import wraps
from config import Config

def mobile_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "message": "Auth token missing"}), 401
        
        token = auth_header.replace("Bearer ", "")

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload["id"]
        except Exception:
            return jsonify({"success": False, "message": "Invalid or expired token"}), 401

        return f(*args, **kwargs)
    return wrapper


