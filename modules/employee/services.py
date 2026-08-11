from __future__ import annotations
import os
import secrets
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

from core.extensions import db
from core.models import Employee, EmployeeDocument

# ------------------------
# Helpers
# ------------------------
def _generate_avatar(name: str) -> str:
    if not name:
        return "??"
    parts = name.strip().split()
    if len(parts) == 1:
        return (parts[0][0] + (parts[0][1] if len(parts[0]) > 1 else '')).upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _generate_access_code():
    return secrets.token_hex(3).upper()


def _ensure_folder_dir(employee_id: int, folder_name: str | None) -> str:
    """
    Ensures the upload folder exists for an employee (with optional subfolder) and returns its path.
    """
    base_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], "employees", str(employee_id))
    if folder_name:
        base_folder = os.path.join(base_folder, secure_filename(folder_name))
    os.makedirs(base_folder, exist_ok=True)
    return base_folder


# ------------------------
# Folder Operations
# ------------------------
def create_folder_for_employee(employee, folder_name: str):
    folder_name = (folder_name or "").strip()
    if not folder_name:
        raise ValueError("Folder name is required.")
    return _ensure_folder_dir(employee.id, folder_name)


# ------------------------
# Employee Document Handling
# ------------------------
def _save_employee_documents(employee, files, folder_name: str | None = None,
                             visibility_type: str = "private", document_type: str = "additional"):
    """
    Save one or multiple documents for an employee under the correct type.
    """
    if not files:
        return

    if not isinstance(files, (list, tuple)):
        files = [files]

    employee_id = getattr(employee, "id", None)
    if employee_id is None:
        raise ValueError("Employee object must have an 'id' attribute.")

    base_folder = _ensure_folder_dir(employee_id, folder_name)

    for f in files:
        if not f or not getattr(f, "filename", None):
            continue

        filename = secure_filename(f.filename)
        filepath = os.path.join(base_folder, filename)
        f.save(filepath)

        rel_path = os.path.relpath(filepath, current_app.config['UPLOAD_FOLDER'])

        doc = EmployeeDocument(
            employee_id=employee_id,
            filename=filename,
            filepath=rel_path,
            visibility_type=visibility_type,
            document_type=document_type  # passport / contract / medical / additional
        )
        db.session.add(doc)


# ------------------------
# Employee CRUD
# ------------------------
def create_employee(form_data, files=None):
    """
    Creates an employee and saves their documents.
    """
    # ---- Basic fields ----
    name = form_data.get("name") or "Unnamed"
    position = form_data.get("position") or None
    phone = form_data.get("phone") or None
    department_id = form_data.get("department") or form_data.get("department_id")
    actual_address = form_data.get("actual_address") or None
    mother_country_address = form_data.get("mother_country_address") or None
    nationality = form_data.get("nationality") or None
    country = form_data.get("country") or None
    state = form_data.get("state") or None
    id_number = form_data.get("id_number") or None

    # ---- Birth date handling ----
    birth_date = form_data.get("birth_date")
    if birth_date and birth_date.strip():
        try:
            birth_date = datetime.strptime(birth_date.strip(), "%Y-%m-%d").date()
        except Exception:
            birth_date = None
    else:
        birth_date = None

    # ---- Department ID ----
    if department_id:
        try:
            department_id = int(department_id)
        except:
            department_id = None

    # ---- Create employee ----
    employee = Employee(
        full_name=name,
        job_title=position,
        phone=phone,
        department_id=department_id,
        actual_address=actual_address,
        mother_country_address=mother_country_address,
        nationality=nationality,
        country=country,
        state=state,
        birth_date=birth_date,
        id_number=id_number
    )
    db.session.add(employee)
    db.session.commit()  # Commit first to get ID

    # ---- Handle documents ----
    folder_name = form_data.get("folder_name")
    visibility_type = (form_data.get("visibility_type") or "private").lower()

    if files:
        name_to_type = {
            "passport": "passport",
            "contract": "contract",
            "medical": "medical",
            "documents": "additional"
        }

        for f in files:
            doc_type = name_to_type.get(f.name, "additional")
            _save_employee_documents(
                employee,
                files=[f],
                folder_name=folder_name,
                visibility_type=visibility_type,
                document_type=doc_type
            )

    db.session.commit()
    return employee


def update_employee(employee_id, form_data, files=None):
    employee = Employee.query.get_or_404(employee_id)

    for field in [
        "full_name", "job_title", "phone", "actual_address", "mother_country_address",
        "nationality", "country", "state", "birth_date", "id_number"
    ]:
        if form_data.get(field) is not None:
            value = form_data.get(field)
            if field == "birth_date":
                if value and value.strip():
                    try:
                        value = datetime.strptime(value.strip(), "%Y-%m-%d").date()
                    except:
                        value = None
                else:
                    value = None
            setattr(employee, field, value)

    # Department
    if form_data.get("department"):
        try:
            employee.department_id = int(form_data.get("department"))
        except Exception:
            pass

    # Handle new documents
    if files:
        folder_name = form_data.get("folder_name")
        visibility_type = (form_data.get("visibility_type") or "private").lower()
        name_to_type = {
            "passport": "passport",
            "contract": "contract",
            "medical": "medical",
            "documents": "additional"
        }

        for f in files:
            doc_type = name_to_type.get(f.name, "additional")
            _save_employee_documents(
                employee,
                files=[f],
                folder_name=folder_name,
                visibility_type=visibility_type,
                document_type=doc_type
            )

    db.session.add(employee)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return employee


def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    # Delete all employee documents
    docs = EmployeeDocument.query.filter_by(employee_id=employee.id).all()
    for doc in docs:
        try:
            abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filepath)
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception:
            pass
        db.session.delete(doc)

    db.session.delete(employee)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return employee
