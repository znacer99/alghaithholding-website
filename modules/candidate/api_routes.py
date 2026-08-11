from flask import Blueprint, jsonify, request, send_file
from core.extensions import db
from core.models import Candidate, Department
from datetime import datetime
from modules.auth.jwt_utils import mobile_auth_required

api_candidate_bp = Blueprint('api_candidate', __name__, url_prefix='/api/candidates')

@api_candidate_bp.route('', methods=['GET'])
@mobile_auth_required
def get_candidates():
    try:
        candidates = Candidate.query.all()
        return jsonify({
            'success': True,
            'candidates': [{
                'id': c.id,
                'full_name': c.full_name,
                'email': c.email,
                'phone': c.phone,
                'nationality': c.nationality,
                'applied_position': c.applied_position,
                'specialty': c.specialty,
                'experience': c.experience,
                'status': c.status,
                'cv_filepath': c.cv_filepath,
                'id_document_filepath': c.id_document_filepath,
                'updated_at': c.updated_at.isoformat() if c.updated_at else None,
                'department': {
                    'id': c.department.id,
                    'name': c.department.name
                } if c.department else None,
                'created_at': c.created_at.isoformat()
            } for c in candidates]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_candidate_bp.route('/<int:id>', methods=['GET'])
@mobile_auth_required
def get_candidate(id):
    try:
        c = Candidate.query.get_or_404(id)
        return jsonify({
            'success': True,
            'candidate': {
                'id': c.id,
                'full_name': c.full_name,
                'email': c.email,
                'phone': c.phone,
                'nationality': c.nationality,
                'applied_position': c.applied_position,
                'specialty': c.specialty,
                'experience': c.experience,
                'education': c.education,
                'skills': c.skills,
                'status': c.status,
                'cv_filepath': c.cv_filepath,
                'id_document_filepath': c.id_document_filepath,
                'department': {
                    'id': c.department.id,
                    'name': c.department.name
                } if c.department else None,
                'created_at': c.created_at.isoformat(),
                'updated_at': c.updated_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_candidate_bp.route('/<int:id>/status', methods=['PUT'])
@mobile_auth_required
def update_status(id):
    try:
        c = Candidate.query.get_or_404(id)
        data = request.json
        c.status = data.get('status', c.status)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_candidate_bp.route('/<int:id>/cv', methods=['GET'])
@mobile_auth_required
def download_cv(id):
    try:
        c = Candidate.query.get_or_404(id)
        if not c.cv_filepath:
            return jsonify({'success': False, 'message': 'No CV found'}), 404
        return send_file(c.cv_filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_candidate_bp.route('/<int:id>/id-document', methods=['GET'])
@mobile_auth_required
def download_id_document(id):
    try:
        c = Candidate.query.get_or_404(id)
        return send_file(c.id_document_filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
