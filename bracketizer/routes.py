from flask import current_app as app

from .models import db, Vote, Bracket


@app.route('/', methods=['GET'])
def index():
    b = Bracket(bracket_name="test")
    db.session.add(b)
    db.session.commit()
    return "Hello"
