import os
from dotenv import load_dotenv
from app.main import create_app
from app.models.models import db, User

load_dotenv()
app = create_app('development')

with app.app_context():
    try:
        user = User(username='test_user_from_script')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        print("Success!")
    except Exception as e:
        print("Error:", repr(e))
