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

import logging
def except_hook(exctype, value, tceback):
    log = logging.getLogger("pypentago.exception")
    from traceback import format_exception
    # For debugging for exceptions thrown before log file generation:
    # asd
    log.critical("Caught exception:\n"+''.join(format_exception(
        exctype, value, tceback)))
def set_except_hook():
    import sys
    sys.excepthook = except_hook
