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

int lookup(struct Board *b, int depth){
   /* TODO: Write me! This is supposed to look up whether we already
      analyzed given position with given depth.*/
   return -1;
}

float alpha_beta(struct Board *b, int depth, float alpha, float beta){
   float v;
   struct Turn t;
   
   int w = won(b);
   if(w){
      if(w == b->colour)
         return INFINITY;
      else{
         return -INFINITY;
      }
   }
      
   int l = lookup(b, depth);
   if(l != -1)
      return l;
   
   /* Game full or max. depth reached. */
   if(depth == 0 || b->filled == 36){
      return rate(b);
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
      if(first || t->value > best->value){
         *best = *t;
         first = 0;
      }
      free(t);
   }
   return best;
}

struct Turn prompt_turn(){
   struct Turn t;
   int r, c, q, dir;
   while(1){
      printf("Row: ");
      scanf("%d", &r);
      if(r == 42){
         /* Yes. This has to be! */
         printf("Where is my towel?\n");
         continue;
      }
      printf("Col: ");
      scanf("%d", &c);
      printf("Quadrant to rotate: ");
      scanf("%d", &q);
      printf("Dir. to rotate (1 = CW|0 = CCW): ");
      scanf("%d", &dir);
      if(r >= 0 && r <= 5 && c >= 0 && c <= 5 && q >= 0 && 
         q <= 3 && dir >= 0 && dir <= 1){
         t.row = r;
         t.col = c;
         t.quad = q;
         t.dir = dir;
         /* This only matters for find_best. */
         t.value = 0;
         return t;
      }
   }
   return t;
}


int main(){
   int depth = 4;
   printf("Welcome to pypentago!\n");
   printf("Note that everything you enter is zero indexed\n");
   printf("\n\n");
   /* This is for testing only! */
   struct Board* b = new_board(WHITE);
   struct Turn* best;
   while(1){
      print_board(b);
      struct Turn tu = prompt_turn();
      do_turn(b, &tu);
      print_board(b);
      if(won(b)){
         printf("You won the game!\n");
         break;
      }
      printf("Pondering...\n");
      best = find_best(b, depth);
      do_turn(b, best);
      if(won(b)){
         print_board(b);
         printf("The AI beat you!\n");
         break;
      }
   }
   return 0;
}
