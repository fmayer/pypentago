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

""" This module allows you to mark functions as deprecated. """


import warnings
import functools
import inspect
import textwrap


def _update_docstring(take_from, depr_msg, exc):
    """ Return new docstring, take arguments and docstring from
    take_from, add depr_msg at the beginning of the docstring and
    take the name of exc """
    depr_msg = '\n'.join(textwrap.wrap(depr_msg))
    doc = ''
    old_doc = take_from.__doc__ or ''
    args = inspect.formatargspec(*inspect.getargspec(take_from))
    
    f_args = 'Actual arguments: %s%s' % (exc.__name__, args)
    f_args = '\n'.join(textwrap.wrap(f_args))
    old_doc = '\n'.join(x.strip() for x in
                        old_doc.splitlines())
    return '\n\n'.join([depr_msg, f_args, old_doc])


def deprecated_by(exc, new_name=''):
    """ Add a reference to exc in the help and raise a
    DeprecationWarning when called """
    def decorator(f):
        @functools.wraps(f)
        def deprecated(*args, **kwargs):
            """ Function to replace the one decorated with """
            d_w = "%s is deprecated, use %s instead."
            warnings.warn(d_w % (f.__name__, new_name or exc.__name__),
                          DeprecationWarning, 2)
            return f(*args, **kwargs)
        
        depr_msg = ('THIS FUNCTION IS DEPRECATED! Use %s instead.' % 
                    (new_name or exc.__name__))
        
        deprecated.__doc__ = _update_docstring(f, depr_msg, f)
        return deprecated
    
    return decorator


def deprecated_alias(exc, new_name=''):
    """ Replace functionality, add a reference to exc in the help and
    raise a DeprecationWarning when called """
    def decorator(f):
        @functools.wraps(f)
        def deprecated(*args, **kwargs):
            """ Function to replace the one decorated with """
            d_w = "%s is deprecated, use %s instead."
            warnings.warn(d_w % (f.__name__, new_name or exc.__name__),
                          DeprecationWarning, 2)
            return exc(*args, **kwargs)
        
        depr_msg = ('THIS FUNCTION WILL BE RENAMED! Use %s instead.' % 
                    (new_name or exc.__name__))

        deprecated.__doc__ = _update_docstring(exc, depr_msg, f)
        return deprecated
    
    return decorator
