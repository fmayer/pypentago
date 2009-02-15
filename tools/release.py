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

from __future__ import with_statement

import tarfile
import bz2
import gzip
import sys
import os
import re

from contextlib import closing
from StringIO import StringIO
from mercurial.dispatch import dispatch

BUFFER = 4096
s_path = os.path.abspath(os.path.dirname(__file__))
release_dir = os.path.join(s_path, os.pardir, 'release/')
pype_path = os.path.join(s_path, os.pardir, 'src/')
version_regex = re.compile("\nVERSION = (.+?)\n", re.MULTILINE)


def buffered_write(dest, src, buffer_size):
    read = src.read(buffer_size)
    while read:
        dest.write(read)
        read = src.read(buffer_size)


def create_files(version, output):
    tar_io = StringIO()
    
    pype_version = 'pypentago-%s' % version

    tar = tarfile.TarFile(mode='w', fileobj=tar_io)
    tar.add(pype_path, pype_version)
    tar.close()
    
    for out_file in output:
        tar_io.seek(0)
        with closing(out_file) as bz:
            buffered_write(bz, tar_io, BUFFER)

def update_setup(version):
    s = os.path.join(pype_path, 'setup.py')
    with open(s) as setup:
        read = setup.read()
    new = version_regex.sub('\nVERSION = %r\n' % version, read)
    with open(s, 'w') as setup:
        setup.write(new)


def hg_commit(msg):
    dispatch(['commit', '-m', msg])


def hg_tag(name, local=True):
    cmd = ['tag']
    if local:
        cmd.append('-l')
    cmd.append(name)
    dispatch(cmd)


def release(version):
    update_setup(version)
    hg_tag(version)
    hg_commit('Release version %s' % version)
    pype_version = 'pypentago-%s' % version

    if not os.path.exists(release_dir):
        os.mkdir(release_dir)

    release_file = os.path.join(release_dir, pype_version)
    files = [bz2.BZ2File(release_file + '.tar.bz2', 'w'),
             gzip.GzipFile(release_file + '.tar.gz', 'w')]
    create_files(version, files)


def main():
    release(sys.argv[1])
    return 0


if __name__ == '__main__':
    sys.exit(main())
