from __future__ import annotations
import os
import secrets
from datetime import datetime
from flask import current_app, request
from werkzeug.utils import secure_filename

from core.extensions import db
from core.models import User, UserDocument

# ------------------------
# Helpers
# ------------------------
def _generate_avatar(name: str) -> str:
    """Generate initials avatar from a name."""
    if not name:
        return "??"
    parts = name.strip().split()
    if len(parts) == 1:
        return (parts[0][0] + (parts[0][1] if len(parts[0]) > 1 else '')).upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _generate_access_code():
    """Generate short random access code for system user."""
    return secrets.token_hex(3).upper()


def _ensure_folder_dir(user_id: int, folder_name: str | None) -> str:
    """Ensure upload folder exists for a user (with optional subfolder)."""
    base_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    if folder_name:
        base_folder = os.path.join(base_folder, secure_filename(folder_name))
    os.makedirs(base_folder, exist_ok=True)
    return base_folder


def _save_documents(
    user: User,
    files,
    folder_name: str | None = None,
    visibility_type: str = "private",
    allowed_users: str | None = None,
    allowed_roles: str | None = None,
    allowed_departments: str | None = None,
):
    """Save uploaded files for a user and create UserDocument entries."""
    if not files:
        return
    if not isinstance(files, (list, tuple)):
        files = [files]

    base_folder = _ensure_folder_dir(user.id, folder_name)

    for f in files:
        if not f or not getattr(f, "filename", None):
            continue
        filename = secure_filename(f.filename)
        filepath = os.path.join(base_folder, filename)
        f.save(filepath)

        rel_path = os.path.relpath(filepath, current_app.config['UPLOAD_FOLDER'])

        doc = UserDocument(
            user_id=user.id,
            filename=filename,
            filepath=rel_path,
            folder_id=None,
            visibility_type=(visibility_type or "private").lower(),
            allowed_users=(allowed_users or None),
            allowed_roles=(allowed_roles or None),
            allowed_departments=(allowed_departments or None),
            uploaded_at=datetime.utcnow(),
        )
        db.session.add(doc)
    db.session.commit()


# ------------------------
# Folder operations
# ------------------------
def create_folder_for_user(user, folder_name: str):
    """Create a virtual folder for a user (filesystem only)."""
    folder_name = (folder_name or "").strip()
    if not folder_name:
        raise ValueError("Folder name is required.")
    _ensure_folder_dir(user.id, folder_name)
    return folder_name


def update_document_visibility(doc_id: int, form_data, acting_user):
    """Update visibility settings for a user document."""
    doc = UserDocument.query.get_or_404(doc_id)
    if doc.user_id != acting_user.id and acting_user.role.lower() not in ["general_director", "it_manager"]:
        raise PermissionError("Not allowed to change visibility for this document.")

    vtype = (form_data.get("visibility_type") or "private").lower()
    doc.visibility_type = vtype
    doc.allowed_users = form_data.get("allowed_users") or None
    doc.allowed_roles = form_data.get("allowed_roles") or None

    db.session.add(doc)
    db.session.commit()
    return doc


# ------------------------
# User CRUD
# ------------------------
def create_user(form_data):
    """Create a system user (with login, role, avatar, documents)."""
    email = form_data.get("email")
    name = form_data.get("name") or "Unnamed"
    role = (form_data.get("role") or "employee").lower()
    password = form_data.get("password") or secrets.token_urlsafe(10)
    access_code = form_data.get("access_code") or _generate_access_code()
    avatar = form_data.get("avatar") or _generate_avatar(name)
    is_active = form_data.get("is_active", True)
    phone = form_data.get("phone")
    position = form_data.get("position")

    user = User(
        email=email,
        name=name,
        role=role,
        access_code=access_code,
        avatar=avatar,
        is_active=is_active,
        phone=phone,
        position=position,
    )
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()

        # Handle document uploads
        files = request.files.getlist("documents") or []
        single = request.files.get("document")
        if single and getattr(single, "filename", ""):
            files.append(single)

        folder_name = request.form.get("folder_name")
        visibility_type = (request.form.get("visibility_type") or "private").lower()
        allowed_users = request.form.get("allowed_users")
        allowed_roles = request.form.get("allowed_roles")

        _save_documents(
            user,
            files,
            folder_name=folder_name,
            visibility_type=visibility_type,
            allowed_users=allowed_users,
            allowed_roles=allowed_roles,
        )
    except Exception as e:
        db.session.rollback()
        raise e

    return user


def update_user(user_id, form_data):
    """Update a system user including documents, phone, and position."""
    user = User.query.get_or_404(user_id)

    # Update basic fields
    for field in ["email", "name", "access_code", "avatar", "phone", "position"]:
        if field in form_data and form_data[field] is not None:
            setattr(user, field, form_data[field])

    # Update role
    if "role" in form_data and form_data["role"]:
        user.role = form_data["role"].lower()

    # Update password if provided
    if "password" in form_data and form_data["password"]:
        user.set_password(form_data["password"])

    # Update active status
    if "is_active" in form_data:
        user.is_active = bool(form_data["is_active"])

    # Handle document uploads
    files = request.files.getlist("documents") or []
    single_file = request.files.get("document")
    if single_file and getattr(single_file, "filename", ""):
        files.append(single_file)

    folder_name = request.form.get("folder_name")
    visibility_type = (request.form.get("visibility_type") or "private").lower()
    allowed_users = request.form.get("allowed_users")
    allowed_roles = request.form.get("allowed_roles")

    _save_documents(
        user,
        files,
        folder_name=folder_name,
        visibility_type=visibility_type,
        allowed_users=allowed_users,
        allowed_roles=allowed_roles,
    )

    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return user


def delete_user(user_id):
    """Delete a system user and all associated documents."""
    user = User.query.get_or_404(user_id)

    docs = UserDocument.query.filter_by(user_id=user.id).all()
    for doc in docs:
        try:
            abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filepath)
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception:
            pass
        db.session.delete(doc)

    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return user
