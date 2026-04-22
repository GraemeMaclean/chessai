import random
import typing

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
            fen: str | None = None,
            extra_info: dict[str, typing.Any] | None = None) -> chessai.core.gamestate.GameState:
        return chessai.chess.gamestate.GameState(fen = fen)
