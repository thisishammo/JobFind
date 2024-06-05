from app import app, db, User, Company, Job

with app.app_context():
    # Assuming there is at least one user and one company
    user = User.query.first()
    company = Company.query.first()

    if not user or not company:
        print("Add a user and a company first.")
    else:
        job1 = Job(title="Software Developer", description="Develop software applications.", company_id=company.id, location="New York")
        job2 = Job(title="Data Scientist", description="Analyze data and build models.", company_id=company.id, location="San Francisco")

        db.session.add(job1)
        db.session.add(job2)
        db.session.commit()
        print("Jobs added!")
