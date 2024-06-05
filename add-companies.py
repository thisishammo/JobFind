from app import app, db, User, Company

with app.app_context():
    user = User.query.filter_by(username="thisisemployer").first()
    
    if not user:
        print("User not found. Please add a user first.")
    else:
        # Create a new company
        new_company = Company(name="Tech Innovators", description="Leading tech company", user_id=user.id)
        
        # Add and commit the new company to the database
        db.session.add(new_company)
        db.session.commit()
        print(f"Company '{new_company.name}' added!")
