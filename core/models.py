from datetime import datetime
from core.extensions import db
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from flask_login import UserMixin
from flask import current_app

ph = PasswordHasher()

# -------------------- USER --------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # General Director, IT Manager, etc.
    avatar = db.Column(db.String(255), nullable=True)
    access_code = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    documents = db.relationship('UserDocument', back_populates='user', cascade="all, delete-orphan")
    folders_created = db.relationship('Folder', back_populates='creator', cascade="all, delete-orphan")
    activities = db.relationship('ActivityLog', back_populates='user', cascade="all, delete-orphan")
    leave_requests = db.relationship('LeaveRequest', back_populates='requester', foreign_keys='LeaveRequest.user_id')
    approved_requests = db.relationship('LeaveRequest', back_populates='approver', foreign_keys='LeaveRequest.approver_id')


    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except (VerifyMismatchError, InvalidHash):
            return False
        except Exception as e:
            current_app.logger.error(f"Password verification error: {str(e)}")
            return False

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False



# -------------------- EMPLOYEE --------------------
class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    # New fields
    actual_address = db.Column(db.String(255), nullable=True)
    mother_country_address = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    id_number = db.Column(db.String(50), unique=True, nullable=True)  # Identity card / Passport number
    nationality = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optional link to a user account
    documents = db.relationship('EmployeeDocument', back_populates='employee', cascade='all, delete-orphan')


    # Relationships
    department = db.relationship("Department", back_populates="employees")
    user = db.relationship("User")  # Optional one-to-one or one-to-many link

    def __repr__(self):
        return f"<Employee {self.full_name} - {self.job_title}>"


# -------------------- DEPARTMENT --------------------
class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employees = db.relationship("Employee", back_populates="department", lazy="selectin")
    candidates = db.relationship("Candidate", back_populates="department", lazy="selectin")
    job_offers = db.relationship("JobOffer", back_populates="department", lazy="selectin")

    def __repr__(self):
        return f"<Department {self.name}>"


# -------------------- FOLDER --------------------
class Folder(db.Model):
    __tablename__ = 'folders'
    __table_args__ = (db.UniqueConstraint('name', 'created_by', name='uix_user_folder'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('UserDocument', back_populates='folder', cascade="all, delete-orphan")
    creator = db.relationship('User', back_populates='folders_created')

    def __repr__(self):
        return f"<Folder {self.name}>"


# -------------------- USER DOCUMENT --------------------
class UserDocument(db.Model):
    __tablename__ = 'user_documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # points to User
    owner_id = db.Column(db.Integer, nullable=False)  # id of owner (User or Employee)
    owner_type = db.Column(db.String(50), nullable=False, default='user')  # 'user' or 'employee'
    visibility_type = db.Column(db.String(50), default='private')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New field for document type
    document_type = db.Column(db.String(50), nullable=False, server_default='additional')  # passport, contract, medical, additional

    # Access control fields
    allowed_users = db.Column(db.String, nullable=True)        # comma-separated user IDs
    allowed_roles = db.Column(db.String, nullable=True)        # comma-separated role names
    allowed_departments = db.Column(db.String, nullable=True)  # comma-separated department IDs

    # Relationships
    folder = db.relationship('Folder', back_populates='documents')
    user = db.relationship('User', back_populates='documents', foreign_keys=[user_id])

    def __repr__(self):
        return f"<UserDocument id={self.id} filename={self.filename} owner={self.owner_type}:{self.owner_id} folder_id={self.folder_id} type={self.document_type}>"

    # ------------------------
    # Access control
    # ------------------------
    def can_owner_access(self, owner):
        if self.visibility_type == 'shared':
            return True
        return self.owner_id == getattr(owner, "id", None) and self.owner_type == owner.__class__.__name__.lower()

    def can_owner_delete(self, owner):
        privileged_roles = ['general_director', 'it_manager']
        if self.owner_type == 'user' and hasattr(owner, 'role'):
            return self.owner_id == owner.id or owner.role.lower() in privileged_roles
        return self.owner_id == getattr(owner, "id", None)

    @staticmethod
    def visible_documents_for(owner):
        all_docs = UserDocument.query.all()
        return [doc for doc in all_docs if doc.can_owner_access(owner)]



# -------------------- ACTIVITY LOG --------------------
class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    target = db.Column(db.String(100))
    details = db.Column(db.Text, nullable=True)  # added to prevent keyword errors
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='activities')

# -------------------- LEAVE REQUEST --------------------
class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(30), nullable=False, default='annual')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')
    decided_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[user_id], back_populates='leave_requests')
    approver = db.relationship('User', foreign_keys=[approver_id], back_populates='approved_requests')


# -------------------- CANDIDATE --------------------
class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    
    # UPDATED: Changed from specific positions to categories
    applied_position = db.Column(db.String(120), nullable=True)  # Engineer, Technician, Helper, Unskilled Worker
    
    # NEW: Added specialty field
    specialty = db.Column(db.String(255), nullable=True)  # Specific field of work/specialization
    
    experience = db.Column(db.String(50), nullable=True)  # 0-2, 3-5, 6-10, 10+
    education = db.Column(db.String(50), nullable=True)   # High School, Bachelor's, Master's, PhD
    skills = db.Column(db.Text, nullable=True)           # Skills and qualifications
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    job_offer_id = db.Column(db.Integer, db.ForeignKey('job_offers.id'), nullable=True)
    cv_filepath = db.Column(db.String(255), nullable=True)
    
    # UPDATED: Changed from nullable to required (nullable=False)
    id_document_filepath = db.Column(db.String(255), nullable=False)
    
    status = db.Column(db.String(50), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department = db.relationship("Department", back_populates="candidates", lazy=True)
    job_offer = db.relationship("JobOffer", back_populates="candidates", lazy=True)

    def __repr__(self):
        return f"<Candidate {self.full_name} - {self.applied_position} ({self.status})>"


# -------------------- EmployeeDocument ----------------

class EmployeeDocument(db.Model):
    __tablename__ = 'employee_documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False, default='additional')  # passport, contract, medical, etc.
    visibility_type = db.Column(db.String(50), default='private')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship
    employee = db.relationship('Employee', back_populates='documents')

    def __repr__(self):
        return f"<EmployeeDocument id={self.id} filename={self.filename} employee_id={self.employee_id}>"


# -------------------- JOB OFFER --------------------
class JobOffer(db.Model):
    __tablename__ = 'job_offers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    title_ar = db.Column(db.String(150), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    location = db.Column(db.String(100), default='Tripoli, Libya')
    location_ar = db.Column(db.String(100), default='طرابلس، ليبيا')
    employment_type = db.Column(db.String(50), default='Full-time')  # Full-time, Part-time, Contract
    category = db.Column(db.String(100), nullable=True)  # Engineer, Technician, Helper, Unskilled Worker
    specialty = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    description_ar = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    requirements_ar = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, closed, draft
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    department = db.relationship("Department", back_populates="job_offers", lazy=True)
    candidates = db.relationship("Candidate", back_populates="job_offer", lazy=True)
    creator = db.relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<JobOffer {self.title} ({self.status})>"