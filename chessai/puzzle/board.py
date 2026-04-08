import copy
import typing

import chessai.core.board

class Board(chessai.core.board.Board):
    """
    A board for Puzzle games.

    In addition to walls, Puzzle boards also have:
    move lines that represent potential solutions
    and potential feedback for moves.
    """

    def __init__(self, *args: typing.Any,
            move_lines: list[list[chessai.core.action.Action]] | dict[str, typing.Any] | None = None,
            **kwargs: typing.Any) -> None:
        if (move_lines is None):
            move_lines = []

        self.move_lines: list[list[chessai.core.action.Action]] = move_lines # type: ignore
        """ The valid solutions to a puzzle game, with the associated feedback. """

        # TODO(Lucas): We will need a space for feedback later, but should it be attached to the move line or general?
        # TODO(Lucas): Handle to the dict case for move lines.

        super().__init__(*args, **kwargs)  # type: ignore

    # TODO(Lucas): Add additional methods to check if a move follows a specific move lines.
    def get_move_lines(self) -> list[list[chessai.core.action.Action]]:
        """ Gets the valid solutions to a puzzle game. """

        return self.move_lines

    def update_move_lines(self, action: chessai.core.action.Action) -> bool:
        """
        Update the move lines based on the agents action.
        Returns true if the action satisfies at least one move line, else false.
        """

        new_move_lines = []
        matched_move_line = False

        for move_line in self.move_lines:
            if (len(move_line) == 0):
                continue

            # Skip if the action is not consistent with the move line.
            if (move_line[0] != action):
                continue

            matched_move_line = True

            new_move_line = move_line[1:]

            # If there is nothing left in the move line, skip it.
            if (len(new_move_line) == 0):
                continue

            new_move_lines.append(new_move_line)

        self.move_lines = new_move_lines
        return matched_move_line

    def copy(self) -> 'Board':
        board = super().copy()

        board = typing.cast('Board', board)

        board.move_lines = copy.deepcopy(self.move_lines)
        return board
