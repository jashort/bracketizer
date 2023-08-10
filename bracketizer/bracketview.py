import dataclasses
import hashlib

from exceptions import BracketException

from bracketizer.models import Bracket, Vote


@dataclasses.dataclass
class Choice:
    name: str
    votes: int = 0

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Choice):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return False

    def __str__(self):
        return self.name

    def __hash__(self):
        return self.name.__hash__()


@dataclasses.dataclass
class Round:
    round_number: int
    choices: [str]

    def total_questions(self) -> int:
        return int(len(self.choices) / 2)

    def get_question(self, number: int) -> (str, str):
        """Returns the two choices. Question number 1 returns choice 0 and 1, and so on"""
        if number < 1:
            raise BracketException(f"The first question is number 1")
        if number > len(self.choices) / 2:
            raise BracketException(f"Requested question {number} but there are only {self.total_questions()}")
        else:
            pos = ((number - 1) * 2)
            return self.choices[pos], self.choices[pos + 1]

    def __repr__(self):
        return f"Round {self.round_number}, {len(self.choices)} choices"


class BracketView:
    """ Combines a Bracket and a list of votes in to a final representation
    of a bracket"""

    def __init__(self, bracket: Bracket, votes: [Vote]):
        self._bracket = bracket
        self._votes = votes
        self.name = self._bracket.name
        self.total_rounds = self._bracket.total_rounds()
        self._rounds = []
        self._rounds.append(Round(1, [Choice(c) for c in self._bracket.choices]))
        self._score()

    def longest_name(self) -> int:
        longest = 0
        for c in self._bracket.choices:
            if len(c) > longest:
                longest = len(c)
        return longest

    def get_round(self, number: int) -> Round:
        """Returns round number [number] or a synthetic round"""
        if number - 1 < len(self._rounds):
            return self._rounds[number - 1]
        else:
            choice_count = len(self._bracket.choices)
            i = 1
            while i < number:
                i = i + 1
                choice_count = choice_count / 2
            choices = []
            for i in range(int(choice_count)):
                choices.append(Choice("__________", 0))
            return Round(round_number=number, choices=choices)

    def header(self):
        output = []
        i = 1
        while i <= self.total_rounds:
            output.append(f"Round {i}")
            i += 1
        return output

    def to_table(self) -> []:
        data = []
        # Generate grid
        for i in range(len(self._bracket.choices) * 2):
            data.append([""] * (self.total_rounds))

        spaces = 2  # spaces between items in first round
        offset = 0  # vertical offset
        round_number = 1

        # Add one to get the final winning round as well
        while round_number <= self.total_rounds:
            this_round = self.get_round(round_number)
            for i in range(len(this_round.choices)):
                row_number = i * spaces + offset
                data[row_number][round_number - 1] = this_round.choices[i]
            round_number += 1
            spaces = spaces * 2
            offset = offset * 2 + 1

        col_width = self.longest_name() + 4
        rounds = []
        for i in range(1, self.total_rounds + 1):
            rounds.append(f"Round {i}".ljust(col_width))
        return data

    def _score(self):
        """Combine the Bracket with any Votes to generate a final representation"""
        round_number = 1
        while round_number < self.total_rounds:
            round_votes: [] = [v for v in self._votes if v.round_number == round_number]

            cur_round = self.get_round(round_number)
            next_round = Round(round_number + 1, choices=[])

            question_number = 1
            winners = []
            while question_number <= cur_round.total_questions():
                question_votes: [Vote] = [v for v in round_votes if v.question_number == question_number]

                c1, c2 = cur_round.get_question(question_number)
                counts = {c1: 0, c2: 0}
                for v in question_votes:
                    if v.choice == c1:
                        counts[c1] += 1
                    elif v.choice == c2:
                        counts[c2] += 1
                if counts[c1] == 0 and counts[c2] == 0:
                    winners.append(Choice("__________", 0))
                elif counts[c1] > counts[c2]:
                    winners.append(Choice(c1.name, 0))
                elif counts[c1] == counts[c2]:
                    h1 = hashlib.md5(c1.name.encode("utf-8")).hexdigest()
                    h2 = hashlib.md5(c2.name.encode("utf-8")).hexdigest()
                    if h1 < h2:
                        winners.append(Choice(c1.name, counts[c1]))
                        print(f"Tie! Using {c1}")
                    else:
                        winners.append(Choice(c2.name, 0))
                else:
                    winners.append(Choice(c2.name, 0))
                question_number += 1
                # Add vote counts to the current round
                for c in self.get_round(round_number).choices:
                    if c in counts:
                        c._votes = counts[c]
            next_round.choices = winners
            self._rounds.append(next_round)

            round_number += 1

    def get_question(self, bracket_round: int, question: int) -> (str, str):
        my_round = self.get_round(bracket_round)
        return my_round.get_question(question)
