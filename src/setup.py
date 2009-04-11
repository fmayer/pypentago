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
and the main scripts into /usr/bin. """

import sys
import imp
import optparse

from setuptools import setup, Extension, Distribution, Feature
from distutils import sysconfig

VERSION = '0.1.0'

known = {
    'gcc': ['--std=c99']
}

def depends(deps):
    dependencies = []
    for dep in deps:
        try:
            imp.find_module(dep)
        except ImportError:
            dependencies.append(dep)
    return dependencies


def parse_compiler(argv):
    for i, opt in enumerate(argv):
        if opt == '-c' or opt == '--compiler':
            return sys.argv[i + 1]
        elif opt.startswith('--compiler='):
            return opt[len('--compiler='):]
    return None


def get_compiler():
    cc = parse_compiler(sys.argv[1:])
    if cc == 'unix' or cc is None:
        cc = sysconfig.get_config_var('CC')
    return cc


def get_default_opts(c_string):
    if c_string is None:
        return []
    for compiler, opts in known.iteritems():
        if c_string.startswith(compiler):
            return opts
    return []


cc = get_compiler()
# enable_speedups = cc is not None
#: Until the AI is done, disable speedups by default.
enable_speedups = False
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

dep.extend(depends(['twisted']))


board_speedup = Extension('pypentago._board',
              ['pypentago/_board.c', 'lib/board.c', 'lib/ai.c'],
              include_dirs=['lib'], extra_compile_args=opts)


class FixedDistribution(Distribution):
    def _include_misc(self, name, value):
        if name == 'entry_points':
            old = getattr(self, name)
            for (group, entries) in value.iteritems():
                self.entry_points.setdefault(group, list()).extend(entries)
        else:
            Distribution._include_misc(self, name, value)

    def _exclude_misc(self, name, value):
        if name == 'entry_points':
            old = getattr(self, name)
            for (group, entries) in value.iteritems():
                old_entries = set(self.entry_points.get(group, list()))
                self.entry_points[group] = list(old_entries - set(entries))
        else:
            Distribution._exclude_misc(self, name, value)


setup(
    distclass=FixedDistribution,
    name='pypentago',
    version=VERSION,
    description='Pentago board game',
    author='Florian Mayer et al.',
    author_email='flormayer@aim.com',
    url='http://bitbucket.org/segfaulthunter/pypentago-mainline',
    keywords='pentago game board',
    license='GPL',
    zip_safe=False,
    packages=['pypentago', 'easy_twisted'],
    py_modules=['actions', 'depr'],
    features=dict(
        client=Feature('GUI client',
            standard=True,
            entry_points={
                'gui_scripts': [
                    'pypentago = pypentago.client.main:main'
                ],
                'setuptools.installation': [
                    'eggsecutable = pypentago.client.main:main'
                ]
            },
            packages=['pypentago.client', 'pypentago.client.interface'],
            install_requires=depends(['PyQt4'])
        ),
        server=Feature('network server',
            standard=True,
            entry_points={
                'console_scripts': [
                    'pypentagod = pypentago.server.main:main'
                ],
            },
            packages=['pypentago.server', 'pypentago.server.db'],
            install_requires=depends(['sqlalchemy'])
        ),
        speedups=Feature('optional C speed-enhancements',
            standard=enable_speedups,
            ext_modules=[board_speedup],
        )
    ),
    package_data={'pypentago': ['data/*.png', 'data/*.svg']},
    scripts=[ ],
    entry_points=dict(),
    install_requires=dep,
)

