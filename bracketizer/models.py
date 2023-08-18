from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, UniqueConstraint

from exceptions import BracketException

db = SQLAlchemy()



class User(db.Model):
    """ A specific user """
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())


class Bracket(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(250), nullable=False, index=True)
    current_round: int = db.Column(db.Integer, nullable=False, default=0)
    """If 0, allow voting on the entire bracket. If 1+, only allow guesses
     in that round"""
    is_open: bool = db.Column(db.Boolean, nullable=False, default=False)
    choices: [str] = db.Column(db.JSON, nullable=False, default=[])
    """All choices available in this bracket"""
    start_time = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    """Start time, UTC"""
    end_time = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
    """End time, UTC"""
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
    __table_args__ = (UniqueConstraint('username', 'bracket_id', 'round_number', 'question_number',
                                       name='_vote_uc'),
                      )

    def __repr__(self):
        return f'<Vote {self.username} {self.bracket_name} {self.round_number} {self.question_number}>'


class Guess(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(100), nullable=False, index=True)
    bracket_id = db.Column("bracket_id", db.ForeignKey(Bracket.id))
    round_number: int = db.Column(db.Integer, nullable=False, index=True)
    question_number: int = db.Column(db.Integer, nullable=False)
    choice: str = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    __table_args__ = (UniqueConstraint('username', 'bracket_id', 'round_number', 'question_number',
                                       name='_guess_uc'),
                      )

    def __repr__(self):
        return f'<Guess {self.username} {self.bracket_name} {self.round_number} {self.question_number}>'


def load_data():
    if db.session.query(Bracket).count() == 0:
        b = Bracket(name="Favorite Things",
                    is_open=True,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow() + timedelta(days=21),
                    choices=["Raindrops on roses",
                             "whiskers on kittens",
                             "Bright copper kettles",
                             "warm woolen mittens",
                             "Brown paper packages tied up with strings",
                             "Cream-colored ponies",
                             "crisp apple strudels",
                             "Doorbells"
                             ])
        c = Bracket(name="More Favorite Things",
                    is_open=True,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow() + timedelta(days=21),
                    current_round=1,
                    choices=["Raindrops on roses",
                             "whiskers on kittens",
                             "Bright copper kettles",
                             "warm woolen mittens",
                             "Brown paper packages tied up with strings",
                             "Cream-colored ponies",
                             "crisp apple strudels",
                             "Doorbells"
                             ])
        d = Bracket(name="Closed Favorite Things",
                    is_open=False,
                    start_time=datetime.utcnow() - timedelta(days=7),
                    end_time=datetime.utcnow() - timedelta(days=5),
                    current_round=4,
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
        db.session.add(c)
        db.session.add(d)
        db.session.commit()

        votes = [(1, 1, 'Raindrops on roses'),
                 (1, 2, 'warm woolen mittens'),
                 (1, 3, 'Cream-colored ponies'),
                 (1, 4, 'crisp apple strudels'),
                 (2, 1, 'Raindrops on roses'),
                 (2, 2, 'crisp apple strudels'),
                 (3, 1, 'crisp apple strudels')]
        for v in votes:
            my_vote = Vote(username="testuser", bracket_id=c.id, round_number=v[0], question_number=v[1], choice=v[2])
            db.session.add(my_vote)
        db.session.commit()


try:
    load_data()
except Exception as ex:
    print(ex)
