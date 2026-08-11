import os
from flask import current_app
from werkzeug.utils import secure_filename
from core.extensions import db
from core.models import Candidate

# -------------------- Helper -------------------- #
def save_file(file_obj, subfolder="candidates"):
    """Save uploaded file to static/subfolder or /tmp on Vercel"""
    if not file_obj or not getattr(file_obj, 'filename', None):
        return None

    is_vercel = os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ
    if is_vercel:
        folder = os.path.join('/tmp', subfolder)
    else:
        folder = os.path.join(current_app.root_path, "static", subfolder)

    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        pass

    filename = secure_filename(file_obj.filename)
    path = os.path.join(folder, filename)
    file_obj.save(path)

    if is_vercel:
        return path  # Full path in /tmp
    return f"{subfolder}/{filename}"


# -------------------- CRUD -------------------- #
def save_candidate(form_data, cv_file=None, id_file=None):
    candidate = Candidate(
        full_name=form_data.get("full_name"),
        email=form_data.get("email"),
        phone=form_data.get("phone"),
        nationality=form_data.get("nationality"),
        applied_position=form_data.get("applied_position"),
        specialty=form_data.get("specialty"),
        experience=form_data.get("experience"),
        education=form_data.get("education"),
        skills=form_data.get("skills"),
        department_id=form_data.get("department_id"),
        job_offer_id=form_data.get("job_offer_id"),
        status=form_data.get("status") or "new",
    )

    candidate.cv_filepath = save_file(cv_file)
    candidate.id_document_filepath = save_file(id_file)

    # Validate required fields for public applications
    if not candidate.id_document_filepath:
        raise ValueError("ID document is required")

    # On Vercel, save to SQLite in /tmp
    try:
        db.session.add(candidate)
        db.session.commit()
    except Exception as db_err:
        current_app.logger.warning("Local DB commit warning: %s", db_err)
        db.session.rollback()

    # Real-time Auto-Sync to Supabase Database and Storage
    try:
        is_vercel = os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ
        if is_vercel:
            cv_local = candidate.cv_filepath
            id_local = candidate.id_document_filepath
        else:
            cv_local = os.path.join(current_app.root_path, "static", candidate.cv_filepath) if candidate.cv_filepath else None
            id_local = os.path.join(current_app.root_path, "static", candidate.id_document_filepath) if candidate.id_document_filepath else None
        
        from core.supabase_sync import sync_candidate_to_supabase
        sync_candidate_to_supabase(candidate, cv_local, id_local)
    except Exception as sync_err:
        current_app.logger.error("Supabase auto-sync failed for new candidate: %s", sync_err)

    return candidate


def update_candidate(candidate_id, form_data, cv_file=None, id_file=None):
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.full_name = form_data.get("full_name", candidate.full_name)
    candidate.email = form_data.get("email", candidate.email)
    candidate.phone = form_data.get("phone", candidate.phone)
    candidate.nationality = form_data.get("nationality", candidate.nationality)
    candidate.applied_position = form_data.get("applied_position", candidate.applied_position)
    candidate.specialty = form_data.get("specialty", candidate.specialty)  # NEW FIELD
    candidate.experience = form_data.get("experience", candidate.experience)
    candidate.education = form_data.get("education", candidate.education)
    candidate.skills = form_data.get("skills", candidate.skills)
    candidate.department_id = form_data.get("department_id", candidate.department_id)
    candidate.status = form_data.get("status", candidate.status)

    # Update files if new ones are uploaded
    if cv_file:
        candidate.cv_filepath = save_file(cv_file)
    if id_file:
        candidate.id_document_filepath = save_file(id_file)

    db.session.commit()

    # Real-time Auto-Sync to Supabase Database and Storage
    try:
        cv_local = os.path.join(current_app.root_path, "static", candidate.cv_filepath) if candidate.cv_filepath else None
        id_local = os.path.join(current_app.root_path, "static", candidate.id_document_filepath) if candidate.id_document_filepath else None
        
        from core.supabase_sync import sync_candidate_to_supabase
        sync_candidate_to_supabase(candidate, cv_local, id_local)
    except Exception as sync_err:
        current_app.logger.error("Supabase auto-sync failed for updated candidate: %s", sync_err)

    return candidate


def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)

    # Delete files from static folder
    for file_attr in ["cv_filepath", "id_document_filepath"]:
        filepath = getattr(candidate, file_attr)
        if filepath:
            abs_path = os.path.join(current_app.root_path, "static", filepath)
            if os.path.exists(abs_path):
                os.remove(abs_path)

    db.session.delete(candidate)
    db.session.commit()
    return True


# -------------------- Service Object -------------------- #
class CandidateService:
    save_candidate = staticmethod(save_candidate)
    update_candidate = staticmethod(update_candidate)
    delete_candidate = staticmethod(delete_candidate)


candidate_services = CandidateService()