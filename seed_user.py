from app import app, db
from models import User
from security import hash_password

def create_seed_user():
    with app.app_context():
        admin_email = "admin@example.com" # 시드 사용자 이메일(default)
        existing = User.query.filter_by(email=admin_email).first()

        if not existing:
            user = User(
                email=admin_email,
                username="admin", # 기본 사용자 이름(default: admin)
                password=hash_password("admin123"), # 해시된 비밀번호(default: admin123)
                level=1,
                exp=0
            )
            db.session.add(user)
            db.session.commit()
            print("Seed user created")
        else:
            print("Seed user already exists")

if __name__ == "__main__":
    create_seed_user()

