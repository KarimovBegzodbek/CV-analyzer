from datetime import datetime
from flask_login import UserMixin
from extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) # Hashed
    role = db.Column(db.String(20), nullable=False, default='user')
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    cvs = db.relationship('CV', backref='owner', lazy=True)

class CV(db.Model):
    __tablename__ = 'cvs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    analyses = db.relationship('Analysis', backref='cv', lazy=True)

class Analysis(db.Model):
    __tablename__ = 'analyses'
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('cvs.id'), nullable=False)
    structure_score = db.Column(db.Float, nullable=True)
    skills_score = db.Column(db.Float, nullable=True)
    formatting_score = db.Column(db.Float, nullable=True)
    content_score = db.Column(db.Float, nullable=True)
    overall_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    feedbacks = db.relationship('Feedback', backref='analysis', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    suggestions = db.Column(db.Text, nullable=False)
    recommended_roles = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
