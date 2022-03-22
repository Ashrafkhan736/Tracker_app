from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String,  nullable=False)
    trackers = db.relationship('Tracker_info', backref='user', lazy=True)


class Tracker_info(db.Model):
    tracker_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    description = db.Column(db.String, nullable=False)
    tracker_type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=False)

    options = db.Column(db.String, nullable=True, default=None)
    numerical_log = db.relationship(
        'Numerical_log', backref='tracker_info', lazy=True)
    mcq_log = db.relationship(
        'Mcq_log', backref='tracker_info', lazy=True)


class Numerical_log(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    value = db.Column(db.Float, nullable=False)
    note = db.Column(db.String, nullable=True)
    tracker_id = db.Column(
        db.Integer, db.ForeignKey('tracker_info.tracker_id'), nullable=False)


class Mcq_log(db.Model):
    __tablename__ = "mcq_log"
    log_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String, nullable=True)
    tracker_id = db.Column(
        db.Integer, db.ForeignKey('tracker_info.tracker_id'), nullable=False)
