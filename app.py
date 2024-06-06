from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobfinding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

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
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('applications', lazy=True))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    job = db.relationship('Job', backref=db.backref('applications', lazy=True))
    cover_letter = db.Column(db.Text, nullable=True)    

    def __repr__(self):
        return f'<Application {self.user.username} for {self.job.title}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', 'success')
            print('Success')
            return f"Hello World {user.password}"
        else:
            flash('Invalid email or password', 'danger')
            print('Failed')
    else:
        print('Form validation failed:', form.errors)

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

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
    return render_template('job-detail.html', job=job)

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
