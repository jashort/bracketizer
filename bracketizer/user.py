import uuid

from flask import request, session, flash, render_template, redirect, Blueprint, url_for, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

bp = Blueprint('user', __name__, url_prefix='/')


class UserForm(FlaskForm):
    username = StringField("Name", validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField("Save")


@bp.route('/user', methods=['GET', 'POST'])
def user():
    my_form = UserForm()
    bracket_name = request.args.get("bracket", None)
    round_number = int(request.args.get("round", 1))
    question_number = int(request.args.get("question", 1))
    next_page = request.args.get("next_page", None)

    if 'username' in session and my_form.username.data is None:
        my_form.username.data = session['username']
    if my_form.validate_on_submit():
        flash(f"Welcome {my_form.username.data}")
        session['username'] = my_form.username.data
        if 'session_uuid' not in session or session['session_uuid'] is None:
            session['session_uuid'] = uuid.uuid4().hex
        current_app.logger.info(f"{session['username']} set in session {session['session_uuid']}")

        if next_page is None:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
            # return redirect(url_for(next_page, bracket=bracket_name, round=round_number, question=question_number))

    return render_template('user.html',
                           form=my_form,
                           bracket=bracket_name,
                           bracket_round=round_number,
                           question_number=question_number)
