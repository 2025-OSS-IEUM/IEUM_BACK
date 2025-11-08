from flask import Flask
from flask_sqlalchemy import SQLAlchemy   # 추가
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)                      # 추가: Flask와 DB 연결

@app.route('/')
def home():
    return "Flask environment setup successful"

if __name__ == '__main__':
    app.run(debug=True)
