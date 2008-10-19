# pyrate - calculate chess ratings
# Copyright (C) 2008 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Calculate ECF grades. """

class Player:
    """ Class to use the grading functions with """
    def __init__(self, grade):
        self.grade = int(grade)
    def __int__(self):
        return self.grade

def ecf_to_elo(ecf_grade):
    """ Convert ECF grade to ELO rating """
    if ecf_grade <= 215:
        return ecf_grade * 5 + 1250
    else:
        return ecf_grade * 8 + 600

def _get_opponent_grade(own_grade, opponent_grade):
    """ Get the grade of the opponent used for calculation. This applies the 
    rule that says that for calculation the grades may not differ more 
    than 40 """
    if opponent_grade+40 < own_grade:
        return own_grade - 40
    elif opponent_grade-40 > own_grade:
        return own_grade + 40
    else:
        return opponent_grade

def get_new_grade(winner, loser, draw=False):
    """ get_new_rating(player1, player2) -> (int, int).
    Returns the new rating when winner won the game. If it has been a draw set 
    draw to True. Player objects have to have a grade attribute. """
    if not hasattr(winner, "rating") or not hasattr(loser, "rating"):
        winner = Player(int(winner))
        loser = Player(int(loser))
    
    loser_grade = _get_opponent_grade(winner.grade, loser.grade)
    winner_grade = _get_opponent_grade(loser.grade, winner.grade)

    if draw:
        winner_new_grade = loser_grade
        loser_new_grade  = winner_grade
    else:
        loser_new_grade = winner_grade - 50
        winner_new_grade = loser_grade + 50
    return (winner_new_grade, loser_new_grade)

def update_grade(winner, loser, draw=False):
    """ Update the grade attributes of winner and loser """
    (winner.grade, loser.grade) = get_new_grade(winner, loser, draw)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        sys.exit(2)
    a, b = Player(int(sys.argv[1])), Player(int(sys.argv[2]))
    print "%s - %s" % get_new_grade(a, b)
