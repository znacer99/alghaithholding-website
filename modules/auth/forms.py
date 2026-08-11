# modules/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class LogoutForm(FlaskForm):
    """Simple form used solely for CSRF-protected logout"""
    submit = SubmitField('Logout')
