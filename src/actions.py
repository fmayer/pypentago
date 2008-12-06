# -*- coding: us-ascii -*-

# actions - Handle actions by defining handlers
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

"""
NOTE: Each of the examples is self-contained, which means you will have
to use a new context, clean the default context or start a new python
session in order to make them yield the displayed results.

Decorators
==========
It is also possible to register handlers using decorators.

Functions
---------
You can use the register decorator in order to register a function to an
action.

>>> @register("baz")
... def baz(state):
...     print state
... 
>>> emmit_action("baz", "state")
state
>>> 

You can also bind a function to multiple actions using the decorator syntax.

>>> @register('foo')
... @register('bar')
... def quuz(state):
...     print "spam! eggs!"
... 
>>> emmit_action('foo')
spam! eggs!
>>> emmit_action('bar')
spam! eggs!
>>> 

Bound methods
-------------
If you want to bind bound methods of your instances to actions, you need to
subclass ActionHandler and call its __init__ in the __init__ of your class
so that it registers the handlers once an instance is created.
The methods can be bound to a actions using the register_method decorator.

>>> class Handlers(ActionHandler):
...     def __init__(self):
...             ActionHandler.__init__(self)
...     @register_method("foo")
...     def foo(self, state):
...             print "foo.", state
... 
>>> handlers = Handlers()
>>> emmit_action("foo", "this is the state")
foo. this is the state
>>> 

As with normal functions, you can also bind a method to multiple actions.

>>> class Foo(ActionHandler):
...     def __init__(self):
...             ActionHandler.__init__(self)
...     @register_method('foo')
...     @register_method('bar')
...     def quuz(self, state):
...             print "spam! eggs!"
... 
>>> foo = Foo()
>>> emmit_action('foo')
spam! eggs!
>>> emmit_action('bar')
spam! eggs!
>>> 

Context
=======
The functions exposed at module level use the default context.
If you need serveral parts of your application to use actions 
independantely, specify a context object for each of them, and use 
its methods and/or pass it to the constructor of ActionHandler or 
to register when using decorators.

>>> context = Context()
>>> other_context = Context()
>>> class Foo(ActionHandler):
...     def __init__(self):
...             ActionHandler.__init__(self, context)
...     @register_method('foo')
...     def foo(self, state):
...             print "This is Foo.foo"
... 
>>> @other_context.register('foo')
... def foo(state):
...     print "This is foo"
... 
>>> foo = Foo() # Instantiate to enable bound-method binding.
>>> context.emmit_action('foo')
This is Foo.foo
>>> other_context.emmit_action('foo') # Same action in different context
This is foo
>>> emmit_action('foo') # We did not touch the default context.
>>> 

"""

import warnings

from base64 import b64decode
from collections import defaultdict

# Increment by one everytime the file's API is changed!
__version__ = 5
__author__ = "Florian Mayer"
# Import module to obtain email-address in readable form.
__contact__ = b64decode("Zmxvcm1heWVyQGFpbS5jb20=")
__license__ = "GPLv3"

FAIL = 2
WARN = 1
IGNORE = 0

def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    # I am aware that this is already implemented in inspect, but
    # a) It's better when it's a generator
    # b) I need it to swallow exceptions, some frameworks raise them
    #    when getting attributes. Don't ask me...
    for key in dir(object):
        try:
            value = getattr(object, key)
        except Exception:
            # Yes. That happens! I'm looking at you, wxPython!
            # We shouldn't need these members anyway. Go on.
            continue
        if not predicate or predicate(value):
            yield (key, value)


class StopHandling(Exception):
    """ Raising this exception in an action handler prevents all the 
    successive handlers from being executed. """
    pass


class Action:
    """ This represents an action and its handlers.
    
    You shouldn't need to use it directly as all of its functionality
    is exposed in the Context class."""
    def __init__(self):
        self.handlers = []
    
    def __call__(self, state):
        """ Call all handlers for the action """
        for callback in self.handlers:
            exc, args, kwargs, no_state = callback
            try:
                r = (no_state and exc(*args, **kwargs) or
                     exc(state, *args, **kwargs))
                yield r
            except StopHandling:
                break
    
    def __contains__(self, func):
        """ See if func is a handler of the action """
        return any(h[0] == func for h in self.handlers)
    
    def __getitem__(self, exc):
        try:
            return (h for h in self.handlers if h[0] == exc).next()
        except StopIteration:
            raise ValueError('Handler not bound to action')
    
    def __delitem__(self, exc):
        self.remove_handler(exc)
        
    def __len__(self):
        return len(self.handlers)
    
    def __iter__(self):
        for h in self.handlers:
            yield h[0]

    def __nonzero__(self):
        return bool(self.handlers)
    
    def add_handler(self, exc, *args, **kwargs):
        """ Add a handler that does take the state as the
        first argument """
        if exc in self:
            raise ValueError('Handler already registered')
        self.handlers.append((exc, args, kwargs, False))
    
    def add_nostate_handler(self, exc, *args, **kwargs):
        """ Add a handler that doesn't take state as the
        first argument """
        if exc in self:
            raise ValueError('Handler already registered')
        self.handlers.append((exc, args, kwargs, True))
    
    def remove_handler(self, exc):
        """ Remove exc from the handlers of the action """
        self.handlers.remove(self[exc])
    
    def is_state(self, handler):
        """ See if all handlers take state """
        return all(not h[4] for h in self.handlers if h[0] == handler)


