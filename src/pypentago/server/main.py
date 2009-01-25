#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

# Imports that are not dependant on PYTHONPATH being set.
import sys
import logging

from os.path import join, dirname, abspath, expanduser
from optparse import OptionParser
from ConfigParser import ConfigParser, NoOptionError

import pypentago
# Imports that need PYTHONPATH set.
from pypentago.get_conf import get_conf_obj
from pypentago.server.server import run_server
from pypentago import __version__, verbosity_levels
from pypentago.server import server


config = get_conf_obj("server")

def_port = config.get("default", "port")
def_logfile = config.get("default", "logfile")
def_verbosity = config.get("default", "verbosity")
def_daemon = config.get("default", "daemon")

parser = OptionParser(version = 'pypentago ' + __version__)
parser.add_option("-l", "--log", action="store", 
                     type="string", dest="logfile", default = def_logfile,
                     help="write logs to FILE", metavar="FILE")

parser.add_option("-d", "--daemon", action="store_true", 
                     dest="daemon", default=def_daemon,
                     help="start server as daemon. POSIX only!")

parser.add_option("-p", "--port", action="store", default = def_port,
                     type="int", dest="port", metavar="PORT",
                     help="start server on port PORT")

parser.add_option('--verbose', '-v', action='count', dest='verbose',
                  help="Increase verbosity. Use -vv for very verbose")
parser.add_option('--quiet', '-q', action='store_const', dest='verbose', 
                  const=-1, default=0, help="Show only error messages")

options, args = parser.parse_args()
verbosity = verbosity_levels[options.verbose]
    
try:
    def_pid = config.get("default", "pidfile", {"{port}": str(options.port)})
except NoOptionError:
    def_pid = abspath(join(script_path, "pid"))
pid_filename = abspath(def_pid)

db_driver = config.get('database','dbdriver')
db_host   = config.get('database','dbhost')
db_port   = str(config.get('database','dbport'))
db_user   = config.get('database','dbuser')
db_name   = config.get('database','dbname')
db_pass   = config.get('database','dbpass')
if db_driver == 'sqlite':
    # SQLite ignores anything but driver and db_name.
    # If any other databases do this add to if clause above.
    connect_string = '%s:///%s' % (db_driver, db_name)
else:
    connect_string = db_driver+"://"+db_user+":"+db_pass+"@"+\
                   db_host+":"+db_port+"/"+db_name

def main():
    logfile = expanduser(str(options.logfile))
    logfile = logfile.replace("{port}", str(options.port))
    if not logfile:
        logfile = join(script_path, "server.log")
    pypentago.init_logging(logfile, verbosity)
    log = logging.getLogger("pypentago.server")

    if options.daemon:
        import daemon
        from os import getpid
        daemon.daemonize(True, cwd='/')
        pid_file = open(pid_filename, "w")
        pid_file.write(str(getpid()))
        pid_file.close()
    run_server(options.port, connect_string)


if __name__ == "__main__":
    main()
