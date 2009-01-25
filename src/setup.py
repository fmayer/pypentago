#!/usr/bin/env python

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

""" Setup file for pypentago. It puts all but the main modules in site-packages 
and the main scripts into /usr/bin. This script is only usable for POSIX 
compatible systems. We will supply a separate installer for Windows. """

import sys
import optparse

from setuptools import setup, Extension, Feature
from distutils import sysconfig

known = {
    'gcc': ['--std=c99']
}

def get_compiler():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--compiler", action="store", type='str',
                     dest="compiler", default=sysconfig.get_config_var('CC'))
    options, args = parser.parse_args()
    cc = options.compiler
    if cc == 'unix':
        cc = sysconfig.get_config_var('CC')
    return cc


def get_default_opts(c_string):
    for compiler, opts in known.iteritems():
        if c_string.startswith(compiler):
            return opts
    return []


cc = get_compiler()
enable_speedups = cc is not None
opts = get_default_opts(cc)

dep = []

# Don't bother setuptools with any dependencies that are already installed.
try:
    try:
        import json
    except ImportError:
        import simplejson
except ImportError:
    dep.append('simplejson')

try:
    import twisted
except ImportError:
    dep.append('twisted')

try:
    import sqlalchemy
except ImportError:
    dep.append('sqlalchemy')


board_speedup = Extension('pypentago._board',
              ['pypentago/_board.c', 'lib/board.c', 'lib/ai.c'],
              include_dirs=['lib'], extra_compile_args=opts)

setup(
    name='pypentago',
    version='0.1',
    description='Pentago board game',
    author='Florian Mayer',
    author_email='flormayer@aim.com',
    url='https://gna.org/projects/pypentago/',
    keywords='pentago game board',
    license='GPL',
    zip_safe=False,
    packages=['pypentago', 'pypentago.server', 'pypentago.server.db.', 
              'pypentago.client',  'easy_twisted', 
              'pypentago.client.interface'],
    py_modules=['actions', 'depr'],
    features=dict(
        speedups=Feature('optional C speed-enhancements',
            standard=enable_speedups,
            ext_modules=[board_speedup],
        )
    ),
    package_data={'pypentago': ['data/*.png', 'data/*.svg']},
    scripts=[ ],
    entry_points = {
        'console_scripts': [
            'pypentagod = pypentago.server.main:main',
            ],
        'gui_scripts': [
            'pypentago = pypentago.client.main:main',
            ],
        
        'setuptools.installation': [
            'eggsecutable = pypentago.client.main:main',
        ]
    },


    install_requires=dep,
)

