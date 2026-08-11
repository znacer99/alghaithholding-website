from flask import Blueprint, jsonify, request
from core.models import JobOffer
from modules.job_offer.services import job_offer_services

api_job_offer_bp = Blueprint("api_job_offers", __name__, url_prefix="/api/job-offers")


@api_job_offer_bp.route("/", methods=["GET"])
def get_job_offers():
    status = request.args.get('status', 'active')
    if status == 'all':
        jobs = job_offer_services.get_all_job_offers()
    else:
        jobs = JobOffer.query.filter_by(status=status).order_by(JobOffer.created_at.desc()).all()
        
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "title_ar": job.title_ar,
            "department": job.department.name if job.department else None,
            "department_id": job.department_id,
            "location": job.location,
            "location_ar": job.location_ar,
            "employment_type": job.employment_type,
            "category": job.category,
            "specialty": job.specialty,
            "description": job.description,
            "description_ar": job.description_ar,
            "requirements": job.requirements,
            "requirements_ar": job.requirements_ar,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "applicant_count": len(job.candidates)
        })
    return jsonify({"success": True, "job_offers": result})


@api_job_offer_bp.route("/<int:id>", methods=["GET"])
def get_job_offer_detail(id):
    job = job_offer_services.get_job_offer_by_id(id)
    return jsonify({
        "success": True,
        "job_offer": {
            "id": job.id,
            "title": job.title,
            "title_ar": job.title_ar,
            "department": job.department.name if job.department else None,
            "location": job.location,
            "location_ar": job.location_ar,
            "employment_type": job.employment_type,
            "category": job.category,
            "specialty": job.specialty,
            "description": job.description,
            "description_ar": job.description_ar,
            "requirements": job.requirements,
            "requirements_ar": job.requirements_ar,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "applicant_count": len(job.candidates)
        }
    })
