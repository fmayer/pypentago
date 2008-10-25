# easy_twisted - a framework to easily use twisted
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


import warnings


__version__ = "svn"
__author__    = "Florian Mayer <flormayer@aim.com>"
__url__       = "https://gna.org/projects/pypentago/"
__copyright__ = "(c) 2008 Florian Mayer"
__license__   = "GNU General Public License version 3"
__description__ = ("easy_twisted is a framework that helps using Twisted "
                   "easily")

def register(keyword, method=True, binds=None):
    """ Insert function decorated with this to the dictionary binds using 
    the key keyword. 
    
    Only decorate methods of the Connection class. If you decorate a function, 
    pass method=False to the decorator or it will not work as intended! """
    def decorate(f):
        if keyword in binds:
            warnings.warn('Overriding bind %s!' % keyword)
        if method:
            x = f.__name__
        else:
            x = f
        binds[keyword] = {}
        binds[keyword]['function'] = x
        binds[keyword]['args'] = []
        binds[keyword]['kwargs'] = {}
        return f
    return decorate
