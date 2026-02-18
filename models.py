from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SecurityQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300))
    answer = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime)
