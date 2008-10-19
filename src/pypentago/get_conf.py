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

""" This module is used to get the path of a config file.
Please only use this module to get config files, so it will be easier to 
manage the directories in which they may be. """

from __future__ import with_statement


from os.path import join, dirname, abspath, expanduser, exists
from os import environ, mkdir
from os import name as os_name

from functools import partial

from ConfigParser import ConfigParser

from pypentago import could_int


default_server_conf = \
"""[default]
port = 26500
verbosity = 30
logfile = {appdata}/server.log
daemon = False
pidfile = {appdata}/pid.{port}

[database]
dbdriver = sqlite
dbuser = 
dbpass = 
dbhost = 
dbport = 
dbname = {appdata}/database

[smtp]
host = 
port =
user =
password =
"""

default_client_conf = \
"""[default]
server = pypentago.servegame.com
port = 26500
verbosity = 30
logfile = {appdata}/client.log
"""

class ConfParser(ConfigParser, object):
    """ Extended ConfigParser class that automatically replaces occurences in 
    configurations. These are defined as a dictionary in self.replace. All 
    values defined in self.expand will be expanded with the user, e.g. 
    ~/.pypentago -> /home/name/.pypentago for my user. This class automatically 
    replaces any occurences of {appdata}, {clientpath} and {serverpath} with 
    the values. Note that it does NOT replace {port} as it does not know the 
    value of that when it is created. See pypentago.client.main or 
    pypentago.server.main"""
    def __init__(self, app_data, script_path):
        ConfigParser.__init__(self)
        self.replace = \
            {"{appdata}": app_data,
             "{clientpath}": join(script_path, "client"),
             "{serverpath}": join(script_path, "server"),
             }
        self.expand = (("default", "logfile"), ("default", "pidfile"))
    
    def get(self, section, option, replace={}):
        ret = super(ConfParser, self).get(section, option)

        for key, value in self.replace.items() + replace.items():
            ret = ret.replace(key, value)
        if (section, option) in self.expand:
            ret = abspath(expanduser(ret))
        if could_int(ret):
            ret = int(ret)
        try:
            ret = str_to_bool(ret)
        except AttributeError:
            pass
        return ret
    
    def __getitem__(self, item):
        class Item:
            def __init__(self, partial):
                self.partial = partial
            def __getitem__(self, item):
                return self.partial(item)
        return Item(partial(self.get, item))


def get_app_data():
    """ Get the directory where the application data, such as config files or 
    logfiles, should be stored according to the Operating System used by the 
    user. If the Operating System is unknown it defaults to ~/.pypentago """
    if 'APPDATA' in environ:
        # Most likely only Windows, but who knows?
        app_data = join(environ['APPDATA'], "pypentago")
    elif os_name == "posix":
        # POSIX Systems such as Linux, *BSD, etc.
        app_data = join("~", ".pypentago")
    elif os_name == "mac":
        # MacOS Systems.
        app_data = join("~", "Library", "Application Support", "pypentago")
    else:
        # If everything fails we will use the standard POSIX path.
        # It should always work as most Operating Systems know home directories.
        from warnings import warn
        warn("Unsupported Operating System. Falling back to POSIX standard! "
        "Please file a bugreport containing your Operating System and the "
        "Application Path")
        app_data = join("~", ".pypentago")

    return abspath(expanduser(app_data))


app_data = get_app_data()


def create_app_data(app_data):
    """ Create application data folder if it does not exist and fill it with 
    default config files. This is ~/.pypentago with POSIX systems. """
    mkdir(app_data)
    with open(join(app_data, "server.ini"), 'w') as open_file:
        open_file.write(default_server_conf)
    with open(join(app_data, "client.ini"), 'w') as open_file:
        open_file.write(default_server_conf)

if not exists(app_data):
    create_app_data()


script_path = dirname(__file__)
# Scan the following directories in order
locations = [app_data,
             join(script_path, "client"),
             join(script_path, "server"),
             join(script_path, "server", "db")]
endings = [".ini", ".cfg"]


def get_conf(*file_names):
    """
    This function will return the full path of the first config file passed 
    that exist, in order. If you pass 'client.ini' and 'dbconf.ini' and 
    both exist, the path of 'client.ini' will be returned.
    You may also pass the searched config file without ending, if it ends with 
    the standard endings defined in endings.
    Raises IOError when the file can not be found.
    """
    for file_name in file_names:
        for location in locations:
            conf_file = join(abspath(location), file_name)
            if exists(conf_file):
                return conf_file
            else:
                for ending in endings:
                    other_file = conf_file+ending
                    if exists(other_file):
                        return other_file
    raise IOError("No config file %s found" % file_name)


def get_conf_obj(*file_names):
    """ Returns ConfParser object for config file. Only this function should be 
    used to get ConfParser objects! """
    file_name = get_conf(*file_names)
    conf = ConfParser(app_data, script_path)
    conf.read(file_name)
    return conf


def str_to_bool(x):
    ''' Convert string to bool. If the string is "True" return True, if "False" 
    return False, else raise AttributeError. '''
    if x.lower() == "true":
        return True
    elif x.lower() == "false":
        return False
    else:
        raise AttributeError("Invalid attribute. Has to be False or True. Got "
                             "%s" % x)

