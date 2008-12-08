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

#include <string.h> // For memset
#include <iostream>
#include <vector>

#define NONE char(0)
#define WHITE char(1)
#define BLACK char(2)

#define WIN 100
#define LOSE 0

using namespace std;

// Put into board.h later.
class Board
{
  public:
   Board();
   // The array is [row][col]!
   char board[6][6];
   void rotate_cw(int quad);
   void rotate_ccw(int quad);
   void set_stone(char player, int quad, int row, int col);
   int longest_row(char player);
   int longest_col(char player);
   int longest_dia(char player);
   int longest_line(char player);
   int rate(char player);
   void print_board();
   // These may be made private later:
   int quad_row(int quad);
   int quad_col(int quad);
  private:
   int dia_sum(char player, char r, char c);
};

int Board::rate(char player){
    // TODO: Write this properly.
    int own_line = longest_line(player);
    if(own_line >= 5){
        return WIN;
    }
    int other_line = longest_line(3 - player);
    if(other_line >= 5){
        return LOSE;
    }
    return own_line - other_line;
}

int Board::longest_line(char player){
   int d = longest_dia(player);
   if(d == 5 || d == 6){
      return d;
   }
   int r = longest_row(player);
   if(r == 5){
      return 5;
   }
   int c = longest_col(player);
   if(c == 5){
      return 5;
   }
   return max(max(r, c), d);
}

int Board::longest_dia(char player){
   int a = dia_sum(player, 0, 0);
   if(a == 6 || a == 5){
      return a;
   }
   int b = dia_sum(player, 0, 1);
   if(b == 5){
      return 5;
   }
   int c = dia_sum(player, 1, 0);
   if(b == 5){
      return 5;
   }
   return max(max(a, b), c);
}

int Board::dia_sum(char player, char r, char c){
   int len = 0;
   int longest = 0;
   for(char x = 0; x <= (5 - (r || c)); x++){
      if(board[x+r][x+c] == player){
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

int Board::longest_row(char player){
   int len = 0;
   int longest = 0;
   for(char r = 0; r <= 5; r++){
      for(char c = 0; c <= 5; c++){
         if(board[r][c] == player){
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

int Board::longest_col(char player){
   int len = 0;
   int longest = 0;
   for(char c = 0; c <= 5; c++){
      for(char r = 0; r <= 5; r++){
         if(board[r][c] == player){
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

void Board::print_board(){
   for(char r = 0; r <= 5; r++){
      for(char c = 0; c <= 5; c++){
         cout << int(board[r][c]) << " ";
         if(c == 2)
            cout << " ";
      }
      cout << endl;
      if(r == 2)
         cout << endl;
   }
}

int Board::quad_row(int quad){
   return quad >= 2 && 1;
}

int Board::quad_col(int quad){
   return (quad == 1 || quad == 3) && 1;
}

Board::Board(){
   // The field is empty in the beginning.
   memset(board, NONE, 6 * 6 * sizeof(char));
}

void Board::rotate_cw(int quad){
   // 2 - i
   int row = 3 * quad_row(quad);
   int col = 3 * quad_col(quad);
   char q[3][3];
   for(char r = 0; r <= 2; r++){
      for(char c = 0; c <= 2; c++){
         q[r][c] = board[row+r][col+c];
      }
   }

   for(char r = 0; r <= 2; r++){
      for(char c = 0; c <= 2; c++){
         board[row+c][col+2-r] = q[r][c];
      }
   }
}

void Board::rotate_ccw(int quad){
   // 2 - i
   int row = 3 * quad_row(quad);
   int col = 3 * quad_col(quad);
   char q[3][3];
   for(char r = 0; r <= 2; r++){
      for(char c = 0; c <= 2; c++){
         q[r][c] = board[row+r][col+c];
      }
   }

   for(char r = 0; r <= 2; r++){
      for(char c = 0; c <= 2; c++){
         board[row+c][col+2-r] = q[2-r][2-c];
      }
   }
}

void Board::set_stone(char player, int quad, int row, int col){
   int r = 3 * quad_row(quad);
   int c = 3 * quad_col(quad);
   board[r+row][c+col] = player;
}


int main(){
   // Testing purposes.
   Board b;
   //cout << b.quad_row(0) << endl;
   //cout << b.quad_row(1) << endl;
   //cout << b.quad_row(2) << endl;
   //cout << b.quad_row(3) << endl;
   //cout << endl;
   //cout << b.quad_col(0) << endl;
   //cout << b.quad_col(1) << endl;
   //cout << b.quad_col(2) << endl;
   //cout << b.quad_col(3) << endl;
   //cout << endl;
   b.set_stone(WHITE, 1, 0, 0);
   b.set_stone(BLACK, 2, 0, 0);
   b.print_board();
   cout << endl;
   b.rotate_cw(1);
   b.print_board();
   b.set_stone(WHITE, 0, 0, 0);
   b.set_stone(WHITE, 0, 1, 1);
   b.set_stone(WHITE, 0, 2, 2);
   b.set_stone(WHITE, 3, 0, 0);
   b.set_stone(WHITE, 0, 0, 1);
   b.set_stone(WHITE, 0, 0, 2);
   cout << "l: " << b.longest_line(WHITE) << endl;
   b.print_board();
   b.rotate_cw(3);
   b.print_board();

   b.set_stone(WHITE, 0, 2, 1);
   b.set_stone(WHITE, 1, 0, 0);
   b.set_stone(BLACK, 1, 1, 2);
   b.set_stone(BLACK, 2, 1, 1);
   b.set_stone(WHITE, 3, 2, 2);
   // b.board[0][0] = WHITE;
   // b.board[1][2] = BLACK;
   for(int i = 0; i < 10000000; i++){
      b.rotate_cw(0);
      b.rotate_ccw(0);
   }
   // b.print_board();
   return 0;
}
