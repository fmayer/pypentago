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

