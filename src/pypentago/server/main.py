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

""" Main entry-point for the server. Parses command line switches in argv
and starts a server according to them. """

import sys
import logging

import os

from optparse import OptionParser
from ConfigParser import ConfigParser, NoOptionError

import pypentago
from pypentago import conf
from pypentago.server.server import run_server
from pypentago import __version__, verbosity_levels
from pypentago.server import server

def main(args=None):
    if not os.path.exists(conf.app_data):
        conf.init_appdata(conf.app_data)
    
    if args is None:
        args = sys.argv[1:]
    
    var = {'appdata': conf.app_data}
    
    config = ConfigParser()
    config.read(conf.possible_configs('server.ini'))
    
    def_port = config.getint("server", "port")
    def_logfile = config.get("server", "logfile", vars=var)
    def_verbosity = config.getint("server", "verbosity")
    def_daemon = config.getboolean("server", "daemon")
    
    parser = OptionParser(version = 'pypentago ' + __version__)
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
    
    options, args = parser.parse_args(args)
    verbosity = verbosity_levels[options.verbose]
    
    var.update({'port': options.port})
    
    pid_filename = os.path.abspath(
        config.get("server", "pidfile", vars=var)
    )
    connect_string = config.get("server", 'database', vars=var)
    logfile = config.get("server", "logfile", vars=var)
    
    pypentago.init_logging(logfile, verbosity)
    log = logging.getLogger("pypentago.server")
    
    if options.daemon:
        from pypentago import daemon
        daemon.daemonize(True, cwd='/')
        with open(pid_filename, "w") as pid_file:
            pid_file.write(str(os.getpid()))
    run_server(options.port, connect_string)


if __name__ == "__main__":
    main()
