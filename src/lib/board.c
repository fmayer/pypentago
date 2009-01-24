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

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "constants.h"
#include "board.h"

/* Helper functions */


void print_turn(struct Turn* x){
   printf("r: %d; c: %d; q: %d; r: %d\n", x->row, x->col, x->quad, x->dir);
}

int quad_row(int quad){
   return (quad >= 2);
}

int quad_col(int quad){
   return (quad == 1 || quad == 3);
}

void set_colour(struct Board* b, char v){
   b->colour = v;
}

int get_colour(struct Board* b){
   return b->colour;
}

unsigned char get(struct Board* b, unsigned char row, unsigned char col){
   return b->board[row][col];
}

void set(struct Board* b, unsigned char row, unsigned char col,
         unsigned char v){
   b->filled++;
   b->board[row][col] = v;
}

void set_value(struct Board* b, unsigned char quad, 
               unsigned char row, unsigned char col, unsigned char v){
   int r = 3 * quad_row(quad);
   int c = 3 * quad_col(quad);
   b->filled++;
   b->board[r+row][c+col] = v;
}

/* End of helper functions */

char won_row(struct Board* b, unsigned char r){
   unsigned char c, check, winner, imp_set;
   winner = imp_set = 0;
   for(check=1; check <= 2; check++){
      if(imp_set)
         break;
      for(c=1; c < 5; c++){
         if(b->board[r][c] != check){
            winner = 0;
            break;
         }
         else{
            imp_set = 1;
            winner = check;
         }
      }
      if(winner && b->board[r][0] != check && b->board[r][5] != check)
         return 0;
   }
   return winner;
}

char won_col(struct Board* b, unsigned char c){
   unsigned char r, check, winner, imp_set;
   winner = imp_set = 0;
   for(check=1; check <= 2; check++){
      if(imp_set)
         break;
      for(r=1; r < 5; r++){
         if(b->board[r][c] != check){
            winner = 0;
            break;
         }
         else{
            imp_set = 1;
            winner = check;
         }
      }
      if(winner && b->board[0][c] != check && b->board[5][c] != check)
         return 0;
   }
   return winner;
}

char won_dia(struct Board* b, unsigned char r, unsigned char c){
   unsigned char x, check, winner, imp_set;
   winner = imp_set = 0;
   for(check=1; check <= 2; check++){
      if(imp_set)
         break;
      if(!r && !c)
         r = c = 1;
      for(x=0; x <= (5 - (r && c)); x++){
         if(b->board[x+r][x+c] != check){
            winner = 0;
            break;
         }
         else{
            imp_set = 1;
            winner = check;
         }
      }
      if(r && c && b->board[0][0] != check && b->board[5][5] != check)
         return 0;
   }
   return winner;
}

char won(struct Board* b){
   unsigned char r, w;
   for(r=0; r < 6; r++){
      w = won_row(b, r);
      if(w != 0)
         return w;
      w = won_col(b, r);
      if(w != 0)
         return w;
   }
   w = won_dia(b, 0, 0);
   if(w != 0)
      return w;
   w = won_dia(b, 0, 1);
   if(w != 0)
      return w;
   w = won_dia(b, 1, 0);
   if(w != 0)
      return w;
   return 0;
}

void rotate_cw(struct Board* b, int quad){
   int row = 3 * quad_row(quad);
   int col = 3 * quad_col(quad);
   char q[3][3];
   unsigned char r, c;
   for(r = 0; r <= 2; r++){
      for(c = 0; c <= 2; c++){
         q[r][c] = b->board[row+r][col+c];
      }
   }

   for(r = 0; r <= 2; r++){
      for(c = 0; c <= 2; c++){
         b->board[row+c][col+2-r] = q[r][c];
      }
   }
}

void rotate_ccw(struct Board* b, int quad){
   int row = 3 * quad_row(quad);
   int col = 3 * quad_col(quad);
   char q[3][3];
   unsigned char r, c;
   for(r = 0; r <= 2; r++){
      for(c = 0; c <= 2; c++){
         q[r][c] = b->board[row+r][col+c];
      }
   }

   for(r = 0; r <= 2; r++){
      for(c = 0; c <= 2; c++){
         b->board[row+c][col+2-r] = q[2-r][2-c];
      }
   }
}

void set_stone(struct Board* b, unsigned char quad, 
               unsigned char row, unsigned char col){
   int r = 3 * quad_row(quad);
   int c = 3 * quad_col(quad);
   b->filled++;
   b->board[r+row][c+col] = b->colour;
   b->colour = 3 - b->colour;
}

char get_stone(struct Board* b, unsigned char quad, unsigned char row,
               unsigned char col){
   int r = 3 * quad_row(quad);
   int c = 3 * quad_col(quad);
   return b->board[r+row][c+col];
}


struct Board* new_board(char beginner){
   struct Board* b;
   b = (struct Board*) malloc(sizeof(struct Board));
   int i, k;
   /* The field is empty in the beginning. */
   for(i=0; i < 6; i++)
      for(k=0; k < 6; k++)
         b->board[i][k] = NONE;
   b->filled = 0;
   b->colour = beginner;
   return b;
}

struct Board* copy_board(struct Board* b){
   struct Board* nb = (struct Board*) malloc(sizeof(struct Board));
   memcpy(nb, b, sizeof(struct Board));
   return nb;
}

void free_board(struct Board* b){
   free(b);
}

void free_turn(struct Turn* t){
   free(t);
}

void print_board(struct Board* b){
   /* Mainly useful for debugging. */
   unsigned char r, c;
   for(r = 0; r <= 5; r++){
      for(c = 0; c <= 5; c++){
         printf("%d ", b->board[r][c]);
         if(c == 2)
            printf(" ");
      }
      printf("\n");
      if(r == 2)
         printf("\n");
   }
}

void do_turn(struct Board* b, struct Turn* t){
   /* Keep game-piece counter up-to-date */
   b->filled++;
   b->board[t->row][t->col] = b->colour;
   if(t->dir == CW){
      rotate_cw(b, t->quad);
   }
   else{
      rotate_ccw(b, t->quad);
   }
   /* Swap active player: 3 - 2 = 1; 3 - 1 = 2 */
   b->colour = 3 - (b->colour);
}

void undo_turn(struct Board* b, struct Turn* t){
   /* Keep game-piece counter up-to-date */
   b->filled--;
   b->colour = 3 - (b->colour);
   if(t->dir == CW){
      rotate_ccw(b, t->quad);
   }
   else{
      rotate_cw(b, t->quad);
   }
   b->board[t->row][t->col] = NONE;
}
