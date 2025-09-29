from extensions import db
from flask_login import UserMixin

class Parent(UserMixin, db.Model):
    __tablename__ = "parent"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    kids = db.relationship("Kid", backref="parent", lazy=True)

class Kid(db.Model):
    __tablename__ = "kid"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)          # daily points
    weekly_points = db.Column(db.Integer, default=0)   # weekly total
    parent_id = db.Column(db.Integer, db.ForeignKey("parent.id"))

    tasks = db.relationship("Task", backref="kid", lazy=True)

class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=5)
    completed = db.Column(db.Boolean, default=False)
    kid_id = db.Column(db.Integer, db.ForeignKey("kid.id"))
