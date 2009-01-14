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

from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import create_engine, MetaData

class Database(object):
    """ This class has to be sub-classed and needs the create_tables
    and the map_tables methods overriden in order to work. """
    def __init__(self, connect_string=None):
        if connect_string is not None:
            self.connect(connect_string)        
    
    def create_tables(self, metadata):
        """ Create and return your tables in here. The return value is
        passed to map_tables. 
        
        For example:
        
        def create_tables(self, metadata):
            spam = Table('SpamTable', metadata, ...)
            eggs = Table('EggsTable', metadata, ...)
            return spam, eggs
        """
        raise NotImplementedError
    
    def map_tables(self, *args):
        """ Define the mapping of the tables to classes here.
        The tables are passed to it in the order that create_tables
        returns them. 
        
        For example:
        
        def map_tables(self, spam, eggs):
            mapper(Spam, spam)
            mapper(Eggs, eggs)
        """
        raise NotImplementedError
    
    def connect(self, connect_string):
        engine = create_engine(connect_string)
        metadata = MetaData(engine)
        self.tables = self.create_tables(metadata)
        # If the tables do not exist yet - create them!
        metadata.create_all()
        # Map our classes to the tables.
        self.map_tables(*self.tables)
        
        self.Session = sessionmaker(bind=engine, 
                                    autoflush=True,
                                    transactional=True)
    
    @property
    def transaction(self):
        """ Use this with the with keyword to get a transaction.
        
        >>> with database.transaction as session:
        ...     session.save(obj)
        """
        return DatabaseConnection(self.Session)


class DatabaseConnection(object):
    """ This is to be used with the with keyword. 
    
    >>> with Database(Session) as session:
    ...     session.save(obj)
    """
    def __init__(self, Session):
        self.Session = Session
    
    def __enter__(self):
        self.session = self.Session()
        return self.session
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_tb is None:
            # No exception. Commit the transaction.
            self.session.commit()
        else:
            # Exception in code. Rollback.
            self.session.rollback()
        self.session.close()


class DatabaseObject(object):
    """ Provides a nice repr that prints out all attribues. 
    Provides a cmp that checks if all attributes are the same.
    
    Pass a dictionary to __init__ and it will set all of them as 
    attributes, e.g. {'answer': 42, 'spam': 'eggs'} will set 
    self.answer = 42 and self.spam = 'eggs'. 
    """
    def __init__(self, kwargs=None):
        if kwargs is None:
            return
        if 'self' in kwargs:
            # We don't need the reference to self!
            del kwargs['self']
        for key, kwarg in kwargs.items():
            setattr(self, key, kwarg)
    
    def __eq__(self, other):
        one = [(key, value) for key, value in vars(self).iteritems()
              if not key.startswith('_')]
        other = [(key, value) for key, value in vars(other).iteritems()
              if not key.startswith('_')]
        return dict(one) == dict(other)
    
    def __neq__(self, other):
        return not (one == other)
    
    def __repr__(self):
        attr = sorted(vars(self).items())
        cls_name = self.__class__.__name__
        # Seperator for different attributes
        sep = ',\n'+' ' * (len(cls_name)+2)
        # Formatted Attributes usable in repr
        frmt_attr = sep.join("%s=%r" % x for x in attr
                             if not x[0].startswith("_"))
        return "<%s(%s)>" % (cls_name, frmt_attr)

