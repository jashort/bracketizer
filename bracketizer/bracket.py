from flask import request, session, render_template, redirect, Blueprint, url_for

from bracketview import BracketView
from .models import db, Bracket, Vote


bp = Blueprint('bracket', __name__, url_prefix='/bracket')


@bp.route('/bracket', methods=['GET'])
def bracket():
    bracket_name = request.args.get("bracket", "not_found")
    if 'username' not in session:
        return redirect(
            url_for('username', next_page="bracket", bracket=bracket_name))
    my_bracket = db.session.execute(db.select(Bracket).where(Bracket.name == bracket_name)).one()[0]
    votes = Vote.query.filter_by(username=session['username'], bracket_id=my_bracket.id)

    bv = BracketView(my_bracket, votes)

    return render_template('bracket.html',
                           bracket=my_bracket,
                           data=bv.to_table(),
                           header=bv.header())
