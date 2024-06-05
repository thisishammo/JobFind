from app import app, db, User, Company, Job
from datetime import datetime

predefined_categories = [
    {"title": "Marketing", "icon": "fa-mail-bulk"},
    {"title": "Customer Service", "icon": "fa-headset"},
    {"title": "Health", "icon": "fa-user-tie"},
    {"title": "Project Management", "icon": "fa-tasks"},
    {"title": "Business Development", "icon": "fa-chart-line"},
    {"title": "Sales & Communication", "icon": "fa-hands-helping"},
    {"title": "Teaching & Education", "icon": "fa-book-reader"},
    {"title": "Design & Creative", "icon": "fa-drafting-compass"},
]

with app.app_context():
    user = User.query.first()
    company = Company.query.first()

    if not user or not company:
        print("Add a user and a company first.")
    else:

        marketing_category = next((cat for cat in predefined_categories if cat['title'] == "Marketing"), None)
        customer_service_category = next((cat for cat in predefined_categories if cat['title'] == "Customer Service"), None)

        new_jobs = [
            Job(
                title="Marketing Specialist",
                description="Plan and execute marketing campaigns.",
                date_posted=datetime.utcnow(),
                company_id=company.id,
                company=company,
                location="Los Angeles",
                company_logo="img/com-logo-3.jpg",
                salary=60000,
                category=marketing_category['title']
            ),
            Job(
                title="Customer Service Representative",
                description="Assist customers with inquiries and issues.",
                date_posted=datetime.utcnow(),
                company_id=company.id,
                company=company,
                location="Chicago",
                company_logo="img/com-logo-4.jpg",
                salary=40000,
                category=customer_service_category['title']
            )
        ]

        db.session.add_all(new_jobs)
        db.session.commit()
        print("Jobs added!")
