from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from core.extensions import db
from core.models import Employee, UserDocument
from modules.auth.jwt_utils import mobile_auth_required
from datetime import datetime
import os

api_employee_upload_bp = Blueprint(
    "api_employee_upload",
    __name__,
    url_prefix="/api/employees"
)

UPLOAD_FOLDER = "instance/uploads/documents/employees"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}


def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@api_employee_upload_bp.route("/<int:emp_id>/upload", methods=["POST"])
@mobile_auth_required
def upload_documents(emp_id):
    emp = Employee.query.get_or_404(emp_id)

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No files part"}), 400

    f = request.files["file"]

    if not f or f.filename == "":
        return jsonify({"success": False, "message": "Empty filename"}), 400

    if not allowed(f.filename):
        return jsonify({"success": False, "message": "File type not allowed"}), 400

    emp_folder = os.path.join(UPLOAD_FOLDER, str(emp_id))
    os.makedirs(emp_folder, exist_ok=True)

    filename = secure_filename(f.filename)
    save_path = os.path.join(emp_folder, filename)
    f.save(save_path)

    doc = UserDocument(
        filename=filename,
        filepath=save_path,
        folder_id=None,
        user_id=emp.user_id,
        owner_id=emp.id,
        owner_type="employee",
        visibility_type="private",
        uploaded_at=datetime.utcnow(),
        document_type="employee_upload",
        allowed_users=None,
        allowed_roles=None,
        allowed_departments=None,
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify({"success": True, "message": "File uploaded successfully", "document_id": doc.id}), 200
