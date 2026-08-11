from flask import Blueprint

leave_bp = Blueprint('leave', __name__, template_folder='templates')

from . import routes  # noqa: E402,F401  (ensure routes register on import)