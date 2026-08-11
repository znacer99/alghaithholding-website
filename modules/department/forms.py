from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Save')

class DeleteForm(FlaskForm):
    pass  # only for CSRF token protection