from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from forms import LoginForm, ApplicationForm, SignupForm
import hashlib

app = Flask(__name__)   
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobfinding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_employer = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('companies', lazy=True))

    def __repr__(self):
        return f'<Company {self.name}>'

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    bio = db.Column(db.Text, nullable=True)
    resume = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Profile {self.user.username}>'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    company = db.relationship('Company', backref=db.backref('jobs', lazy=True))
    location = db.Column(db.String(100), nullable=False)
    company_logo = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Job {self.title}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    portfolio = db.Column(db.String(200), nullable=True)
    resume = db.Column(db.String(200), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Application {self.name} for Job ID {self.job_id}>'

from flask_login import current_user

def check_if_application_exists(job_id, user_identifier):
    application_exists = Application.query.filter(
        (Application.job_id == job_id) & 
        ((Application.user_id == user_identifier) | (Application.email == user_identifier))
    ).first() is not None
    print(f'Checking if application exists for job_id={job_id} and user_identifier={user_identifier}: {application_exists}')
    return application_exists

@app.route('/applications')
def applications1():
    if current_user.is_authenticated:
        applications = Application.query.filter_by(user_id=current_user.id).all()
        return render_template('applications.html', applications=applications)
    else:
        return render_template('login.html')

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    form = ApplicationForm()
    application_success = False
    application_already_submitted = False

    user_id = current_user.id if current_user.is_authenticated else None

    # Check if the application already exists
    user_identifier = user_id if user_id else form.email.data if form.email.data else None
    application_already_submitted = check_if_application_exists(job_id, user_identifier)

    if application_already_submitted:
        flash('You have already applied for this job.', 'warning')
        return render_template('job-detail.html', job=job, job_id=job_id, form=form, application_success=application_success, application_already_submitted=application_already_submitted)

    if form.validate_on_submit():
        print('Form validated')

        # Ensure email is collected when user is not authenticated
        if user_id is None and not form.email.data:
            flash('Email is required to apply for this job.', 'warning')
            return render_template('job-detail.html', job=job, job_id=job_id, form=form, application_success=application_success, application_already_submitted=application_already_submitted)

        print('Creating new application')
        application = Application(
            name=form.name.data,
            email=form.email.data,
            portfolio=form.portfolio.data,
            resume=form.file.data.filename,
            cover_letter=form.coverletter.data,
            user_id=user_id,
            job_id=job.id,
            date_applied=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted!', 'success')
        application_success = True

    return render_template('job-detail.html', job=job, job_id=job_id, form=form, application_success=application_success, application_already_submitted=application_already_submitted)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

from flask_login import login_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if form.is_employer.data == user.is_employer:
                login_user(user)
                return redirect(url_for('job_list'))
            else:
                flash('Employer/Employee status mismatch', 'danger')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/applications')
def applications():
    return render_template('applications.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome to the dashboard, {current_user.email}!"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/category')
def category():
    return render_template('category.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/job-detail/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    form=ApplicationForm()
    return render_template('job-detail.html', job=job, job_id=job_id, form=form)

@app.route('/job-list')
def job_list():
    jobs = Job.query.order_by(Job.date_posted.desc()).all()
    return render_template('job-list.html', jobs=jobs)

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_employer=form.is_employer.data)
        db.session.add(user)
        db.session.commit()
        if form.is_employer.data:
            company = Company(name=form.company_name.data, description=form.company_description.data, user=user)
            db.session.add(company)
            db.session.commit()
            login_user(user)
            flash('Your account has been created!', 'success')
            return redirect(url_for('employer'))
        else:
            login_user(user)
            flash('Your account has been created!', 'success')
            return redirect(url_for('job_list'))
    return render_template('signup.html', form=form)

@app.route('/')
def home():
    categories = [
        {"icon": "fa-mail-bulk", "title": "Marketing"},
        {"icon": "fa-headset", "title": "Customer Service"},
        {"icon": "fa-user-tie", "title": "Health"},
        {"icon": "fa-tasks", "title": "Project Management"},
        {"icon": "fa-chart-line", "title": "Business Development"},
        {"icon": "fa-hands-helping", "title": "Sales & Communication"},
        {"icon": "fa-book-reader", "title": "Teaching & Education"},
        {"icon": "fa-drafting-compass", "title": "Design & Creative"},
    ]

    for category in categories:
        category_jobs_count = Job.query.filter_by(category=category["title"]).count()
        category["vacancies"] = category_jobs_count

    jobs = Job.query.all()
    return render_template('index.html', categories=categories, jobs=jobs)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
