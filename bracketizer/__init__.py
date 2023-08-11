import os

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
        from . import user, bracket, vote, guess
        app.register_blueprint(user.bp)
        app.register_blueprint(bracket.bp)
        app.register_blueprint(vote.bp)
        app.register_blueprint(guess.bp)
        db.create_all()

    return app
