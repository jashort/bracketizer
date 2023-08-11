import datetime

from flask import current_app as app, render_template

from .models import db, Bracket


@app.route('/')
def index():
    now = datetime.datetime.utcnow()
    brackets = Bracket.query.filter(Bracket.start_time<=now)
    # brackets = db.session.execute(db.select(Bracket).fiter(.order_by(Bracket.created_at)).scalars()
    return render_template('index.html', brackets=brackets, now=now)