class Context:
    """ The context in which the actions are defined. A default context is 
    created and its methods are exposed at module level automatically. 
    You may want to use contexts if you have got two independant things that
    both need to use actions, then you can define a context for each of them.
    """
    def __init__(self, offers=None, severity=WARN):
        self.actions = defaultdict(Action)
        self.offered = offers
        if offers is None or severity == IGNORE:
            self._not_offered = lambda x: None
        elif severity == WARN:
            self._not_offered = self._warn_if_not_offered
        elif severity == FAIL:
            self._not_offered = self._fail_if_not_offered
        else:
            raise ValueError("Invalid verbosity")
        
    def register_handler(self, action, exc, *args, **kwargs):
        """ Register exc to the action action with additional paramenters to be
        passed to the hook function. 
        
        Registering multiple hooks for the same 
        action will execute them in order of registration. """
        self._not_offered(action)
        self.actions[action].add_handler(exc, *args, **kwargs)
    
    def register_nostate_handler(self, action, exc, *args, **kwargs):
        """ Register handler that does not take state as first argument. 
        
        Please only use this rarely and only for handlers that would only take 
        None as state. Useful for binding directly to framework functions. """
        self._not_offered(action)
        self.actions[action].add_nostate_handler(exc, *args, **kwargs)
        
    def remove_handler(self, action, exc):
        """ Remove the function exc from the list of hooks for action. """
        if exc in self.actions[action]:
            self.actions[action].remove_handler(exc)
    
    def remove_function(self, exc):
        """ Remove the function exc from the list of hooks for any action. """
        for action in self.actions:
            self.remove_handler(action, exc)
        
    def delete_action(self, action):
        """ Delete all handlers associated with action. """
        del self.actions[action]
    
    def emmit_action(self, action, state=None):
        """ Call all the functions associated with action with state as first 
        argument, unless they are nostate handlers. 
        
        Returns a list of return values of all the handlers, in order
        of calling. """
        self._not_offered(action)
        return list(self.actions[action](state))
    
    def register(self, *actions):
        """ Associate decorated function with action. """
        def decorate(exc):
            for action in actions:
                self.register_handler(action, exc)
            return exc
        return decorate
    
    def clear(self):
        """ Reset context to inital state. """
        self.actions = defaultdict(Action)
    
    def offers(self, action):
        """ Tell whether the context offers given action. Always returns
        True if self.offered is None. """
        return self.offered is None or action in self.offered
    
    def has_handlers(self, action):
        """ Tell whether there are any handlers bound to action. """
        return bool(action in self.actions and self.actions[action])
    
    def _warn_if_not_offered(self, action):
        """ Warn if the context defines the actions it offers but action
        is not in them.
        
        You shouldn't need this method. """
        if not self.offers(action):
            warnings.warn("Action %r unknown by Context" % action, stacklevel=3)
    
    def _fail_if_not_offered(self, action):
        """ Raise ValueError if the context defines the actions it 
        offers but action is not in them.
        
        You shouldn't need this method. """
        if not self.offers(action):
            raise ValueError("Action %r unknown by Context" % action)
    
    def __contains__(self, action):
        return bool(action in self.actions and self.actions[action])
    
    def __getitem__(self, action):
        self._not_offered(action)
        return self.actions[action]
    
    def __delitem__(self, action):
        self.delete_action(action)


# Create default context and expose its methods on module level.
# This is useful for people who only use one context in their program.
_inst = Context()
register_handler = _inst.register_handler
register_nostate_handler = _inst.register_nostate_handler
remove_handler = _inst.remove_handler
remove_function = _inst.remove_function
delete_action = _inst.delete_action
emmit_action = _inst.emmit_action
register = _inst.register
clear = _inst.clear
offers = _inst.offers
has_handlers = _inst.has_handlers


def register_method(action, lst=None):
    """ Associate decorated method with action. Be sure to call 
    ActionHandler.__init__ in your classes __init__ method. 
    """
    if lst is not None:
        # Developer still seems to use old version including _decorators.
        warnings.warn("Using register_method with lst is deprecated", 
                      DeprecationWarning, 2)
    def decorate(exc):
        """ Append action to functions _bind_to attribute, if that does
        not exist, set it to an empty list and append to that one. """
        if not hasattr(exc, '_bind_to'):
            exc._bind_to = []
        exc._bind_to.append(action)
        return exc
    return decorate


class ActionHandler:
    """ Subclass this class for classes using the register_method decorators 
    with one or more of its methods.
    Make sure to call the __init__, otherwise the handlers will
    not be bound. 
    """
    def __init__(self, context=_inst):
        self.__actions = {}
        self.__context = context
        for name, method in getmembers(self):
            if hasattr(method, '_bind_to'):
                for bind_to in method._bind_to:
                    self.__actions[bind_to] = method
                    self.__context.register_handler(bind_to, method)
    
    def remove_actions(self):
        """ This deletes all actions that were associated with methods of the 
        class.
        
        Please note that it doesn't only delete the handlers, but also any 
        other handlers that may be associated with the given action. 
        """
        for action in self.__actions:
            self.__context.delete_action(action)
    
    def remove_handlers(self):
        """ This deassociates all handlers of this class from the actions. 
        
        In difference to remove_action this does not delete any other handlers 
        """
        for action, handler_func in self.__actions.items():
            self.__context.remove_handler(action, handler_func)
