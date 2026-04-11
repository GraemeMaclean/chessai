import copy
import re
import typing

import chessai.core.action
import chessai.core.board

MOVE_LINES_KEY: str = 'move_lines'
MOVE_LINE_INNER_PATTERN: re.Pattern = re.compile(r'\[([^\]]*)\]')

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
        parsed_move_lines: list[list[chessai.core.action.Action]]
        if move_lines is None:
            parsed_move_lines = []
        elif isinstance(move_lines, dict):
            parsed_move_lines = move_lines_from_string(move_lines.get(MOVE_LINES_KEY, ''))
        elif isinstance(move_lines, str):
            parsed_move_lines = move_lines_from_string(move_lines)
        else:
            parsed_move_lines = move_lines

        # TODO(Lucas): We will need a space for feedback later, but should it be attached to the move line or general?
        self.move_lines: list[list[chessai.core.action.Action]] = parsed_move_lines
        """ The valid solutions to a puzzle game, with the associated feedback. """

        super().__init__(*args, **kwargs)

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

def move_lines_from_string(raw: str) -> list[list[chessai.core.action.Action]]:
    """
    Parse a move lines string into a list of lists of Actions.

    The expected format is one or more bracketed, comma-separated lists of UCI moves,
    all wrapped in an outer bracket:
        "[[c6d5, e2e4], [c6d5, e2e3]]"
        "[[c6d5]]"

    Each UCI token must be a valid chess move (e.g. 'e2e4', 'a7a8q').
    Whitespace around tokens is ignored.
    """

    raw = raw.strip()

    if (len(raw) == 0):
        return []

    # Strip the outermost brackets.
    if not (raw.startswith('[') and raw.endswith(']')):
        raise ValueError(f"Puzzle move_lines string must be wrapped in '[...]': '{raw}'.")
    raw = raw[1:-1].strip()

    if (len(raw) == 0):
        return []

    # Split on inner brackets: find each '[...]' group.
    groups = MOVE_LINE_INNER_PATTERN.findall(raw)

    if (len(groups) == 0):
        raise ValueError(f"move_lines string contains no inner '[...]' groups: '{raw}'.")

    move_lines: list[list[chessai.core.action.Action]] = []
    for group in groups:
        tokens = [t.strip() for t in group.split(',') if t.strip()]
        actions = [chessai.core.action.Action(uci) for uci in tokens]
        move_lines.append(actions)

    return move_lines
