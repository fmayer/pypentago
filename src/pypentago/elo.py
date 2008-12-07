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
    """ Class with which update_rating can be used. Please mind that it is
    senseless to subclass this class, because any object with a rating 
    attribute will just work fine. """
    def __init__(self, rating):
        self.rating = int(rating)

    def __int__(self):
        return self.rating


def elo_to_ecf(elo_rating):
    """ Convert ELO rating to EFC grade. There may be a small inaccuracy due
    to rounding. """
    if elo_rating > 2320:
        return (elo_rating - 600) / 8
    else:
        return (elo_rating - 1250) / 5


def _determine_rating_constant(rating):
    """ Get the rating constant to ensure weaker players gain points faster.

    This function should only be used internally by get_new_rating and is
    thus not exposed as API. """
    if rating < 2000:
        return 30
    elif rating <= 2400:
        return 130-rating/20
    else:
        return 10


def _calculate_new_rating(player_rating, opponent_rating, outcome):
    """ Calculate new rating for player1 if his rating was player_rating. 
    Do not use this function directly but rather get_new_rating to get the new 
    ratings for both players. 

    New rating is only calculated for player with player_rating, 
    the opponent_rating is only important to tell how many points the player 
    gained or lost. 

    outcome is either 1 for win, 0 for loss or 0.5 for draw. outcome is from
    the position of the player with the rating player_rating.
    """
    if RULE_350:        
        if opponent_rating + 350 < player_rating:
            opponent_rating = player_rating - 350
        elif opponent_rating - 350 > player_rating:
            opponent_rating = player_rating + 350

    d = player_rating - opponent_rating
    exponent = -d/float(400)
    expected_outcome = 1/float(1+10 ** exponent)
    c = _determine_rating_constant(player_rating)
    new_rating = round(player_rating + c * (outcome - expected_outcome))
    return int(new_rating)


def get_new_rating(winner_rating, loser_rating, draw=False):
    """ get_new_rating(int winner_rating, int loser_rating) -> (int, int).
    Returns the new rating for both players assuming the player with
    winner_rating has won the game, unless draw is set to True. 

    >>> get_new_rating(1200, 1230)
    (1216, 1214)
    >>> get_new_rating(1200, 1230, True)
    (1201, 1229)
 
    This example shows that when a draw is played, the better player loses 
    points, because he was supposed to win the game, according to the 
    rating, while the worse player gains points, because it seems that 
    he was as good as the better player in that very game.
    """
    # If it is a draw both players have outcome of 0.5, else winner has 1
    # while the loser has 0.
    outcome_winner = draw and 0.5 or 1
    outcome_loser = draw and 0.5 or 0 
    winner_rating = _calculate_new_rating(winner_rating, loser_rating, 
                                          outcome_winner)
    loser_rating = _calculate_new_rating(loser_rating, winner_rating, 
                                         outcome_loser)
    return (winner_rating, loser_rating)


def update_rating(winner, loser, draw=False):
    """ Update rating attributes of winner and loser. winner and loser have
    to be objects with a rating attribute containing the current elo rating 
    of the player. 

    >>> a, b = Player(1200), Player(1230)
    >>> update_rating(a, b)
    >>> a.rating, b.rating
    (1216, 1214)

    In this example, the lower-rated player a won a game about the 
    higher-ranked player b, thus he gains rating points while b loses them.
    """
    winner.rating, loser.rating = get_new_rating(winner.rating, loser.rating, 
                                                 draw)


if __name__ == "__main__":
    # Cheap command line interface for testing.
    import sys
    if len(sys.argv) != 3:
        sys.exit(2)
    a, b = int(sys.argv[1]), int(sys.argv[2])
    print "%s - %s" % get_new_rating(a, b)
