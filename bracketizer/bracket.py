from datetime import datetime

from flask import request, session, render_template, redirect, Blueprint, url_for, flash

from .bracketview import BracketView
from .models import db, Bracket


bp = Blueprint('bracket', __name__, url_prefix='/')


@bp.route('/bracket', methods=['GET'])
def bracket():
    bracket_name = request.args.get("bracket", "not_found")
    if 'username' not in session:
        return redirect(
            url_for('user.user', next_page="bracket", bracket=bracket_name))
    my_bracket = db.session.execute(db.select(Bracket).where(Bracket.name == bracket_name)).one()[0]
    if datetime.utcnow() < my_bracket.start_time:
        flash("No peeking! This round isn't open yet")
        return redirect(url_for('index'))

    # Don't show votes, this cuts down on the risk of cheating
    # votes = Vote.query.filter_by(username=session['username'], bracket_id=my_bracket.id)
    votes = []
    bv = BracketView(my_bracket, votes)

    return render_template('bracket.html',
                           bracket=my_bracket,
                           data=bv.to_table(),
                           header=bv.header())
