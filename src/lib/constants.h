/* pypentago - a board game
Copyright (C) 2008 Florian Mayer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. */

#ifndef INFINITY
#ifdef __GNUC__
#warning "No INFINITY. Try compiling in C99 mode. Assuming INFINITY = big!"
#endif
/* That should be enough. I want it to compile on C89 */
static float INFINITY = 2147483647.0;
#endif

#ifndef max
/* Visual Studio already has this defined */
#define max(a,b)    (((a) > (b)) ? (a) : (b))
#endif

static char NONE = 0;
static char WHITE = 1;
static char BLACK = 2;

static char CW = 1;
static char CCW = 0;
