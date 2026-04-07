import random
import typing

import chessai.core.action
import chessai.core.board
import chessai.core.gamestate

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a Puzzle game. """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        super().__init__(board, seed, game_over, **kwargs)

        # TODO(Lucas): How do we want to track puzzle moves.

    # TODO(Lucas): Should we store puzzle moves and check each turn, or analyze at the end?
    def process_turn(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        board = self.get_board()
        board._push(action)

    # TODO(Lucas): What denotes a complete game?
    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        return ([chessai.core.types.Color.BLACK], 0)
