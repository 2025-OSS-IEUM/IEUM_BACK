from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def home():
    return "Flask environment setup successful"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # models.py의 테이블 자동 생성
        print("Database tables created successfully")
    app.run(debug=True)
