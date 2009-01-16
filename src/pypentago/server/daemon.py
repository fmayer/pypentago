# daemon - daemonize the current process
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


import os
import sys
import errno
import resource


MAXFD = 1024
NULL_DEVICE = getattr(os, 'devnull', '/dev/null')


def _fork_exit_parent():
    """ Fork and kill parent. """
    pid = os.fork()
    if pid != 0:
        os._exit(0)


def close_tty():
    """ Close all file descriptors to TTY """
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = MAXFD

    for fd in xrange(0, maxfd):
        if os.isatty(fd):
            try:
                os.close(fd)
            except OSError, err:
                if err.errno != errno.EBADF:
                    raise


def redirect_std():
    """ Redirect stdin/stdout and stderr to /dev/null """
    null = os.open(NULL_DEVICE, os.O_RDWR)
    
    os.dup2(null, sys.stdin.fileno())
    os.dup2(null, sys.stdout.fileno())
    os.dup2(null, sys.stderr.fileno())

    os.close(null)


def daemonize(redirect=True, umask=None, cwd=None):
    """ Daemonize current process. 
    
    If redirect is True, redirect stdin/stdout and stderr to /dev/null. 
    If umask is set, set the processes umask. If cwd is set chdir to cwd. """
    if not hasattr(os, 'fork') or not hasattr(os, 'setsid'):
        raise OSError('Daemonizing unavailable on your platform.')
    _fork_exit_parent()
    os.setsid()
    _fork_exit_parent()
    if umask is not None:
        os.umask(umask)
    if cwd is not None:
        os.chdir(cwd)
    close_tty()
    if redirect:
        redirect_std()


if __name__ == '__main__':
    # Testing function.
    import time
    import tempfile
    output = tempfile.NamedTemporaryFile(mode='w', prefix="test", 
                                         dir=os.getcwdu())
    print "Output file %s" % output.name
    output.write('PID: %d\n' % os.getpid())
    output.flush()
    daemonize()
    print "You shouldn't see this!"
    print >>sys.stderr, "Nor this!"
    output.write('PID after daemonization: %d\n' % os.getpid())
    output.flush()
    for count in xrange(11):
        output.write('Counting: %d\n' % count)
        output.flush()
        time.sleep(1)
    # Sleep 10 seconds so the file doesn't get deleted too early.
    time.sleep(10)
    output.close()
