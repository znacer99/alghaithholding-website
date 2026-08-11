# modules/auth/routes.py
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from core.extensions import db
from core.models import User
from datetime import datetime
from modules.auth.forms import LoginForm, LogoutForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
    print(f"🔍 LOGIN ROUTE: User authenticated? {current_user.is_authenticated}")
    
    # Redirect if already logged in
    if current_user.is_authenticated:
        print(f"🔍 Already logged in: {current_user.email}, Role: {current_user.role}")
        # Redirect IT Managers to IT Manager dashboard
        if current_user.role == "it_manager":
            print("🔍 Redirecting to IT Manager dashboard")
            return redirect(url_for('dashboard.it_manager_dashboard'))
        # Redirect all others to role-based dashboard
        print("🔍 Redirecting to role dashboard")
        return redirect(url_for('dashboard.role_dashboard'))

    form = LoginForm()
    print(f"🔍 Form submitted: {form.validate_on_submit()}")
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(f"🔍 Attempting login: {email}")

        # Find user by email
        user = User.query.filter_by(email=email).first()
        print(f"🔍 User found: {user is not None}")

        if user:
            print(f"🔍 User details: {user.email}, Role: {user.role}, Active: {user.is_active}")
            print(f"🔍 Password check: {user.check_password(password)}")
        
        # Validate credentials
        if user and user.check_password(password):
            print(f"🔍 Login successful, calling login_user()")
            login_user(user)
            
            # Update login stats
            user.login_count += 1
            user.last_login = datetime.utcnow()
            db.session.commit()

            # debug print
            print(f"🔍 Logged in as: {user.email} with role: {user.role}")
            
            # Redirect to appropriate dashboard
            if user.role == "it_manager":
                print("🔍 Redirecting IT Manager to IT Manager dashboard")
                return redirect(url_for('dashboard.it_manager_dashboard'))
            print("🔍 Redirecting to role dashboard")
            return redirect(url_for('dashboard.role_dashboard'))
        else:
            print("🔍 Login failed - invalid credentials")
            flash('Invalid email or password', 'error')
    
    print("🔍 Rendering login template")
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    # using LogoutForm ensures the CSRF token is validated
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        flash('You have been logged out', 'success')
        return redirect(url_for('auth.login'))

    # If CSRF validation fails or form not submitted properly
    flash('Invalid logout request', 'danger')
    return redirect(url_for('dashboard.role_dashboard'))


# Removed admin-login route because 'admin' no longer exists.
# If you want to keep a special IT Manager login route, rename it and update:

@auth_bp.route('/it-login', methods=['GET', 'POST'])
def it_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.role == 'it_manager':  # Only allow IT managers
            login_user(user)
            return redirect(url_for('dashboard.it_manager_dashboard'))
        flash('IT Manager access denied', 'error')
    return render_template('auth/login.html', form=form)
