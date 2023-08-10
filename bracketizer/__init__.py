import os

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bootstrap = Bootstrap5()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    bootstrap = Bootstrap5(app)

    if test_config is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    with app.app_context():
        from . import routes
        db.create_all()

    return app
