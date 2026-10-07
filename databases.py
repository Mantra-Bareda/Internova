from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200))
    credits = db.Column(db.Integer, default=10) # 10 Free starting credits
    resumes = db.relationship('Resume', backref='user', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=True)
    version_number = db.Column(db.Integer, default=1)
    filename = db.Column(db.String(200))
    resume_text = db.Column(db.Text)
    analysis_result = db.Column(db.Text)
    internships_result = db.Column(db.Text) # Stores cached internship data
    interview_questions_result = db.Column(db.Text) # Stores cached interview questions
    career_alignment_result = db.Column(db.Text) # Stores cached alignment data
    roadmap_options_result = db.Column(db.Text) # Stores cached roadmap options
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    versions = db.relationship('Resume', backref=db.backref('parent', remote_side=[id]), lazy=True, cascade='all, delete-orphan')
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default="To Do") # To Do, In Progress, Done
    
class InterviewSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_history = db.Column(db.Text) # JSON string of conversation history
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100))
    headline = db.Column(db.String(200))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    education_details = db.Column(db.Text)
    experience_details = db.Column(db.Text)
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    portfolio_url = db.Column(db.String(200))
    
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
