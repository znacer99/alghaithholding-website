from datetime import datetime
from core.extensions import db
from core.models import JobOffer

def get_all_job_offers():
    return JobOffer.query.order_by(JobOffer.created_at.desc()).all()

def get_active_job_offers():
    return JobOffer.query.filter_by(status='active').order_by(JobOffer.created_at.desc()).all()

def get_job_offer_by_id(job_id):
    return JobOffer.query.get_or_404(job_id)

def create_job_offer(form_data, user_id=None):
    job_offer = JobOffer(
        title=form_data.get('title'),
        title_ar=form_data.get('title_ar'),
        department_id=form_data.get('department_id') if form_data.get('department_id') else None,
        location=form_data.get('location') or 'Tripoli, Libya',
        location_ar=form_data.get('location_ar') or 'طرابلس، ليبيا',
        employment_type=form_data.get('employment_type') or 'Full-time',
        category=form_data.get('category'),
        specialty=form_data.get('specialty'),
        description=form_data.get('description'),
        description_ar=form_data.get('description_ar'),
        requirements=form_data.get('requirements'),
        requirements_ar=form_data.get('requirements_ar'),
        status=form_data.get('status') or 'active',
        created_by=user_id
    )
    db.session.add(job_offer)
    db.session.commit()
    return job_offer

def update_job_offer(job_id, form_data):
    job_offer = JobOffer.query.get_or_404(job_id)
    job_offer.title = form_data.get('title', job_offer.title)
    job_offer.title_ar = form_data.get('title_ar', job_offer.title_ar)
    job_offer.department_id = form_data.get('department_id') if form_data.get('department_id') else job_offer.department_id
    job_offer.location = form_data.get('location', job_offer.location)
    job_offer.location_ar = form_data.get('location_ar', job_offer.location_ar)
    job_offer.employment_type = form_data.get('employment_type', job_offer.employment_type)
    job_offer.category = form_data.get('category', job_offer.category)
    job_offer.specialty = form_data.get('specialty', job_offer.specialty)
    job_offer.description = form_data.get('description', job_offer.description)
    job_offer.description_ar = form_data.get('description_ar', job_offer.description_ar)
    job_offer.requirements = form_data.get('requirements', job_offer.requirements)
    job_offer.requirements_ar = form_data.get('requirements_ar', job_offer.requirements_ar)
    job_offer.status = form_data.get('status', job_offer.status)
    job_offer.updated_at = datetime.utcnow()
    
    db.session.commit()
    return job_offer

def toggle_job_offer_status(job_id):
    job_offer = JobOffer.query.get_or_404(job_id)
    if job_offer.status == 'active':
        job_offer.status = 'closed'
    else:
        job_offer.status = 'active'
    job_offer.updated_at = datetime.utcnow()
    db.session.commit()
    return job_offer

def delete_job_offer(job_id):
    job_offer = JobOffer.query.get_or_404(job_id)
    db.session.delete(job_offer)
    db.session.commit()
    return True

class JobOfferService:
    get_all_job_offers = staticmethod(get_all_job_offers)
    get_active_job_offers = staticmethod(get_active_job_offers)
    get_job_offer_by_id = staticmethod(get_job_offer_by_id)
    create_job_offer = staticmethod(create_job_offer)
    update_job_offer = staticmethod(update_job_offer)
    toggle_job_offer_status = staticmethod(toggle_job_offer_status)
    delete_job_offer = staticmethod(delete_job_offer)

job_offer_services = JobOfferService()
