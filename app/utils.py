from flask import jsonify
from typing import Dict, Any

class ResponseFactory:
    @staticmethod
    def create_response(data: Dict[str, Any], status_code: int) -> tuple:
        return jsonify(data), status_code

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            from app import db
            cls._instance.db = db
        return cls._instance

    def get_session(self):
        return self.db.session

class DatabaseRepository:
    @staticmethod
    def get_by_id(model, id):
        return DatabaseManager().get_session().get(model, id)

    @staticmethod
    def add(model_instance):
        session = DatabaseManager().get_session()
        session.add(model_instance)
        session.commit()

    @staticmethod
    def delete_all():
        from app.models import Rental, Movie, User
        session = DatabaseManager().get_session()
        Rental.query.delete()
        Movie.query.delete()
        User.query.delete()
        session.commit()