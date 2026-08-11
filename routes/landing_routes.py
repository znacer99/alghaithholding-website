from flask import Blueprint, render_template, request
from config_data.specialties import SPECIALTIES, SPECIALTIES_BY_CATEGORY
from config_data.nationalities import NATIONALITIES

from core.models import JobOffer

# Define blueprint
landing_bp = Blueprint('landing', __name__)

# Route for the landing page
@landing_bp.route('/')
def landing():
    submitted = request.args.get('submitted') # capture the query parameter
    try:
        job_offers = JobOffer.query.filter_by(status='active').order_by(JobOffer.created_at.desc()).all()
    except Exception:
        job_offers = []
    return render_template(
        'landing.html',
        specialties=SPECIALTIES,
        specialties_by_category=SPECIALTIES_BY_CATEGORY,
        nationalities=NATIONALITIES,
        submitted=submitted,
        job_offers=job_offers
    )
