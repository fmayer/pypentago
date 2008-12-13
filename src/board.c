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

#define CW 1
#define CCW 0

#ifndef INFINITY
#warning "No INFINITY. Try compiling in C99 mode. Assuming INFINITY = big!"
/* That should be enough. I want it to compile on C89 */
#define INFINITY 2147483647
#endif


static char NONE = 0;
static char WHITE = 1;
static char BLACK = 2;


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

/* Helper functions */


void print_turn(struct Turn* x){
   printf("r: %d; c: %d; q: %d; r: %d\n", x->row, x->col, x->quad, x->dir);
}

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
   unsigned char r, c;
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
   if(len > longest)
      return len;
   return longest;
}

int longest_col(struct Board* b, char player){
   int len = 0;
   int longest = 0;
   unsigned char r, c;
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
   if(len > longest)
      return len;
   return longest;
}

int dia_sum(struct Board* b, char player, char r, char c){
   int len = 0;
   int longest = 0;
   unsigned char x;
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
   if(len > longest)
      return len;
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

float rate(struct Board* b){
   /* TODO: This needs a lot of love! */
   int own_line = longest_line(b, b->colour);
   if(own_line >= 5){
      return INFINITY;
   }
   int other_line = longest_line(b, 3 - b->colour);
   if(other_line >= 5){
      return -INFINITY;
   }
   return own_line - other_line;
}

char won(struct Board* b){
   char imp_set = 0;
   char winner = 0;
   char break_ = 0;
   char check = 1;
   unsigned char r, c;
   for(check=1; check <= 2; check++){
      if(winner || imp_set)
         break;
      for(r=0; r < 6; r++){
         if(break_)
            break;
         for(c=1; r < 5; c++){
            if(b->board[r][c] != check){
               winner = 0;
               break_ = 1;
               break;
            }
            else{
               imp_set = 1;
               winner = check;
            }
         }
      }
      if(!(winner && (b->board[r][0] == check || b->board[r][5])))
         winner = 0;
   }
   return winner;
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

void set_stone(struct Board* b, char player, int quad, int row, int col){
   int r = 3 * quad_row(quad);
   int c = 3 * quad_col(quad);
   b->filled++;
   b->board[r+row][c+col] = player;
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
   struct Board* nb;
   nb = (struct Board*) malloc(sizeof(struct Board));
   unsigned int i;
   for(i=0; i < sizeof(struct Board); i++){
      nb[i] = b[i];
   }
   return nb;
}

void free_board(struct Board* b){
   free(b);
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

int rate_with_turn(struct Board* b, struct Turn* t, char player){
   /* This may or may not be useful. */
   do_turn(b, t);
   int r = rate(b);
   undo_turn(b, t);
   return r;
}

int lookup(struct Board *b, int depth){
   /* TODO: Write me! This is supposed to look up whether we already
      analyzed given position with given depth.*/
   return -1;
}

float alpha_beta(struct Board *b, int depth, float alpha, float beta){
   float v;
   float ra;
   struct Turn t;
   
   ra = rate(b);
   
   /* Game is over. */
   if(ra == INFINITY || ra == -INFINITY){
      return ra;
   }
   
   int l = lookup(b, depth);
   if(l != -1)
      return l;
   
   /* Game full or max. depth reached. */
   if(depth == 0 || b->filled == 36){
      return ra;
   }

   unsigned char q, r, c, cw;
   for(r=0; r <= 5; r++){
      for(c=0; c <= 5; c++){
         if(b->board[r][c] != NONE){
            continue;
         }
         for(q=0; q <= 3; q++){
            for(cw=0; cw <= 1; cw++){
               t.row = r;
               t.col = c;
               t.quad = q;
               t.dir = cw;
               do_turn(b, &t);
               v = -alpha_beta(b, depth-1, -beta, -alpha);
               undo_turn(b, &t);
               if(v > alpha)
                  alpha = v;
               if(beta <= alpha)
                  return alpha;
            }
         }
      }
   }
   return alpha;
}

struct Turn* best_turn(struct Board *b, int depth){
   struct Turn* best = (struct Turn*) malloc(sizeof(struct Turn));
   /* best = NULL; */
   float v;
   struct Turn t;
   
   float alpha = -INFINITY;
   float beta = INFINITY;
   
   unsigned char q, r, c, cw;
   for(r=0; r <= 5; r++){
      for(c=0; c <= 5; c++){
         if(b->board[r][c] != NONE){
            continue;
         }
         for(q=0; q <= 3; q++){
            for(cw=0; cw <= 1; cw++){
               t.row = r;
               t.col = c;
               t.quad = q;
               t.dir = cw;
               do_turn(b, &t);
               v = -alpha_beta(b, depth-1, -beta, -alpha);
               undo_turn(b, &t);
               if(v > alpha){
                  t.value = v;
                  alpha = v;
                  *best = t;
               }
               if(beta <= alpha){
                  return best;
               }
            }
         }
      }
   }
   return best;
}

struct Turn* find_best(struct Board* b, int max_depth){
   int d;
   char first=1;
   struct Turn* best = (struct Turn*) malloc(sizeof(struct Turn));
   struct Turn* t;
   for(d=1; d <= max_depth; d++){
      t = best_turn(b, d);
      if(first){
         *best = *t;
         first = 0;
      }
      else if(t->value > best->value){
         *best = *t;
      }
      free(t);
   }
   return best;
}


int main(){
   /* This is for testing only! */
   struct Board* b = new_board(WHITE);
   set_stone(b, WHITE, 0, 0, 0);
   set_stone(b, WHITE, 0, 1, 0);
   set_stone(b, WHITE, 0, 2, 0);
   set_stone(b, WHITE, 1, 0, 1);
   
   b->colour = WHITE;
   
   print_board(b);

   /*printf("- Thinking -\n");*/
   struct Turn* best = find_best(b, 3);/*, -INFINITY, INFINITY); */
   do_turn(b, best);
   print_board(b);
   return 0;
}