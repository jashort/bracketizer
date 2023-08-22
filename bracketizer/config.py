from os import environ


class Config:
    # General Config
    SECRET_KEY = environ.get('SECRET_KEY', "dev")
    FLASK_APP = environ.get('FLASK_APP', "bracketizer")
    FLASK_ENV = environ.get('FLASK_ENV', "dev")
    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///database.db")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
