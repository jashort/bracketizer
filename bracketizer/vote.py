from datetime import datetime

from flask import request, session, flash, render_template, redirect, Blueprint, url_for, abort
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, HiddenField

from bracketizer.models import Bracket, Vote, db
from bracketview import BracketView
from exceptions import BracketException

bp = Blueprint('vote', __name__, url_prefix='/')


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
        if my_bracket.current_round != 0 or datetime.utcnow() < my_bracket.start_time or not my_bracket.is_open:
            flash("No peeking! This bracket isn't open for voting")
            return redirect(url_for('index'))

        user_vote_count = Vote.query.filter_by(username=session['username'], bracket_id=my_bracket.id).count()
        if user_vote_count > 0:
            flash(f"It looks like you've already voted in {bracket_name}")
            return redirect(url_for('index'))

        if 'votes' in session:
            votes = [Vote(username=session['username'],
                          bracket_id=my_bracket.id,
                          round_number=v['r'],
                          question_number=v['q'],
                          choice=v['c']) for v in session['votes']]
        else:
            votes = []

        bv = BracketView(my_bracket, votes)
        my_round = bv.get_round(round_number)
        my_form = VoteForm()
        my_form.choice.choices = bv.get_question(round_number, question_number)

        if my_form.validate_on_submit():
            if 'votes' not in session or session['votes'] is None:
                session['votes'] = []
            session['votes'].append(
                {"b_id": my_bracket.id,
                 "r": round_number,
                 "q": question_number,
                 "c": my_form.choice.data}
            )
            session.modified = True

            if question_number < my_round.total_questions():
                return redirect(
                    url_for('vote.vote', bracket=bracket_name, round=round_number, question=question_number + 1))
            elif round_number < my_bracket.total_rounds() - 1:
                return redirect(url_for('vote.vote', bracket=bracket_name, round=round_number + 1, question=1))
            else:
                # Should have votes for every question, persist to database
                # From the session, filter votes that are for this bracket vs not
                to_keep_in_session = []
                to_save = []
                for v in session['votes']:
                    if v['b_id'] == my_bracket.id:
                        to_save.append(v)
                    else:
                        to_keep_in_session.append(v)

                # Convert to ORM objects and save them in the database
                db_votes = []
                for v in to_save:
                    db_votes.append(
                        Vote(username=session['username'],
                             bracket_id=my_bracket.id,
                             round_number=v['r'],
                             question_number=v['q'],
                             choice=v['c']
                             ))
                db.session.add_all(db_votes)
                db.session.commit()

                # Remove votes for this bracket from the session. There's a
                # race condition here (session is saved between browser tabs)
                # but practically I don't expect that to matter. Is someone really
                # switching back and forth between tabs voting in different brackets in
                # the same session? Doubtful.
                # TODO: Show a "what your votes were" page once, THEN clear votes from
                # TODO: the session.
                session['votes'] = to_keep_in_session
                session.modified = True
                flash('Saved!')
                return redirect(url_for('bracket.bracket', bracket=bracket_name))
        return render_template('vote.html',
                               form=my_form,
                               bracket=my_bracket,
                               bracket_round=round_number,
                               question_number=question_number)
    except BracketException as ex:
        abort(400, description=str(ex))
