#!/usr/bin/env python
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

""" Main entry-point for the server. Parses command line switches in argv
and starts a server according to them. """

from __future__ import with_statement

import sys
import logging

import os

from optparse import OptionParser
from ConfigParser import ConfigParser

import pypentago
from pypentago import conf
from pypentago import __version__, verbosity_levels
from pypentago import server

def main(args=None):
    if not os.path.exists(conf.app_data):
        conf.init_appdata(conf.app_data)
    
    if args is None:
        args = sys.argv[1:]
    
    parser = OptionParser(version='pypentago ' + __version__)
    parser.add_option("-d", "--daemon", action="store_true", 
                      dest="daemon", default=None,
                      help="start server as daemon. POSIX only!")
    
    parser.add_option("-p", "--port", action="store", default=None,
                      type="int", dest="port", metavar="PORT",
                      help="start server on port PORT")
    
    parser.add_option('--verbose', '-v', action='count', dest='verbose',
                      help="Increase verbosity. Use -vv for very verbose",
                      default=0)
    
    parser.add_option('--quiet', '-q', action='count', dest='quiet', 
                      help="Show only error messages", default=0)
    
    parser.add_option('--reset-config', action='store_true', dest='reset_conf',
                      default=False, help="Reset the config files.")
    
    options, args = parser.parse_args(args)
    verbosity = verbosity_levels[options.verbose - options.quiet]
    
    if options.reset_conf:
        conf.init_server_conf(conf.app_data)
        if verbosity <= 20:
            # -v or -vv
            print "Reset server configuration file."
        # We're done.
        return 0
    
    config = ConfigParser()
    config.read(conf.possible_configs('server.ini'))
    
    if options.port is None:
        port = config.getint("server", "port")
    else:
        port = options.port
    
    var = {'appdata': conf.app_data, 'port': port}
    
    if options.daemon is None:
        daemonize = config.getboolean("server", "daemon")
    else:
        daemonize = options.daemon
    
    pid_filename = os.path.abspath(
        config.get("server", "pidfile", vars=var)
    )
    connect_string = config.get("server", 'database', vars=var)
    logfile = config.get("server", "logfile", vars=var)
    
    pypentago.init_logging(logfile, verbosity)
    log = logging.getLogger("pypentago.server")
    
    if daemonize:
        from pypentago.server import daemon
        daemon.daemonize(True, cwd='/')
        with open(pid_filename, "w") as pid_file:
            pid_file.write(str(os.getpid()))
    try:
        server.run_server(port, connect_string)
    finally:
        if daemonize:
            os.remove(pid_filename)


if __name__ == "__main__":
    sys.exit(main())
