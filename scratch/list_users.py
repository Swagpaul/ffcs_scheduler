from app.main import create_app
from app.models.models import User, db

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Total registered users: {len(users)}")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}")
