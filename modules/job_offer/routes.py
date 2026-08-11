from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from core.models import Department, JobOffer
from modules.job_offer.services import job_offer_services
from config_data.specialties import SPECIALTIES, SPECIALTIES_BY_CATEGORY

job_offer_bp = Blueprint("job_offers", __name__, url_prefix="/dashboard/jobs")


@job_offer_bp.route("/")
@login_required
def list_job_offers():
    status_filter = request.args.get('status')
    if status_filter:
        job_offers = JobOffer.query.filter_by(status=status_filter).order_by(JobOffer.created_at.desc()).all()
    else:
        job_offers = job_offer_services.get_all_job_offers()
    return render_template("dashboard/job_offers/list.html", job_offers=job_offers, current_filter=status_filter)


@job_offer_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_job_offer():
    departments = Department.query.all()
    if request.method == "POST":
        try:
            job_offer_services.create_job_offer(request.form, user_id=current_user.id)
            flash("Job offer created successfully.", "success")
            return redirect(url_for("job_offers.list_job_offers"))
        except Exception as e:
            flash(f"Error creating job offer: {str(e)}", "danger")
            
    return render_template(
        "dashboard/job_offers/form.html",
        job_offer=None,
        departments=departments,
        specialties=SPECIALTIES,
        specialties_by_category=SPECIALTIES_BY_CATEGORY
    )


@job_offer_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_job_offer(id):
    job_offer = job_offer_services.get_job_offer_by_id(id)
    departments = Department.query.all()
    if request.method == "POST":
        try:
            job_offer_services.update_job_offer(id, request.form)
            flash("Job offer updated successfully.", "success")
            return redirect(url_for("job_offers.list_job_offers"))
        except Exception as e:
            flash(f"Error updating job offer: {str(e)}", "danger")

    return render_template(
        "dashboard/job_offers/form.html",
        job_offer=job_offer,
        departments=departments,
        specialties=SPECIALTIES,
        specialties_by_category=SPECIALTIES_BY_CATEGORY
    )


@job_offer_bp.route("/toggle/<int:id>", methods=["POST"])
@login_required
def toggle_job_offer(id):
    try:
        job = job_offer_services.toggle_job_offer_status(id)
        flash(f"Job offer '{job.title}' status changed to '{job.status}'.", "info")
    except Exception as e:
        flash(f"Error changing status: {str(e)}", "danger")
    return redirect(url_for("job_offers.list_job_offers"))


@job_offer_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_job_offer(id):
    try:
        job_offer_services.delete_job_offer(id)
        flash("Job offer deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting job offer: {str(e)}", "danger")
    return redirect(url_for("job_offers.list_job_offers"))


@job_offer_bp.route("/<int:id>")
@login_required
def view_job_offer(id):
    job_offer = job_offer_services.get_job_offer_by_id(id)
    return render_template("dashboard/job_offers/view.html", job_offer=job_offer)
