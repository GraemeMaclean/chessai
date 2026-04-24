#!/usr/bin/env python3

import sys

import chessai.chess.bin

def main():
    # ARG_STRING = '--pacman /home/eriq/code/cse140-assignments-private/p2/test-submissions/solution/multiagents.py:MinimaxAgent --board classic-minimax --agent-arg 0::ply_count=4 --ui null --num-games 100 --isolation process'
    # ARG_STRING = '--pacman /home/eriq/code/cse140-assignments-private/p2/test-submissions/solution/multiagents.py:MinimaxAgent --board classic-minimax --agent-arg 0::ply_count=4 --ui null --num-games 100'
    # ARG_STRING = '--board search-test --pacman agent-search-problem --agent-arg 0::problem=search-problem-food --ui null --seed 4 --num-games 100'
    # ARG_STRING = '--pacman agent-search-problem --board search-test --agent-arg 0::problem=search-problem-food --agent-arg 0::solver=/home/eriq/code/cse140-assignments-private/p1/test-submissions/solution/singlesearch.py:depth_first_search --ui null --seed 4 --num-games 100'
    ARG_STRING = '--white-team agent-random --black-team agent-random --seed 4 --num-games 1'

    sys.argv += ARG_STRING.split()
    chessai.chess.bin.main()

if __name__ == '__main__':
    main()
