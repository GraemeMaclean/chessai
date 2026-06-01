#!/usr/bin/env python3

import sys

import chessai.chess.bin
import chessai.puzzle.bin

def main():
    # ARG_STRING = '--white-team agent-random --black-team agent-random --seed 4 --num-games 10'
    # ARG_STRING = '--agent /home/lucas-ellenberger/cse240-assignments-ta/Assignment2/test-submissions/lucas_solution/multiagents.py:MyMinimaxLikeAgent'
    # ARG_STRING = '--agent /home/lucas-ellenberger/cse240-assignments-ta/Assignment2/test-submissions/lucas_solution/multiagents.py:MyMinimaxLikeAgent --board puzzle-mate-3'
    ARG_STRING = ('--agent /home/lucas-ellenberger/cse240-assignments-ta/Assignment2/test-submissions/lucas_solution/multiagents.py:MyMinimaxLikeAgent'
                  + ' --agent-arg black::state_eval_func=state-eval-minimax-better --agent-arg black::alphabeta_prune=true --board puzzle-mate-3')

    sys.argv += ARG_STRING.split()
    # chessai.chess.bin.main()
    chessai.puzzle.bin.main()

if __name__ == '__main__':
    main()
