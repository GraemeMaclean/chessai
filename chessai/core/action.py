"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import re

import edq.util.json

import chessai.core.coordinate
import chessai.core.types

ACTION_PATTERN: re.Pattern = re.compile(r'^([a-z]+\d+)([a-z]+\d+)([a-z]?)$')

UCI_NULL_ACTION: str = '0000'

class Action(edq.util.json.DictConverter):
    """
    The possible actions that an agent is allowed to take.

    Actions are strings in the Chess UCI format
    (https://en.wikipedia.org/wiki/Universal_Chess_Interface).
    """

    def __init__(self,
                 start_coordinate: chessai.core.coordinate.Coordinate = chessai.core.coordinate.NULL_COORDINATE,
                 end_coordinate: chessai.core.coordinate.Coordinate = chessai.core.coordinate.NULL_COORDINATE,
                 promotion: chessai.core.types.PieceType | None = None) -> None:

        self.start_coordinate: chessai.core.coordinate.Coordinate = start_coordinate
        """ The starting coordinate for the action. """

        self.end_coordinate: chessai.core.coordinate.Coordinate = end_coordinate
        """ The ending coordinate for the action. """

        self.promotion: chessai.core.types.PieceType | None = promotion
        """ The piece to promote to, or None if this is not a promotion move. """

    def uci(self) -> str:
        """ Represent the agent action as a chess move in UCI format. """

        # The null action in UCI is encoded as '0000'.
        if (self == NULL_ACTION):
            return UCI_NULL_ACTION

        start = self.start_coordinate.uci()
        end = self.end_coordinate.uci()
        promotion = self.promotion.symbol if (self.promotion is not None) else ''

        return f"{start}{end}{promotion}"

    @classmethod
    def from_uci(cls, uci: str) -> 'Action':
        """
        Get an action from the UCI format.
        Note that this project supports arbitrary sized boards.
        """

        # Check for the null UCI move.
        if (uci == UCI_NULL_ACTION):
            return cls()

        match = ACTION_PATTERN.fullmatch(uci)
        if (match is None):
            raise ValueError('An action must be a pair of coordinates with an optional promotion piece:'
                    + f" '{ACTION_PATTERN.pattern}',"
                    + f" got: '{uci}'.")

        start_coordinate = chessai.core.coordinate.Coordinate.from_uci(match.group(1))
        end_coordinate = chessai.core.coordinate.Coordinate.from_uci(match.group(2))

        # If there is a trailing character, try to parse it as a promotion piece type.
        tail = match.group(3)
        promotion: chessai.core.types.PieceType | None = None

        if (len(tail) == 1):
            if (tail not in chessai.core.types.PIECE_SYMBOLS):
                raise ValueError(f"Unknown promotion piece symbol '{tail}' in UCI string: '{uci}'.")

            promotion = chessai.core.types.PIECE_SYMBOLS[tail]

        return cls(start_coordinate, end_coordinate, promotion)

NULL_ACTION = Action()
