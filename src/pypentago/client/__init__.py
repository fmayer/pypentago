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


import actions

_avail_actions = ['registered', 'not_logged_in', 'display_player',
                  'turn_recv', 'in_game', 'email_available', 'name_available',
                  'login', 'game_over', 'gamelist', 'start', 'conn_lost', 
                  'conn_established']

context = actions.Context(_avail_actions)
