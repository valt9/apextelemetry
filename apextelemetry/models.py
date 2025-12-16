from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions = db.relationship('RaceSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class RaceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    race_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_data = db.relationship('CarData', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RaceSession {self.name}>'

class CarData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('race_session.id'), nullable=False)
    speed = db.Column(db.Float, nullable=False)  # km/h
    rpm = db.Column(db.Float, nullable=False)  # RPM
    lap_time = db.Column(db.Float, nullable=False)  # seconds
    tire_temp = db.Column(db.Float, nullable=False)  # Celsius
    tire_wear = db.Column(db.Float, nullable=False)  # percentage
    sector_time = db.Column(db.Float, nullable=False)  # seconds
    position = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CarData {self.id}>'

class Comparison(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver1_name = db.Column(db.String(100), nullable=False)
    driver2_name = db.Column(db.String(100), nullable=False)
    data1 = db.Column(db.Text, nullable=False)  # JSON string
    data2 = db.Column(db.Text, nullable=False)  # JSON string
    race_date = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comparisons', lazy=True))
    
    def __repr__(self):
        return f'<Comparison {self.driver1_name} vs {self.driver2_name}>'

