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

""" Return timezone information """

import time

def get_timezone():
    """ Return the time current deviation from UTC in hours.
    Takes DST into account """
    if time.daylight:
        timezone_seconds = time.altzone
    else:
        timezone_seconds = time.timezone
    timezone_hours = timezone_seconds / (60*60)
    # Fix Python's weird behavoir of returning a negative number 
    # although the time deviation is positive
    return -timezone_hours


def get_timezone_nodst():
    """ Return the time current deviation from UTC in hours.
    Does not take DST into account """
    timezone_seconds = time.timezone
    timezone_hours = timezone_seconds / (60*60)
    # Fix Python's weird behavoir of returning a negative number 
    # although the time deviation is positive
    return -timezone_hours

def format_timezone(timezone_hours, utc="UTC"):
    """ Format time deviation in the form UTC+3 or UTC-3 """
    if timezone_hours == 0:
        return utc
    else:
        return "%s%+g" % (utc, timezone_hours)
                            

def get_timezone_nodst_string(utc="UTC"):
    """ Get the string for the current timezone. For instance 
    UTC+1. Does not take DST into account """
    return format_timezone(get_timezone())


def get_timezone_string(utc="UTC"):
    """ Get the string for the current timezone. For instance 
    UTC+1. Takes DST into account """
    return format_timezone(get_timezone_nodst())


if __name__ == "__main__":
    print "You are in timezone %s" % get_timezone_nodst_string()