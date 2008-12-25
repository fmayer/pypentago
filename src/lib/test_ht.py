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

import subprocess
import os

def main():
    subprocess.Popen(['gcc', 'test_ht.c', '-o', 'test_ht']).wait()
    p = subprocess.Popen([], executable='./test_ht', stdout=subprocess.PIPE)
    for l in p.stdout:
        l = l.strip()
        x, y = l.split('==')
        if x != y:
            print l
    
    os.remove('./test_ht')

if __name__ == "__main__":
    main()
