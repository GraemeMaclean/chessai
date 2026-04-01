import random

import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
import chessai.errant.gamestate

class Game(chessai.core.game.Game):
    """
    A game following the standard rules of Pac-Man.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: chessai.core.board.Board,
            agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo]) -> chessai.core.gamestate.GameState:
        return chessai.errant.gamestate.GameState(board = board, agent_infos = agent_infos)
