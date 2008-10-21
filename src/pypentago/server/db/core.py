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

def transactionmaker(Session):
    def transaction():
        return DatabaseConnection(Session)
    return transaction


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
    
    def __cmp__(self, other):
        return vars(self) == vars(other)
    
    def __repr__(self):
        attr = sorted(vars(self).items())
        cls_name = self.__class__.__name__
        # Seperator for different attributes
        sep = ',\n'+' ' * (len(cls_name)+2)
        # Formatted Attributes usable in repr
        frmt_attr = sep.join("%s=%r" % x for x in attr
                             if not x[0].startswith("_"))
        return "<%s(%s)>" % (cls_name, frmt_attr)

