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

""" This module is used to get the path of a config file.
Please only use this module to get config files, so it will be easier to 
manage the directories in which they may be. """

from __future__ import with_statement


import os
import pypentago

from ConfigParser import RawConfigParser


def get_app_data():
    """ Get the directory where the application data, such as config files or 
    logfiles, should be stored according to the Operating System used by the 
    user. If the Operating System is unknown it defaults to ~/.pypentago """
    if 'APPDATA' in os.environ:
        # Most likely only Windows, but who knows?
        app_data = os.path.join(os.environ['APPDATA'], "pypentago")
    elif os.name == "posix":
        # POSIX Systems such as Linux, *BSD, etc.
        app_data = os.path.join("~", ".pypentago")
    elif os.name == "mac":
        # MacOS Systems.
        app_data = os.path.join(
            "~", "Library", "Application Support", "pypentago"
        )
    else:
        # If everything fails we will use the standard POSIX path.
        # It should always work as most Operating Systems know home directories.
        from warnings import warn
        warn(
            "Unsupported Operating System. Falling back to POSIX standard! "
            "Please file a bugreport containing your Operating System and the "
            "Application Path"
        )
        app_data = os.path.join("~", ".pypentago")

    return os.path.abspath(os.path.expanduser(app_data))


app_data = get_app_data()


default_locations = [
    app_data
]

if os.name == 'posix':
    default_locations.append('/etc/pypentago/')


def init_server_conf(location):
    server_file = os.path.join(location, 'server.ini')
    
    server = RawConfigParser()
    server.add_section('server')
    server.set('server', 'logfile', '%(appdata)s/server.log')
    server.set('server', 'pidfile', '%(appdata)s/pid.%(port)s')
    server.set('server', 'port', str(pypentago.DEFAULT_PORT))
    server.set('server', 'verbosity', '30')
    server.set('server', 'daemon', 'False')
    server.set('server', 'database', 'sqlite:///:memory:')
    
    with open(server_file, 'w') as server_file:
        server.write(server_file)


def init_client_conf(location):
    client_file = os.path.join(location, 'client.ini')
    
    client = RawConfigParser()
    client.add_section('client')
    client.set('client', 'logfile', '%(appdata)s/client.log')
    client.set('client', 'verbosity', '30')
    
    with open(client_file, 'w') as client_file:
        client.write(client_file)


def init_conf(location):
    init_server_conf(location)
    init_client_conf(location)


def init_appdata(appdata):
    os.mkdir(appdata)
    init_conf(appdata)


def possible_configs(file_name, locations=None):
    if locations is None:
        locations = default_locations
    for location in locations:
        name = os.path.join(location, file_name)
        if os.path.exists(name):
            yield os.path.abspath(name)

