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

""" Main module that sets up the logging, parses the command line switches and 
starts up the interface. """

import logging
import sys
import os
import time

from optparse import OptionParser
from ConfigParser import ConfigParser

import pypentago

from pypentago import conf
from pypentago.client import interface
from pypentago import __version__, verbosity_levels

def main(args=None):
    if not os.path.exists(conf.app_data):
        conf.init_appdata(conf.app_data)
    
    if args is None:
        args = sys.argv[1:]
    
    var = {'appdata': conf.app_data}
    
    config = ConfigParser()
    config.read(conf.possible_configs('client.ini'))

    def_logfile = config.get("client", "logfile", vars=var)
    def_verbosity = config.get("client", "verbosity")
    
    parser = OptionParser(version = 'pypentago ' + __version__)
    
    # FIXME: This doesn't work.
    parser.add_option("-s", "--server", action="store", 
                         type="string", dest="server", metavar="SERVER",
                         help="connect to SERVER", default='')
    
    # FIXME: Neither does this.
    parser.add_option("-p", "--port", action="store", 
                         type="int", dest="port", metavar="PORT",
                         help="connect at PORT", default=-1)
    
    parser.add_option('--verbose', '-v', action='count', dest='verbose',
                      help="Increase verbosity. Use -vv for very verbose")
    
    parser.add_option('--quiet', '-q', action='store_const', dest='verbose', 
                      const=-1, default=0, help="Show only error messages")
    
    options, args = parser.parse_args()
    verbosity = verbosity_levels[options.verbose]
    
    pypentago.init_logging(def_logfile, verbosity)
    log = logging.getLogger("pypentago.client")
    interface.main()

if __name__ == "__main__":
    main()
