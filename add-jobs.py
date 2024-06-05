from app import app, db, User, Company, Job
from datetime import datetime

with app.app_context():
    user = User.query.first()
    company = Company.query.first()

    if not user or not company:
        print("Add a user and a company first.")
    else:
        job1 = Job(
            title="Software Developer",
            description="Develop software applications.",
            date_posted=datetime.utcnow(),
            company_id=company.id,
            company=company,
            location="New York",
            company_logo="img/com-logo-1.jpg",
            salary=50000,
            category="Technology"
        )
        job2 = Job(
            title="Data Scientist",
            description="Analyze data and build models.",
            date_posted=datetime.utcnow(),
            company_id=company.id,
            company=company,
            location="San Francisco",
            company_logo="img/com-logo-2.jpg",
            salary=70000,
            category="Data Science"
        )

        db.session.add(job1)
        db.session.add(job2)
        db.session.commit()
        print("Jobs added!")
