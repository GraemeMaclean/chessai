import random

import chessai.chess.gamestate
import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate

RANDOM_BOARD_PREFIX: str = 'random'

class Game(chessai.core.game.Game):
    """
    A game following the standard rules of Chess.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: chessai.core.board.Board,
            agent_infos: dict[chessai.core.types.Color, chessai.core.agentinfo.AgentInfo],
            ) -> chessai.core.gamestate.GameState:
        return chessai.chess.gamestate.GameState(board = board, agent_infos = agent_infos)
