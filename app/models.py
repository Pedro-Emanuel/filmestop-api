# -*- coding: utf-8 -*-

from app import db
from datetime import datetime
import secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    admin_token = db.Column(db.String(64), unique=True)
    rentals = db.relationship('Rental', backref='user', cascade='all, delete-orphan', lazy=True)

    def generate_admin_token(self):
        self.admin_token = secrets.token_hex(32)
        db.session.commit()
        return self.admin_token
    
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    synopsis = db.Column(db.Text)
    director = db.Column(db.String(100))
    rentals = db.relationship('Rental', backref='movie', cascade='all, delete-orphan', lazy=True)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    rental_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rating = db.Column(db.Float)