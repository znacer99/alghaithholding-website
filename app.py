# app.py
# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false

import logging
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, current_app, session, send_from_directory
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, logout_user
from config import config
from core.extensions import db, login_manager, migrate, babel
from flask_babel import get_locale as babel_get_locale

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def create_app():
    """Application factory function"""
    app = Flask(__name__)

    # Load configuration
    env = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[env])  # <- dynamically pick DevelopmentConfig or ProductionConfig

    # Language configuration
    app.config['LANGUAGES'] = ['en', 'ar']
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    # File upload size limit (10MB)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 # 10 MB limit
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize Babel with the correct locale selector
    babel.init_app(app, locale_selector=get_locale)
    
    class CustomCSRF(CSRFProtect):
        def protect(self):
            # Allow API & public candidate apply
            if request.path.startswith('/api/') or request.path == '/candidates/apply':
                return
            return super(CustomCSRF, self).protect()

    
    csrf = CustomCSRF()
    csrf.init_app(app)

    # Make sure SECRET_KEY is set
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY') or 'mqM_nXhDHOYlb0T8E9bT4c7XCLiDImpINnVHFmCLR-Q'

    # Inject logout_form and locale information
    @app.context_processor
    def inject_common_variables():
        from modules.auth.forms import LogoutForm
        return dict(
            logout_form=LogoutForm(),
            get_locale=babel_get_locale,
            current_lang=session.get('lang', 'en')
        )

    # Register blueprints
    register_blueprints(app)

    return app


def get_locale():
    """Determine the best locale for the current request"""
    # 1. Check if language is specified in URL parameters
    lang = request.args.get('lang')
    if lang in current_app.config['LANGUAGES']:
        session['lang'] = lang
        return lang
    
    # 2. Check session for stored language preference
    if 'lang' in session and session['lang'] in current_app.config['LANGUAGES']:
        return session['lang']
    
    # 3. Check cookies for language preference (backward compatibility)
    lang_cookie = request.cookies.get('user_lang')
    if lang_cookie in current_app.config['LANGUAGES']:
        session['lang'] = lang_cookie
        return lang_cookie
    
    # 4. Fallback to browser settings
    browser_lang = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    if browser_lang:
        return browser_lang
    
    # 5. Default to English
    return current_app.config['BABEL_DEFAULT_LOCALE']


def register_blueprints(app):
    """Register all application blueprints"""
    from modules.auth.routes import auth_bp
    from modules.dashboard.routes import dashboard_bp
    from modules.leave.routes import leave_bp
    from modules.employee.routes import employee_bp
    from routes.document_routes import docs_bp
    from modules.department.routes import department_bp
    from modules.candidate.routes import candidate_bp
    from modules.user.routes import user_bp
    from routes.landing_routes import landing_bp
    from routes.language_routes import lang_bp
    from routes.profile_routes import profile_bp
    from modules.dashboard.api_routes import api_dashboard_bp
    from modules.employee.api_routes import api_employee_bp
    from modules.department.api_routes import api_department_bp
    from modules.leave.api_routes import api_leave_bp
    from modules.document.api_routes import api_document_bp
    from modules.candidate.api_routes import api_candidate_bp
    from modules.user.api_routes import api_user_bp
    from modules.auth.api_mobile import api_mobile_auth_bp
    from modules.employee.api_uploads import api_employee_upload_bp
    from modules.job_offer.routes import job_offer_bp
    from modules.job_offer.api_routes import api_job_offer_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(leave_bp, url_prefix='/leave')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(docs_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(lang_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(job_offer_bp)
    app.register_blueprint(api_dashboard_bp)
    app.register_blueprint(api_employee_bp)
    app.register_blueprint(api_department_bp)
    app.register_blueprint(api_leave_bp)
    app.register_blueprint(api_document_bp)
    app.register_blueprint(api_candidate_bp)
    app.register_blueprint(api_user_bp)
    app.register_blueprint(api_mobile_auth_bp)
    app.register_blueprint(api_employee_upload_bp)
    app.register_blueprint(api_job_offer_bp)

    print("All registered endpoints:")
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, rule)


def initialize_database():
    """Create departments, employees, and initial users safely (idempotent)"""
    from core.models import User, Department, Employee
    from core.extensions import db

    # 1️⃣ Departments
    departments_data = [
        {"key": "executive", "name": "Executive Leadership", "description": "Company executives"},
        {"key": "it", "name": "IT Department", "description": "Technology team"},
        {"key": "hr", "name": "Human Resources", "description": "HR team"},
        {"key": "operations", "name": "Operations", "description": "Company operations"}
    ]

    departments = {}
    for dept_data in departments_data:
        dept = Department.query.filter_by(name=dept_data["name"]).first()
        if not dept:
            dept = Department(name=dept_data["name"], description=dept_data["description"])
            db.session.add(dept)
            db.session.flush()  # get dept.id without committing
        departments[dept_data["key"]] = dept

    # 2️⃣ Users & Employees (only employees who need a User account)
    users_data = [
        {"email": "it@alghaith.com", "name": "IT Manager", "role": "it_manager", "dept": "it", "access_code": "IT-001", "password": "SecurePassword123!"},
        {"email": "director@alghaith.com", "name": "General Director", "role": "general_director", "dept": "executive", "access_code": "GD-001", "password": "DirectorPass123!"},
        {"email": "manager@alghaith.com", "name": "General Manager", "role": "general_manager", "dept": "operations", "access_code": "GM-001", "password": "ManagerPass123!"},
        {"email": "hr@alghaith.com", "name": "Head of HR", "role": "head_of_department", "dept": "hr", "access_code": "HR-001", "password": "HRPass123!"},
        {"email": "dept@alghaith.com", "name": "Department Manager", "role": "manager", "dept": "operations", "access_code": "DM-001", "password": "DeptPass123!"},
        {"email": "employee@alghaith.com", "name": "Regular Employee", "role": "employee", "dept": "operations", "access_code": "EE-001", "password": "EmployeePass123!"}
    ]

    for user_data in users_data:
        # 2a️⃣ Ensure Employee exists
        employee = Employee.query.filter_by(full_name=user_data["name"]).first()
        if not employee:
            employee = Employee(
                full_name=user_data["name"],
                job_title=user_data["role"],
                department=departments[user_data["dept"]],
                phone=""
            )
            db.session.add(employee)
            db.session.flush()  # get employee.id

        # 2b️⃣ Ensure User exists
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                role=user_data["role"],
                access_code=user_data["access_code"],
                avatar=user_data["name"][0] + user_data["name"].split()[-1][0],
                is_active=True
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            db.session.flush()  # get user.id

        # 2c️⃣ Link Employee -> User
        if not employee.user_id:
            employee.user_id = user.id

    db.session.commit()
    print("✅ Database initialized successfully (idempotent)!")


# Create the app instance
app = create_app()

with app.app_context():
    try:
        db.create_all()
        initialize_database()
    except Exception as e:
        print(f"Database initialization error (non-critical): {e}")

# User loader
@login_manager.user_loader
def load_user(user_id):
    from core.models import User
    return db.session.get(User, int(user_id))


# Error handlers
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.before_request
def make_session_permanent():
    session.permanent = True

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('auth.login'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
