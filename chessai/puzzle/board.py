import typing

import chessai.core.board

class Board(chessai.core.board.Board):
    """
    A board for Puzzle games.

    In addition to walls, Puzzle boards also have:
    move lines that represent potential solutions
    and potential feedback for moves.
    """

    # TODO: We will need a space for feedback later, but should it be attached to the move line or general?
    def __init__(self, *args: typing.Any,
            move_lines: list[list[chessai.core.action.Action]] | dict[str, typing.Any] | None = None,
            **kwargs: typing.Any) -> None:
        if (move_lines is None):
            move_lines = []

        self.move_lines: list[list[chessai.core.action.Action]] = move_lines # type: ignore
        """ The valid solutions to a puzzle game, with the associated feedback. """

        # TODO(Lucas): Handle to the dict case for move lines.

        super().__init__(*args, **kwargs)  # type: ignore

    # TODO(Lucas): Add additional methods to check if a move follows a specific move lines.
