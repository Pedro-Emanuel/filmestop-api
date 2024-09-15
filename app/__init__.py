# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        # Suas configurações normais aqui
        DATABASE_URL = 'postgresql://' + os.getenv('DB_USER') + ':' + os.getenv('DB_PASS') + '@' + os.getenv('DB_HOST') + '/' + os.getenv('DB_NAME')
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = "application/json; charset=utf-8"

    db.init_app(app)
    migrate.init_app(app, db)

    from app import routes
    app.register_blueprint(routes.bp)

    return app