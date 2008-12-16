#!/bin/sh

gcc -c board.c ai.c --std=c99;
gcc board.o ai.o -o debug_build;
rm board.o ai.o;
