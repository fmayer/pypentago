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

""" Serialize data so it can be sent through sockets. Currently this only
serializes players by sending the id, which is resolved to the object on
the other side. """


class ObjectIdentifier(object):
    def __init__(self, object_):
        self.object_ = object_
    
    def rpcialize(self, obj):
        return None
    
    def unrpcialize(self, id_):
        return self.object_       


class ObjectDispatcher(object):
    def __init__(self, objects):
        self.objects = objects
    
    def rpcialize(self, obj):
        return self.objects.index(obj)
    
    def unrpcialize(self, id_):
        return self.objects[id_]   


class Raw(object):
    @staticmethod
    def unrpcialize(obj):
        return obj


class TrivialClass(object):
    """
    >>> class Foo(TrivialClass):
    ...     def __init__(self, foo):
    ...         self.foo = foo
    ... 
    >>> foo = Foo('spam')
    >>> foo.rpcialize()
    {'foo': 'spam'}
    >>> rpc = foo.rpcialize()
    >>> new_foo = foo.unrpcialize(rpc)
    >>> new_foo # doctest: +ELLIPSIS
    <__main__.Foo object at 0x...>
    >>> new_foo.foo
    'spam'
    >>> 
    """
    rpcialize_attributes = None
    
    def rpcialize(self):
        attrs = vars(self)
        if self.rpcialize_attributes is not None:
            filtered = {}
            for attr in self.rpcialize_attributes:
                filtered[attr] = attrs[attr]
            return filtered
        else:
            return attrs
    
    @classmethod
    def unrpcialize(cls, args):
        # Avoid the __init__
        inst = object.__new__(cls)
        inst.__dict__.update(args)
        return inst


class Resolver(object):
    """
    >>> class Foo(TrivialClass):
    ...     def __init__(self, foo):
    ...         self.foo = foo
    ... 
    >>> resolver = Resolver()
    >>> resolver.register(Foo)
    >>> foo = Foo('foobar')
    >>> resolver.rpcialize(foo)
    ['Foo', {'foo': 'foobar'}]
    >>> rpc = resolver.rpcialize(foo)
    >>> resolver.resolve(rpc) # doctest: +ELLIPSIS
    <__main__.Foo object at 0x...>
    >>> new_foo = resolver.resolve(rpc)
    >>> new_foo.foo
    'foobar'
    >>> 
    """
    def __init__(self, table=None):
        if table is None:
            table = {}
        self.table = table
        self.reverse_table = dict(
            (item, key) for key, item in table.iteritems()
        )
    
    def resolve(self, arg):
        type_, args = arg
        return self.table[type_].unrpcialize(args)
    
    def register(self, cls, name=None):
        if name is None:
            name = getattr(cls, 'rpcialize_name', cls.__name__)
        if name in self.table:
            raise ValueError("name not unique in this Resolver")
        self.table[name] = cls
        self.reverse_table[cls] = name
    
    def rpcialize(self, obj, *args, **kwargs):
        if hasattr(obj, 'rpcialize'):
            return [self.reverse_table[obj.__class__],
                    obj.rpcialize(*args, **kwargs)]
        else:
            return [self.reverse_table[Raw], obj]
    
    def rpcialize_many(self, *args):
        return map(self.rpcialize, args)


class StandardResolver(Resolver):
    """ Resolver that automatically has '' mapped to Raw. """
    def __init__(self):
        Resolver.__init__(self, {'': Raw})


def player_by_id(p):
    return ['player_by_id', p]


def raw(data):
    return ['', data]


def game(game, cmd, *args):
    return ["GAME", [game.uid, cmd, args]]
