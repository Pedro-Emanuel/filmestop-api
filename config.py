import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    JSONIFY_MIMETYPE = "application/json; charset=utf-8"
    
    @staticmethod
    def get_database_url():
        return 'postgresql://' + os.getenv('DB_USER') + ':' + os.getenv('DB_PASS') + '@' + os.getenv('DB_HOST') + '/' + os.getenv('DB_NAME')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_url()

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = Config.get_database_url()

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}