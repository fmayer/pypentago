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

""" Main module that sets up the logging, parses the command line switches and 
starts up the interface. """

import logging
import sys
import os
import time

from optparse import OptionParser
from ConfigParser import ConfigParser, NoSectionError

import pypentago

from pypentago import conf
from pypentago.client import interface
from pypentago import __version__, verbosity_levels

def main(args=None):
    if not os.path.exists(conf.app_data):
        conf.init_appdata(conf.app_data)
    
    if args is None:
        args = sys.argv[1:]
    
    parser = OptionParser(
        usage='pypentago [options] [servers]',
        version='pypentago ' + __version__
    )
    
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
        conf.init_client_conf(conf.app_data)
        if verbosity <= 20:
            # -v or -vv
            print "Reset client configuration file."
        # We're done.
        return 0
    
    var = {'appdata': conf.app_data}
    
    config = ConfigParser()
    config.read(conf.possible_configs('client.ini'))
    
    logfile = config.get("client", "logfile", vars=var)
    
    pypentago.init_logging(logfile, verbosity)
    log = logging.getLogger("pypentago.client")
    interface.main(args)


if __name__ == "__main__":
    sys.exit(main())
