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

struct Board
{
   short filled;
   char board[6][6];
   char colour;
};

struct Turn
{
   short row;
   short col;
   short quad;
   char dir;
   float value;
};

void undo_turn(struct Board *b,struct Turn *t);
void do_turn(struct Board *b,struct Turn *t);
void print_board(struct Board *b);
void free_board(struct Board *b);
struct Board *copy_board(struct Board *b);
struct Board *new_board(char beginner);
void set_stone(struct Board *b,char player,int quad,int row,int col);
void rotate_ccw(struct Board *b,int quad);
void rotate_cw(struct Board *b,int quad);
char won(struct Board *b);
char won_dia(struct Board *b,unsigned char r,unsigned char c);
char won_col(struct Board *b,unsigned char c);
char won_row(struct Board *b,unsigned char r);
int quad_col(int quad);
int quad_row(int quad);
void print_turn(struct Turn *x);
