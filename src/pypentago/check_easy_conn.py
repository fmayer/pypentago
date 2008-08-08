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

import sys
from os.path import dirname, abspath, join
script_path = abspath(dirname(__file__))
sys.path.append(join(script_path, ".."))

import easy_twisted
from hashlib import sha1
from os.path import dirname, abspath
from os import listdir

results = []
easy_twisted_dir = abspath(dirname(easy_twisted.__file__))
files = listdir(easy_twisted_dir)
for file_name in files:
    if file_name.endswith(".py"):
        results.append((file_name, sha1(file_name).hexdigest()))
    
print "Found easy_twisted in %s" % easy_twisted_dir
for file_name, sha in results:
    print "%s: %s" % (file_name, sha)