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

""" 
Module used to connect GUI and network code. 

Implementation
==============
The Network code offers the hooks into which the GUI should bind it's 
functions that are needed to handle it. 

The handler functions have to look like this: 
def foo(state, bar, baz=None) if the action is bound by 
register_handler('foo', foo, 'bar', baz='baz').

Usage Example
=============
>>> def test(state, value):
...     print state
...     print value
... 
>>> register_handler('testing', test, 'Value')
>>> emmit_action('testing', 'State')
State
Value
>>>

Terminology
===========
emitter --------- function that uses "emit_action"
registrar ------- function that uses "register_handler" or 
                  "register_nostate_handler"
handler --------- function that handles an action
action ---------- event that the emitter wants a handler to handle
state ----------- information the emitter needs to pass to the handler
nostate handler - function that does not take state

Available actions
=================
registered       | state -> ID_REG/ID_NOT_REG/ID_DUP
not_logged_in    | state -> None
display_player   | state -> PlayerInfo object
turn_recv        | state -> [quadrant, row, col, rot_dir, rot_field]
in_game          | state -> None
email_available  | state -> True/False
name_available   | state -> True/False
login            | state -> True/False
game_over        | state -> ID_WIN/ID_DRAW/ID_LOST
gamelist         | state -> [GameInfo, ...]
start            | state -> True/False
conn_lost        | state -> None
conn_established | state -> Conn
"""
# Keep above list synced with the actions that are available.

import inspect
from collections import defaultdict
actions = defaultdict(list)

class StopHandling(Exception):
    """ Raising this exception in an action handler prevents all the 
    successive handlers from being executed. """
    pass

class InstanceDecorator:
    def __init__(self):
        for f_name, dec in self._decorators:
            setattr(self, f_name, dec(getattr(self, f_name)))

class ActionHandler(InstanceDecorator):
    """ All classes using @register_method must be subclasses of this and invoke
    ActionHandler.__init__ in their __init__ method. 
    They also must have a class attribute _decorators due to implementation 
    details. """
    def __init__(self):
        self._actions = []
        InstanceDecorator.__init__(self)
    def remove_actions(self):
        """ This deletes all actions that were associated with methods of the 
        class.
        
        Please note that it doesn't only delete the handlers, but also any 
        other handlers that may be associated with the given action. 
        """
        for action in self._actions:
            delete_action(action)
    def remove_handlers(self):
        """ This deassociates all handlers of this class from the actions. 
        
        In difference to remove_action this does not delete any other handlers 
        """
        for action in self._actions:
            for handler in actions[action]:
                if handler[0] is getattr(self, handler[0].__name__, False):
                    remove_handler(action, handler[0])

def instancedecorator(decorator, lst):
    """ Run decorator when klass is being instantiated. """
    def decorate(f):
        lst.append((f.__name__, decorator))
        return f
    return decorate

def register_handler(action, exc, *args, **kwargs):
    """ Register exc to the action action with additional paramenters to be 
    passed to the hook function. 
    
    Registering multiple hooks for the same 
    action will execute them in order of registration. """
    actions[action].append((exc, args, kwargs, False))

def register_nostate_handler(action, exc, *args, **kwargs):
    """ Register handler that does *NOT* take state as first argument. 
    
    Please only use this rarely and only for handlers that would only take 
    None as state. Useful for binding directly to framework functions. """
    actions[action].append((exc, args, kwargs, True))
    
def remove_handler(action, exc):
    """ Remove the function exc from the list of hooks for action. """
    actions[action] = [x for x in actions[action] if not x[0] == exc] 
    

def delete_action(action):
    """ Delete all handlers associated with action. """
    del actions[action]


def emmit_action(action, state=None):
    """ Call all the functions associated with action with state as first 
    argument, unless they are nostate handlers. """
    for callback in actions[action]:
        exc, args, kwargs, no_state = callback
        try:
            if no_state:
                # Do not pass state to nostate handlers.
                exc(*args, **kwargs)
            else:
                exc(state, *args, **kwargs)
        except StopHandling:
            break
        
def register(action):
    """ Associate decorated function with action """
    def decorate(f):
        register_handler(action, f)
        if inspect.ismethod(f):
            # Is used in ActionHandler.remove_action and 
            # ActionHandler.remove_handlers
            f.im_self._actions.append(action)
        return f
    return decorate

def register_method(action, lst):
    """ Associate action with method. lst has to be _decorators!
    The method will be registered everytime an instance is created, so be sure 
    to delete all old actions when a new instance appears. 
    
    Class of the method has to be a subclass of ActionHandler! """
    return instancedecorator(register(action), lst)


if __name__ == "__main__":
    # Only for testing purposes.
    def foo(state, bar, baz):
        print state
        print bar
        print baz
    def spam(state):
        print "Spam! Spam! More Spam!"
    def bar(baz):
        print baz
    @register('ui_foo')
    def quuz(state):
        print 'quuuuz'

    class UI(ActionHandler):
        _decorators = []
        def __init__(self):
            ActionHandler.__init__(self)
            self.foo = 'FooBar!'
        
        @register_method('ui_foo', _decorators)
        def handle_foo(self, state):
            print state, self.foo
    
    register_handler('foo', foo, baz='baz', bar='spam')
    register_handler('foo', spam)
    register_nostate_handler('bar', bar, baz="Test")
    print "State handler"
    print "============="
    emmit_action('foo', 'eggs')
    
    print 
    print "Nostate handler"
    print "==============="
    emmit_action('bar', ('This', 'state', 'is', 'ignored'))
    
    print 
    print "Method handler"
    print "=============="
    ui = UI()
    emmit_action('ui_foo', "Handling")
    # Trying out ActionHandler.remove_handlers:
    ui.remove_handlers()
    emmit_action('ui_foo', "Handling")
