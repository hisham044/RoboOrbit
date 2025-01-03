# db.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(32), nullable=False)
    isStage = db.Column(db.Boolean, nullable=False, default=False)
    isGroup = db.Column(db.Boolean, nullable=False, default=False)
    limit = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=True, default="pending")
    order = db.Column(db.Integer, nullable=True, default=0)
    duration = db.Column(db.Integer, nullable=False, default=10)  # New column
    topic = db.Column(db.String(255), nullable=False, default="Sample Topic")  # New column


class ProgramList(db.Model):
    __tablename__ = 'programlist'

    id = db.Column(db.Integer, primary_key=True)
    program = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    student = db.Column(db.String(32), nullable=True)
    campus = db.Column(db.String(32), nullable=False)
    code = db.Column(db.String(10), nullable=True)
    mark = db.Column(db.Integer, nullable=True, default=0)
    status = db.Column(db.String(20), nullable=True, default="not registered")
    topic = db.Column(db.Integer, nullable=True, default=0)

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    jamiaNo = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(32), nullable=False)
    campus = db.Column(db.String(32), nullable=False)
    groupId = db.Column(db.String(20), nullable=False)
    point = db.Column(db.Integer, nullable=True, default=0)
