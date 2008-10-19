from core import DatabaseObject

class Player(DatabaseObject):
    def __init__(self, player_name, passwd_hash, real_name, 
                 player_email, player_profile=None, current_rating=1400):
        DatabaseObject.__init__(self, locals())


class GameHistory(DatabaseObject):
    def __init__(self, winner_id, loser_id, winner_rating=0, loser_rating=0, 
                 pgn_string=None, comment_log=None):
        DatabaseObject.__init__(self, locals())
        self.time_stamp = datetime.now()
