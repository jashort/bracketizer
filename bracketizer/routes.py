from flask import current_app as app, render_template

from .models import db, Bracket


@app.route('/')
def index():
    brackets = db.session.execute(db.select(Bracket).order_by(Bracket.created_at)).scalars()
    return render_template('index.html', brackets=brackets)

