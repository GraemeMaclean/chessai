#!/usr/bin/env python3

import sys

import chessai.chess.bin

def main():
    ARG_STRING = '--white-team agent-random --black-team agent-random --seed 4 --num-games 10'

    sys.argv += ARG_STRING.split()
    chessai.chess.bin.main()

if __name__ == '__main__':
    main()
