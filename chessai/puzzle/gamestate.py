import typing

import chessai.chess.piece
import chessai.core.action
import chessai.core.board
import chessai.core.gamestate
import chessai.core.types

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a Puzzle game. """

    def __init__(self,
                 fen: str | None = None,
                 move_stack: list[chessai.core.action.Action] | None = None,
                 board_stack: list[chessai.core.board.Board] | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 puzzle_solved: bool = False,
                 **kwargs: typing.Any) -> None:
        super().__init__(fen, move_stack, board_stack, seed, game_over, **kwargs)

        self.puzzle_solved: bool = puzzle_solved
        """ Set to True when the agent has successfully completed one of the move lines. """

        self.dummy_player: chessai.core.types.Color = self.turn.opposite()
        """ The dummy player for the current game, which is the opponent to the puzzle's starting player. """

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        """
        Determine the outcome of the puzzle.

        The puzzle agent wins with score 1.0 if they fully completed one of the valid move lines.
        Otherwise the agent loses with score 0.0.
        """

        agent = self.dummy_player.opposite()

        if self.puzzle_solved:
            return ([agent], 1.0)

        return ([self.dummy_player], 0.0)
