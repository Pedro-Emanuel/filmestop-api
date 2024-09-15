from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Ensure environment variables are loaded correctly
assert os.getenv('DB_USER'), "DB_USER environment variable not set"
assert os.getenv('DB_PASS'), "DB_PASS environment variable not set"
assert os.getenv('DB_HOST'), "DB_HOST environment variable not set"
assert os.getenv('DB_NAME'), "DB_NAME environment variable not set"

db = SQLAlchemy()

db_user = os.getenv('DB_USER')
db_pass = quote_plus(os.getenv('DB_PASS'))
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
    print(f"Connecting to: postgresql://{db_user}:****@{db_host}/{db_name}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = "application/json; charset=utf-8"

    db.init_app(app)

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app