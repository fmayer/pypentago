#! /usr/bin/env python
# -*- coding: us-ascii -*-

# pypentago - a board game
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


""" This module defines the tests and the behaviour of actions """

import unittest
from actions import (
    ActionHandler, register_handler, register_method, register,
    emmit_action, clear, register_nostate_handler, Context, 
    FAIL, has_handlers, remove_function, remove_handler, _inst,
    StopHandling
)

class TestAction(unittest.TestCase):
    def test_offers(self):
        context = Context(['answer'], FAIL)
        # Test cases where it should fail.
        self.assertRaises(ValueError, context.register_handler,
                          'foo', lambda x: 'bar')
        self.assertRaises(ValueError, context.register_nostate_handler,
                          'foo', lambda: 'bar')
        self.assertRaises(ValueError, context.emmit_action, 'bar')
        # Test case where it shouldn't fail.
        context.register_handler('answer', lambda x: 42)
        self.assertEqual(context.emmit_action('answer'), [42])
    
    def test_same_handler(self):
        def handler(x):
            return x
        register_handler('foo', handler)
        self.assertRaises(ValueError, register_handler, 'foo', handler)
    
    def test_has_handlers(self):
        def handler(x):
            return 2 * x
        self.assertEqual(has_handlers('foo'), False)
        register_handler('foo', handler)
        self.assertEqual(has_handlers('foo'), True)
        remove_function(handler)
        self.assertEqual(has_handlers('foo'), False)
    
    def test_multiple_actionhandler(self):
        class Foo(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self)
                self.test = "foobar"
            
            @register_method('foo')
            def foo(self, state):
                return self.test
            
            @register_method('bar')
            def bar(self, state):
                return "bar"
        
        foo = Foo()
        bar = Foo()
        self.assertEqual(emmit_action('foo'), 2*['foobar'])
        self.assertEqual(emmit_action('bar'), 2*['bar'])
        
    def test_actionhandler(self):
        class Foo(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self)
                self.test = "foobar"
            
            @register_method('foo')
            def foo(self, state):
                return self.test
            
            @register_method('bar')
            def bar(self, state):
                return "bar"
        
        foo = Foo()
        self.assertEqual(emmit_action('foo'), ['foobar'])
        self.assertEqual(emmit_action('bar'), ['bar'])
    
    def test_removemethods(self):
        class Foo(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self)
                self.test = "foobar"
            
            @register_method('foo')
            def foo(self, state):
                return self.test
            
            @register_method('bar')
            def bar(self, state):
                return "bar"
        
        foo = Foo()
        bar = Foo()   
        remove_handler('foo', foo.foo)
        self.assertEqual(emmit_action('foo'), ['foobar'])
        self.assert_(foo.foo not in _inst.actions['foo'])
        remove_function(bar.foo)
        self.assertEqual(emmit_action('foo'), [])
    
    def test_removehandlers(self):
        class Foo(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self)
                self.test = "foobar"
            
            @register_method('foo')
            def foo(self, state):
                return self.test
        
        foo = Foo()
        register_handler('foo', lambda x: 'foo')
        self.assertEqual(emmit_action('foo'), ['foobar', 'foo'])
        foo.remove_handlers()
        self.assertEqual(emmit_action('foo'), ['foo'])

    def test_removeactions(self):
        class Foo(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self)
                self.test = "foobar"
            
            @register_method('foo')
            def foo(self, state):
                return self.test
        
        foo = Foo()
        register_handler('foo', lambda x: 'foo')
        self.assertEqual(emmit_action('foo'), ['foobar', 'foo'])
        foo.remove_actions()
        self.assertEqual(emmit_action('foo'), [])
    
    def test_multiple_deco_method(self):
        class Foo(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self)
                self.test = "foobar"
            
            @register_method('bar')
            @register_method('foo')
            def foo(self, state):
                return self.test
        
        foo = Foo()
        self.assertEqual(emmit_action('foo'), ['foobar'])
        self.assertEqual(emmit_action('bar'), ['foobar'])
    
    def test_multiple(self):
        @register('foo', 'bar')
        def baz(state):
            return 'foo-bar'
        self.assertEqual(emmit_action('foo'), ['foo-bar'])
        self.assertEqual(emmit_action('bar'), ['foo-bar'])
    
    def test_multiple_deco(self):
        @register('foo')
        @register('bar')
        def baz(state):
            return 'foo-bar'
        self.assertEqual(emmit_action('foo'), ['foo-bar'])
        self.assertEqual(emmit_action('bar'), ['foo-bar'])
        
    def test_register(self):
        @register('baz')
        def baz(state):
            return 'foo'
        
        @register('foo')
        def foo_bar(state):
            return "foo bar"
        self.assertEqual(emmit_action('foo'), ['foo bar'])
        self.assertEqual(emmit_action('baz'), ['foo'])
    
    def test_nostate(self):
        def baaz():
            return 'baaz'
        
        register_nostate_handler('baz', baaz)
        self.assertEqual(emmit_action('baz'), ['baaz'])
    
    def test_context(self):
        register_handler('bar', lambda x: 'bar')
        cont = Context()
        class Bar(ActionHandler):
            def __init__(self):
                ActionHandler.__init__(self, cont)
            
            @register_method('bar')
            def baar(self, state):
                return 42
        bar = Bar()
        self.assertEqual(cont.emmit_action('bar'), [42])
        self.assertEqual(emmit_action('bar'), ['bar'])
    
    def test_stophandling(self):
        @register('spam')
        def first(state):
            return 1
        
        @register('spam')
        def second(state):
            raise StopHandling
        
        @register('spam')
        def third(state):
            return 3
        
        self.assertEqual(emmit_action('spam'), [1])
    
    def tearDown(self):
        clear()


if __name__ == '__main__':
    unittest.main()
