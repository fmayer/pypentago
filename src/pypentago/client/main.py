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

""" Main module that sets up the logging, parses the command line switches and 
starts up the interface. """

from optparse import OptionParser
from ConfigParser import ConfigParser
from os.path import join, dirname, expanduser, abspath, exists
import logging
import sys

# Sets the PYTHONPATH if this file is not on its own, meaning that the rest is 
# in site-packages.
script_path = abspath(dirname(__file__))
if exists(join(script_path, "connection.py")):
    sys.path.append(abspath(join(script_path, "..", "..")))

# Imports that need PYTHONPATH set.
# Commented out code was to check which module initalised the reactor and may 
#   be used for similar purpose later.
##print "Importing check_modules"
from pypentago.client.check_modules import check_modules
##print "Importing except_hook"
from pypentago.except_hook import set_except_hook
##print "Importing time_zones"
from pypentago.time_zones import get_timezone
##print "Importing get_conf"
from pypentago.get_conf import get_conf_obj, str_to_bool
##print "Importing client"
from pypentago.client import interface
##print "Importing time_zones"
from pypentago.time_zones import get_timezone
##print "Importing pypentago"
from pypentago import __version__, verbosity_levels
##print "Imported pypentago"

config = get_conf_obj("client")

def_logfile = config.get("default", "logfile")
def_verbosity = config.get("default", "verbosity")
def_port = config.get("default", "port")
def_server = config.get("default", "server")

parser = OptionParser(version = 'pypentago ' + __version__)

parser.add_option("-l", "--log", action="store", 
                     type="string", dest="logfile", default = def_logfile,
                     help="write logs to FILE", metavar="FILE")

parser.add_option("-s", "--server", action="store", 
                     type="string", dest="server", metavar="SERVER",
                     help="connect to SERVER", default=def_server)

parser.add_option("-p", "--port", action="store", 
                     type="int", dest="port", metavar="PORT",
                     help="connect at PORT", default=def_port)

parser.add_option('--verbose', '-v', action='count', dest='verbose',
                  help="Increase verbosity. Use -vv for very verbose")
parser.add_option('--quiet', '-q', action='store_const', dest='verbose', 
                  const=-1, default=0, help="Show only error messages")

options, args = parser.parse_args()
verbosity = verbosity_levels[options.verbose]
    
def main():
    logfile = options.logfile
    if not logfile:
        logfile = join(script_path, "client.log")
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        filename=logfile)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(verbosity)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    log = logging.getLogger("pypentago.client")
    log.info("Current deviation from UTC is %dh" % get_timezone())
    interface.main(options.server, options.port)

if __name__ == "__main__":
    main()