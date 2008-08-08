#!/usr/bin/env python

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

""" Setup file for pypentago. It puts all but the main modules in site-packages 
and the main scripts into /usr/bin. This script is only usable for POSIX 
compatible systems. We will supply a separate installer for Windows. """

from setuptools import setup

setup(
    name='pyPentago',
    version='0.1',
    description='Pentago board game',
    author='Florian Mayer',
    author_email='flormayer@aim.com',
    url='https://gna.org/projects/pypentago/',
    keywords='pentago game board',
    license='GPL',
    zip_safe = False,
    packages=['pypentago', 'pypentago.server', 'pypentago.server.db.', 
              'pypentago.client', 
              'pypentago.client.img', 'easy_twisted', 'pygrade'],
    package_data = {'pypentago.client.img': ['*.png']},
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


    install_requires=[
        'twisted',
        ],
)

