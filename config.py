import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Ensure instance folder exists
INSTANCE_DIR = os.path.join(basedir, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)

UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, 'uploads', 'documents')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_DIR, 'app.db')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mqM_nXhDHOYlb0T8E9bT4c7XCLiDImpINnVHFmCLR'
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "uW1!kP8#zL9@Sh3^Tb7&Qx2%Mn4Rs5*"

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx'}

    # i18n / I10n settings
    LANGUAGES = ['en', 'ar']
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = False   # keep False until you add HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"  # allows cross-device cookie use
    SESSION_COOKIE_DOMAIN = None     # OR set to your VPS domain/IP
    PERMANENT_SESSION_LIFETIME = 315569520


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
