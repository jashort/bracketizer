from datetime import datetime

from flask import request, session, flash, render_template, redirect, Blueprint, url_for, abort
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, HiddenField
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from bracketizer.models import Bracket, Vote, db
from bracketview import BracketView
from exceptions import BracketException

bp = Blueprint('vote', __name__, url_prefix='/vote')


class VoteForm(FlaskForm):
    choice = RadioField("Choose 1", choices=[])
    previous = HiddenField("previous")
    submit = SubmitField("Save")


@bp.route('/vote', methods=['GET', 'POST'])
def vote():
    bracket_name = request.args.get("bracket", "not_found")
    round_number = int(request.args.get("round", 1))
    question_number = int(request.args.get("question", 1))
    if 'username' not in session:
        return redirect(
            url_for('user.user', next_page="vote", bracket=bracket_name, round=round_number, question=question_number))
    try:
        my_bracket = Bracket.query.filter_by(name=bracket_name).first()
        if my_bracket.current_round != 0 or datetime.utcnow() < my_bracket.start_time:
            flash("No peeking! This round isn't open for voting")
            return redirect(url_for('index'))

        votes = Vote.query.filter_by(username=session['username'], bracket_id=my_bracket.id)

        bv = BracketView(my_bracket, votes)
        my_round = bv.get_round(round_number)
        my_form = VoteForm()
        my_form.choice.choices = bv.get_question(round_number, question_number)

        if my_form.validate_on_submit():
            # Upsert votes for a given user/bracket/round/question. You can change it as long
            # as voting is still open.
            stmt = sqlite_upsert(Vote).values([{"username": session['username'], "bracket_id": my_bracket.id,
                                                "round_number": round_number, "question_number": question_number,
                                                "choice": my_form.choice.data}
                                               ])
            stmt = stmt.on_conflict_do_update(
                index_elements=[Vote.username, Vote.bracket_id, Vote.round_number, Vote.question_number],
                set_={"choice": my_form.choice.data}
            )
            db.session.execute(stmt)
            db.session.commit()

            if question_number < my_round.total_questions():
                return redirect(
                    url_for('vote.vote', bracket=bracket_name, round=round_number, question=question_number + 1))
            elif round_number < my_bracket.total_rounds() - 1:
                return redirect(url_for('vote.vote', bracket=bracket_name, round=round_number + 1, question=1))
            else:
                flash('All done!')
                return redirect(url_for('bracket.bracket', bracket=bracket_name))
        return render_template('vote.html',
                               form=my_form,
                               bracket=my_bracket,
                               bracket_round=round_number,
                               question_number=question_number)
    except BracketException as ex:
        abort(400, description=str(ex))
