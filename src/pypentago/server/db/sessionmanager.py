# pyPentago - a board game
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

import sqlalchemy
from sqlalchemy.orm import mapper
from sqlalchemy.orm import clear_mappers
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session
from sqlalchemy.orm import relation
from player import Player
from gamehistory import GameHistory
from os.path import split, join
from ConfigParser import ConfigParser
from pypentago.get_conf import get_conf_obj
def get_connect_string():
    """ Get the connect string from the config file """
    # Implemented because it is needed in create_db too, so we do not have the 
    # code two times
    config = get_conf_obj('server', 'dbconf')

    db_driver = config.get('database','dbdriver')
    db_host   = config.get('database','dbhost')
    db_port   = str(config.get('database','dbport'))
    db_user   = config.get('database','dbuser')
    db_name   = config.get('database','dbname')
    db_pass   = config.get('database','dbpass')
    if db_driver == 'sqlite':
        # SQLite ignores anything but driver and db_name.
        # If any other databases do this add to if clause above.
        connect_string = '%s:///%s' % (db_driver, db_name)
    else:
        # Any other databases that use normal connect string
        if hasattr(str, "format"):
            # Much clearer format that will be used for Python 3.0
            connect_string = ("{db_driver}://{db_user}:{db_pass}@{db_host}:"
                              "{db_port}/{db_name}".format(**locals()))
        else:
            # Old format for pre-Python 3.0
            connect_string = db_driver+"://"+db_user+":"+db_pass+"@"+\
                           db_host+":"+db_port+"/"+db_name
    return connect_string
class SessionManager:
    def __init__(self):
        connect_string = get_connect_string()
        self.engine = sqlalchemy.create_engine(connect_string)
        self.mdata = sqlalchemy.MetaData()

        self.mdata.bind = self.engine
        self.player_table = sqlalchemy.Table('Players', self.mdata, 
                                             autoload=True)
        self.gamehistory_table = sqlalchemy.Table('Gamehistory', self.mdata, 
                                                  autoload=True)

        Session = sessionmaker(bind=self.engine, autoflush=True, 
                               transactional=True)

        #>>> from sqlalchemy.orm import sessionmaker
        #>>> Session = sessionmaker(bind=engine, autoflush=True, 
        #                           transactional=True)
        #>>> Session = sessionmaker(autoflush=True, transactional=True)
        #>>> Session.configure(bind=engine)  # once engine is available
        #>>> session = Session()

        # Should the following not be self.session = Session().
        # See http://www.sqlalchemy.org/docs/04/ormtutorial.html
        self.session = session.Session()

        clear_mappers()
        mapper(Player, self.player_table)        
        mapper(GameHistory, self.gamehistory_table)

    def get_session(self):
        return self.session

    def save_single(self, aObject):
        trans = self.session.create_transaction()
        try:
            self.session.save(aObject)
        except:
            trans.rollback()
            raise
        trans.commit()

    def update_single(self, aObject):
        trans = self.session.create_transaction()
        try:
            self.session.save_or_update(aObject)
        except:
            trans.rollback()
            raise
        trans.commit()

    def delete_single(self, aObject):
        trans = self.session.create_transaction()
        try:
            self.session.delete(aObject)
        except:
            trans.rollback()
            raise
        trans.commit()
        

