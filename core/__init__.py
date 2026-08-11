# core/__init__.py
from .extensions import db, login_manager, migrate
from . import models  # Important to load models