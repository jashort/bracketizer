from sqlalchemy import func
from sqlalchemy.sql import expression

from exceptions import BracketException
from . import db


class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())


class Bracket(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    bracket_name: str = db.Column(db.String(250), nullable=False, index=True)
    choices: [str] = db.Column(db.JSON, nullable=False, default=[])
    start_time = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    end_time = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def total_rounds(self) -> int:
        """Returns the total number of rounds in this bracket, including the
        final winner (only one choice)"""
        total_choices = len(self.choices)
        if total_choices < 2:
            raise BracketException("Not enough choices, you must have at least 2")
        # Check to see if the number of choices is a power of two
        if (total_choices & (total_choices - 1) != 0) or total_choices == 0:
            raise BracketException("You must have an even number of choices!")
        rounds = 0
        while total_choices > 1:
            rounds += 1
            total_choices = total_choices / 2
        # That will get us the number of rounds where there are at least
        # two choices, add one for the final round with the winner
        return rounds + 1



class Vote(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.ForeignKey(User.id))
    username: str = db.Column(db.String(100), nullable=False, index=True)
    bracket_id = db.Column("bracket_id", db.ForeignKey(Bracket.id))
    round_number: int = db.Column(db.Integer, nullable=False, index=True)
    question_number: int = db.Column(db.Integer, nullable=False)
    choice: str = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __repr__(self):
        return f'<Vote {self.username} {self.bracket_name} {self.round_number} {self.question_number}>'


def load_data():
    if db.session.query(Bracket).count() == 0:
        b = Bracket(bracket_name="Favorite Things",
                    choices=["Raindrops on roses",
                             "whiskers on kittens",
                             "Bright copper kettles",
                             "warm woolen mittens",
                             "Brown paper packages tied up with strings",
                             "Cream-colored ponies",
                             "crisp apple strudels",
                             "Doorbells"
                             ])
        db.session.add(b)
        db.session.commit()

try:
    load_data()
except:
    pass