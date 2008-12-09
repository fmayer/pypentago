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


static char NONE = 0;
static char WHITE = 1;
static char BLACK = 2;

static char WIN = 100;
static char LOSE = 0;

struct Board
{
   char board[6][6];
};

/* Helper functions */

int max(int x, int y){
    if(x > y){
        return x;
    }
    else{
        return y;
    }
}

int quad_row(int quad){
   return (quad >= 2);
}

int quad_col(int quad){
    return (quad == 1 || quad == 3);
}

/* End of helper functions */

int longest_row(struct Board* b, char player){
   int len = 0;
   int longest = 0;
   char r, c;
   for(r = 0; r <= 5; r++){
      for(c = 0; c <= 5; c++){
         if(b->board[r][c] == player){
            len++;
         }
         else{
            if(len > longest){
               longest = len;
            }
            len = 0;
         }
      }
   }
   return longest;
}

int longest_col(struct Board* b, char player){
   int len = 0;
   int longest = 0;
   char r, c;
   for(c = 0; c <= 5; c++){
      for(r = 0; r <= 5; r++){
         if(b->board[r][c] == player){
            len++;
         }
         else{
            if(len > longest){
               longest = len;
            }
            len = 0;
         }
      }
   }
   return longest;
}

int dia_sum(struct Board* b, char player, char r, char c){
   int len = 0;
   int longest = 0;
   char x;
   for(x = 0; x <= (5 - (r || c)); x++){
      if(b->board[x+r][x+c] == player){
         len++;
      }
      else{
         if(len > longest){
            longest = len;
         }
         len = 0;
      }
   }
   return longest;
}

int longest_dia(struct Board* b, char player){
   int a = dia_sum(b, player, 0, 0);
   if(a == 6 || a == 5){
      return a;
   }
   int x = dia_sum(b, player, 0, 1);
   if(x == 5){
      return 5;
   }
   int c = dia_sum(b, player, 1, 0);
   if(c == 5){
      return 5;
   }
   return max(max(a, x), c);
}


int longest_line(struct Board* b, char player){
   int d = longest_dia(b, player);
   if(d == 5 || d == 6){
      return d;
   }
   int r = longest_row(b, player);
   if(r == 5){
      return 5;
   }
   int c = longest_col(b, player);
   if(c == 5){
      return 5;
   }
   return max(max(r, c), d);
}

int rate(struct Board* b, char player){
    int own_line = longest_line(b, player);
    if(own_line >= 5){
        return WIN;
    }
    int other_line = longest_line(b, 3 - player);
    if(other_line >= 5){
        return LOSE;
    }
    return own_line - other_line;
}


void rotate_cw(struct Board* b, int quad){
   int row = 3 * quad_row(quad);
   int col = 3 * quad_col(quad);
   char q[3][3];
   char r, c;
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
   char r, c;
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

void set_stone(struct Board* b, char player, int quad, int row, int col){
   int r = 3 * quad_row(quad);
   int c = 3 * quad_col(quad);
   b->board[r+row][c+col] = player;
}


struct Board* new_board(){
   /* The field is empty in the beginning. */
   struct Board* b;
   b = (struct Board*)calloc(1, sizeof(struct Board));
   memset(b->board, NONE, 6 * 6 * sizeof(char));
   return b;
}

struct Board* copy_board(struct Board* b){
    struct Board* nb;
    nb = (struct Board*)calloc(1, sizeof(struct Board));
    int i;
    for(i=0; i < sizeof(struct Board); i++){
        nb[i] = b[i];
    }
    return nb;
}

void free_board(struct Board* b){
    free(b);
}

void print_board(struct Board* b){
    char r, c;
    int x;
    for(r = 0; r <= 5; r++){
       for(c = 0; c <= 5; c++){
           x = b->board[r][c];
           printf("%d ", x);
          if(c == 2)
             printf(" ");
       }
       printf("\n");
       if(r == 2)
           printf("\n");
    }
 }

int main(){
   /* This is for testing only! */
   struct Board* b;
   b = new_board();
   set_stone(b, WHITE, 1, 0, 0);
   set_stone(b, BLACK, 2, 0, 0);
   rotate_cw(b, 1);
   set_stone(b, WHITE, 0, 0, 0);
   set_stone(b, WHITE, 0, 1, 1);
   set_stone(b, WHITE, 0, 2, 2);
   set_stone(b, WHITE, 3, 0, 0);
   set_stone(b, WHITE, 0, 0, 1);
   set_stone(b, WHITE, 0, 0, 2);
   longest_line(b, WHITE);
   rotate_cw(b, 3);
   print_board(b);

   set_stone(b, WHITE, 0, 2, 1);
   set_stone(b, WHITE, 1, 0, 0);
   set_stone(b, BLACK, 1, 1, 2);
   set_stone(b, BLACK, 2, 1, 1);
   set_stone(b, WHITE, 3, 2, 2);
   int i;
   for(i = 0; i < 10000000; i++){
      rotate_cw(b, 0);
      rotate_ccw(b, 0);
   }
   return 0;
}
