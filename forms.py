from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField, FileField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length
import re

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class ApplicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Your Name", "class": "form-control"})
    email = StringField('Email', validators=[DataRequired()], render_kw={"placeholder": "Your Email", "class": "form-control"})
    portfolio = StringField('Portfolio', render_kw={"placeholder": "Portfolio URL", "class": "form-control"})
    file = FileField('Resume', validators=[DataRequired()], render_kw={"class": "form-control"})
    coverletter = TextAreaField('Cover Letter', validators=[DataRequired()], render_kw={"placeholder": "Cover Letter", "class": "form-control", "rows": 5})
    user_id = HiddenField('User ID')
    job_id = HiddenField('Job ID')
    submit = SubmitField('Apply', render_kw={"class": "btn btn-primary w-100"})

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_employer = BooleanField('Register as Employer')
    submit = SubmitField('Sign Up')
