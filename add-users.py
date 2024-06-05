from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():    
    user1 = User(username="thisishammo", email="hammondkakhayanga@gmail.com", password=generate_password_hash("hammond128", method='pbkdf2:sha256'), is_employer=False)
    user2 = User(username="thisisemployer", email="hammondkakhayanga@outlook.com", password=generate_password_hash("hammond128", method='pbkdf2:sha256'), is_employer=True)

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    print("Users added!")
