from sqlalchemy import *

""" This module creates the database structure needed for the pypentago server. 
This structure differs a bit from the one in pyPentago-generate.sql and 
therefor database related code might have to change. Changes done by 
suggestion of people in #SQL @ irc.freenode.net """

def create_database(connect_string=False, drop_all=True):
    """ Create the tables needed for the pypentago database. If drop_all is 
    True it will drop all existing tables and the data in the database """
    from pypentago.server.db.sessionmanager import get_connect_string
    if not connect_string:
        connect_string = get_connect_string()
    if not drop_all:
        kwargs = {'useexisting': True}
    else:
        kwargs = {}
    engine = create_engine(connect_string)
    metadata = MetaData(engine)
        
    players = Table('Players', metadata, 
        Column('player_id', Integer, primary_key = True, index=True,
               autoincrement=True),
        Column('player_name', Text, nullable = False),
        Column('passwd_hash', String(40), nullable = False),
        Column('real_name', Text, nullable = False),
        Column('player_email', Text),
        Column('date_registered', DateTime),
        Column('activation_code', Text),
        Column('activated', Boolean),
        Column('current_rating', Integer),
        Column('player_profile', Text),
        **kwargs
    )

    
    game_hist = Table('GameHistory', metadata, 
        Column('game_id', Integer, primary_key = True, index=True,
               autoincrement=True),
        
        Column('winner_id', Integer, nullable = False),
        Column('winner_rating', Integer, nullable = False),
        Column('loser_id', Integer, nullable = False),
        Column('loser_rating', Integer, nullable = False),
        Column('pgn_string', Text),
        Column('comment_log', Text),
        Column('time_stamp', DateTime),
        Column('draw', Boolean),
        **kwargs
    )
        
    if drop_all:
        metadata.drop_all(engine)
    
    metadata.create_all(bind=engine)
if __name__ == "__main__":
    
    # Set the PYTHONPATH
    from os.path import join, dirname, abspath
    import sys
    
    script_path = abspath(dirname(__file__))
    sys.path.append(abspath(join(script_path, "..", "..", "..")))
    # End of setting the PYTHONPATH
    
    create_database()
