from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from core.extensions import db
from core.models import ActivityLog
from core.forms import ProfileForm, ChangePasswordForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def my_profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'profile_submit' in request.form and profile_form.validate_on_submit():
            try:
                # Update user profile
                current_user.name = profile_form.name.data
                current_user.email = profile_form.email.data
                current_user.phone = profile_form.phone.data
                current_user.position = profile_form.position.data

                # Log the activity
                activity = ActivityLog(
                    user_id=current_user.id,
                    action='UPDATE',
                    target='PROFILE',
                    details=f"User updated their profile information"
                )
                db.session.add(activity)
                db.session.commit()

                flash('Your profile has been updated successfully!', 'success')
                return redirect(url_for('profile.my_profile'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating profile: {str(e)}")
                flash('An error occurred while updating your profile. Please try again.', 'error')

        elif 'password_submit' in request.form and password_form.validate_on_submit():
            try:
                # Verify current password
                if not current_user.check_password(password_form.current_password.data):
                    flash('Current password is incorrect.', 'error')
                    return render_template('profile/my_profile.html', 
                                         profile_form=profile_form, 
                                         password_form=password_form)

                # Update password
                current_user.set_password(password_form.new_password.data)

                # Log the activity
                activity = ActivityLog(
                    user_id=current_user.id,
                    action='UPDATE',
                    target='PASSWORD',
                    details=f"User changed their password"
                )
                db.session.add(activity)
                db.session.commit()

                flash('Your password has been changed successfully!', 'success')
                return redirect(url_for('profile.my_profile'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error changing password: {str(e)}")
                flash('An error occurred while changing your password. Please try again.', 'error')

    return render_template('profile/my_profile.html', 
                         profile_form=profile_form, 
                         password_form=password_form)

@profile_bp.route('/activity')
@login_required
def activity_log():
    # Get user's recent activities
    activities = ActivityLog.query.filter_by(user_id=current_user.id)\
                                .order_by(ActivityLog.timestamp.desc())\
                                .limit(50)\
                                .all()
    
    return render_template('profile/activity_log.html', activities=activities)

@profile_bp.route('/test')
def test():
    return render_template('profile/my_profile.html')