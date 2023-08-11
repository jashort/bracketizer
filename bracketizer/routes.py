import datetime
import os

from flask import current_app as app, render_template, send_from_directory

from .models import Bracket


@app.route('/')
def index():
    now = datetime.datetime.utcnow()
    brackets = Bracket.query.filter(Bracket.start_time <= now)
    return render_template('index.html', brackets=brackets, now=now)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')
