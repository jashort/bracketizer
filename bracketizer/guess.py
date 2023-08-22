from datetime import datetime

from flask import request, session, flash, render_template, redirect, Blueprint, url_for, abort
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from .models import Bracket, Vote, db, Guess
from .bracketview import BracketView
from .exceptions import BracketException
from .vote import VoteForm

bp = Blueprint('guess', __name__, url_prefix='/')


@bp.route('/guess', methods=['GET', 'POST'])
def guess():
    bracket_name = request.args.get("bracket", "not_found")
    round_number = int(request.args.get("round", 1))
    question_number = int(request.args.get("question", 1))
    if 'username' not in session:
        return redirect(
            url_for('user.user', next_page="vote", bracket=bracket_name, round=round_number, question=question_number))
    try:
        my_bracket = Bracket.query.filter_by(name=bracket_name).first()
        if my_bracket.current_round != round_number \
                or datetime.utcnow() < my_bracket.start_time \
                or datetime.utcnow() > my_bracket.end_time \
                or not my_bracket.is_open:
            flash("No peeking! This round isn't open for guessing")
            return redirect(url_for('index'))

        votes = Vote.query.filter_by(bracket_id=my_bracket.id)

        bv = BracketView(my_bracket, votes)
        my_round = bv.get_round(round_number)
        my_form = VoteForm()
        my_form.choice.choices = bv.get_question(round_number, question_number)

        if my_form.validate_on_submit():
            # Upsert votes for a given user/bracket/round/question. You can change it as long
            # as voting is still open.
            stmt = sqlite_upsert(Guess).values([{"username": session['username'], "bracket_id": my_bracket.id,
                                                 "round_number": round_number, "question_number": question_number,
                                                 "choice": my_form.choice.data}
                                                ])
            stmt = stmt.on_conflict_do_update(
                index_elements=[Guess.username, Guess.bracket_id, Guess.round_number, Guess.question_number],
                set_={"choice": my_form.choice.data}
            )
            db.session.execute(stmt)
            db.session.commit()

            if question_number < my_round.total_questions():
                return redirect(
                    url_for('guess.guess', bracket=bracket_name, round=round_number, question=question_number + 1))
            else:
                flash('Done with this round!')
                return redirect(url_for('index'))
        return render_template('vote.html',
                               form=my_form,
                               bracket=my_bracket,
                               bracket_round=round_number,
                               question_number=question_number)
    except BracketException as ex:
        abort(400, description=str(ex))
