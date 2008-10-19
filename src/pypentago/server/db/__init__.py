from __future__ import with_statement

from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import (create_engine, MetaData, Table, Text, String, Boolean,
                        DateTime, Column, Integer)

from pypentago.server.db.core import transactionmaker, DatabaseObject
from pypentago.exceptions import NotInDB
from pypentago.server.db.dbobjs import Player, GameHistory


def create_tables(metadata):
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
        )
    return players, game_hist

transaction = None
def connect(connect_string):
    engine = create_engine(connect_string)
    metadata = MetaData(engine)
    players, game_hist = create_tables(metadata)
    # If the tables do not exist yet - create them!
    metadata.create_all()
    # Map our classes to the tables.
    mapper(GameHistory, game_hist)
    mapper(Player, players)
    global transaction
    transaction = transactionmaker(
        sessionmaker(bind=engine, 
                     autoflush=True, transactional=True)
        )
    return transaction


def players_by_login(login):
    with transaction() as session:
        players = session.query(Player).filter_by(
            player_name=login)
    if players.count() < 1:
        # No player with that login.
        raise NotInDB
    return players.all()


def player_by_id(identifier):
    with transaction() as session:
        player = session.query(Player).get(identifier)
    return player


def login_available(login):
    try:
        players_by_login(login)
    except NotInDB:
        return True
    return False


def email_available(email):
    try:
        players_by_email(email)
    except NotInDB:
        return True
    return False


def players_by_email(email):
    with transaction() as session:
        players = session.query(Player).filter_by(
                player_email=email)
    if players.count() < 1:
        # No player with that login.
        raise NotInDB
    return players.all()
