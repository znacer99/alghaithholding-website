from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from core.models import db, Folder, UserDocument
import os
from werkzeug.utils import secure_filename
from datetime import datetime

docs_bp = Blueprint('docs', __name__, url_prefix='/documents')


@docs_bp.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = request.form.get('folder_name', '').strip()
    if not folder_name:
        flash("Folder name cannot be empty.", "danger")
        return redirect(url_for('docs.list_documents'))

    existing = Folder.query.filter_by(name=folder_name, created_by=current_user.id).first()
    if existing:
        flash(f"You already have a folder named '{folder_name}'.", "warning")
        return redirect(url_for('docs.list_documents'))

    folder = Folder(name=folder_name, created_by=current_user.id)
    db.session.add(folder)
    db.session.commit()
    flash("Folder created successfully!", "success")
    return redirect(url_for('docs.list_documents'))


@docs_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    files = request.files.getlist('documents')
    folder_id = request.form.get('folder_id') or None
    visibility = request.form.get('visibility_type', 'private').lower()

    if visibility == 'shared' and current_user.role.lower() == 'employee':
        flash("❌ You are not allowed to upload shared documents.", "danger")
        return redirect(url_for('docs.list_documents'))

    if not files or all(f.filename == "" for f in files):
        flash("❌ No files selected.", "danger")
        return redirect(url_for('docs.list_documents'))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    uploaded_count = 0
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)

            relative_path = os.path.relpath(filepath, start=current_app.root_path)
            doc = UserDocument(
                filename=file.filename,
                filepath=relative_path,
                folder_id=folder_id,
                user_id=current_user.id,
                owner_id=current_user.id,
                owner_type='user',
                visibility_type=visibility
            )
            db.session.add(doc)
            uploaded_count += 1

    try:
        db.session.commit()
        flash(f"✅ {uploaded_count} document(s) uploaded successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error saving documents: {str(e)}", "danger")

    return redirect(url_for('docs.list_documents'))


@docs_bp.route('/')
@login_required
def list_documents():
    my_folders = Folder.query.filter_by(created_by=current_user.id).order_by(Folder.created_at.desc()).all()
    my_docs = UserDocument.query.filter_by(user_id=current_user.id, folder_id=None, visibility_type='private').all()
    shared_docs = UserDocument.query.filter(UserDocument.visibility_type=='shared', UserDocument.folder_id==None).all()

    return render_template(
        'dashboard/documents.html',
        folders=my_folders,
        documents=my_docs,
        shared_documents=shared_docs
    )


@docs_bp.route('/delete_document/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = UserDocument.query.get_or_404(doc_id)
    if not doc.can_owner_delete(current_user):
        flash("You cannot delete this document.", "danger")
        return redirect(url_for('docs.list_documents'))

    try:
        file_path = os.path.join(current_app.root_path, 'static', doc.filepath)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        flash(f"Error deleting file: {str(e)}", "danger")

    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted successfully!", "success")
    return redirect(url_for('docs.list_documents'))


@docs_bp.route('/delete_folder/<int:folder_id>', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.filter_by(id=folder_id, created_by=current_user.id).first()
    if not folder:
        flash("Folder not found or you don't have permission to delete it.", "danger")
        return redirect(url_for('docs.list_documents'))

    for doc in folder.documents:
        try:
            file_path = os.path.join(current_app.root_path, 'static', doc.filepath)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            flash(f"Failed to delete file {doc.filename}: {str(e)}", "warning")
        db.session.delete(doc)

    db.session.delete(folder)
    db.session.commit()
    flash(f"Folder '{folder.name}' and its documents have been deleted.", "success")
    return redirect(url_for('docs.list_documents'))


@docs_bp.route('/download/<int:doc_id>', methods=['GET'])
@login_required
def download_document(doc_id):
    doc = UserDocument.query.get_or_404(doc_id)
    if not doc.can_owner_access(current_user):
        flash("You cannot download this document.", "danger")
        return redirect(url_for('docs.list_documents'))

    file_path = os.path.join(current_app.root_path, doc.filepath)
    if not os.path.exists(file_path):
        flash("File not found on server.", "danger")
        return redirect(url_for('docs.list_documents'))

    return send_file(file_path, as_attachment=True, download_name=doc.filename)
