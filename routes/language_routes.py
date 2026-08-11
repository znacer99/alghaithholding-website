from flask import Blueprint, request, redirect, session
from flask_babel import refresh

lang_bp = Blueprint('lang', __name__)

@lang_bp.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('lang', 'en')
    
    # Validate the language
    if lang not in ['en', 'ar']:
        lang = 'en'
    
    # Store in session (primary storage)
    session['lang'] = lang
    session.permanent = True
    
    # Also set cookie for compatibility
    response = redirect(request.referrer or '/')
    response.set_cookie('user_lang', lang, max_age=30*24*60*60)  # 30 days
    
    # Refresh Babel locale for current request
    refresh()
    
    return response