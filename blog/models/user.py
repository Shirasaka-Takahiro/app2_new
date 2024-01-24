from blog import db
from flask_login import UserMixin, LoginManager
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25))
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    terraform_executions = db.relationship('TerraformExecution', backref='project', lazy=True)

class TerraformExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    output_path = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # プロジェクトに対する外部キー制約とインデックスの追加
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), index=True, nullable=False)
    project_relation = db.relationship('Project', backref=db.backref('executions', lazy=True))