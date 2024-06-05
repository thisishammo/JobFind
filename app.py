from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobfinding.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model to store information about both employers and employees
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_employer = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Company model to store information about companies
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('companies', lazy=True))

    def __repr__(self):
        return f'<Company {self.name}>'

# Profile model to store employee profiles and resumes
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    bio = db.Column(db.Text, nullable=True)
    resume = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Profile {self.user.username}>'

# Job model to store job postings
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

# Application model to store job applications
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


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/category')
def category():
    return render_template('category.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        
        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/job-detail/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job-detail.html', job=job)

@app.route('/job-list')
def job_list():
    jobs = Job.query.order_by(Job.date_posted.desc()).all()
    print(jobs)
    return render_template('job-list.html', jobs=jobs)

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def home():
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()        
    app.run(debug=True)