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

""" Calculate ELO ratings """

#: Trigger use of 350 rule. See http://www.chesselo.com/350_rule.html
RULE_350 = True

class Player:
    """ Class to use the rating functions with """
    def __init__(self, rating):
        self.rating = int(rating)
    def __int__(self):
        return self.rating

def elo_to_ecf(elo_rating):
    """ Convert ELO rating to EFC grade """
    if elo_rating > 2320:
        return (elo_rating - 600) / 8
    else:
        return (elo_rating - 1250) / 5
        
def _determine_rating_constant(rating):
    """ Get the rating constant to ensure weaker players gain points faster """
    if rating < 2000:
        return 30
    elif rating <= 2400:
        return 130-rating/20
    else:
        return 10

def _calculate_new_rating(player1Rating, player2Rating, outcome):
    """ Calculate new rating for player1 if his rating was player1Rating. 
    Do not use this function directly but rather get_new_rating to get the new 
    ratings for both players """
    if RULE_350:        
        if player2Rating + 350 < player1Rating:
            player2Rating = player1Rating - 350
        elif player2Rating - 350 > player1Rating:
            player2Rating = player1Rating + 350
                
    d = player1Rating - player2Rating
    exponent = -d/float(400)
    expected_outcome = 1/float(1+10 ** exponent)
    c = _determine_rating_constant(player1Rating)
    new_rating = round(player1Rating + c * (outcome - expected_outcome))
    return int(new_rating)

def get_new_rating(winner, loser, draw=False):
    """ get_new_rating(player1, player2) -> (int, int).
    Returns the new rating when winner won the game. If it has been a draw set 
    draw to True. Player objects have to have a rating attribute. """
    if not hasattr(winner, "rating") or not hasattr(loser, "rating"):
        winner = Player(int(winner))
        loser = Player(int(loser))
    if draw:
        winner_rating = _calculate_new_rating(winner.rating, loser.rating, 0.5)
        loser_rating = _calculate_new_rating(loser.rating, winner.rating, 0.5)
    else:
        winner_rating = _calculate_new_rating(winner.rating, loser.rating, True)
        loser_rating = _calculate_new_rating(loser.rating, winner.rating, False)
    return (winner_rating, loser_rating)

def update_rating(winner, loser, draw=False):
    """ Update rating attributes of winner and loser """
    winner.rating, loser.rating = get_new_rating(winner, loser, draw)
    

if __name__ == "__main__":
    import sys
    if not len(sys.argv) == 3:
        sys.exit(2)
    a, b = Player(int(sys.argv[1])), Player(int(sys.argv[2]))
    print "%s - %s" % get_new_rating(a, b)
