"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import re

import edq.util.json

import chessai.core.coordinate

class Action(edq.util.json.DictConverter):
    """
    The possible actions that an agent is allowed to take.

    Actions are strings in the Chess UCI format
    (https://en.wikipedia.org/wiki/Universal_Chess_Interface).
    """

    def __init__(self,
                 start_coordinate: chessai.core.coordinate.Coordinate = chessai.core.coordinate.NULL_COORDINATE,
                 end_coordinate: chessai.core.coordinate.Coordinate = chessai.core.coordinate.NULL_COORDINATE) -> None:

        self.start_coordinate: chessai.core.coordinate.Coordinate = start_coordinate
        """ The starting coordinate for the action. """

        self.end_coordinate: chessai.core.coordinate.Coordinate = end_coordinate
        """ The ending coordinate for the action. """

    def uci(self) -> str:
        """ Represent the agent action as a chess move in UCI format. """

        start = self.start_coordinate.uci()
        end = self.end_coordinate.uci()

        return f"{start}{end}"

    @classmethod
    def from_uci(cls, uci: str) -> 'Action':
        """
        Get an action from the UCI format.
        Note that this project supports arbitrary sized boards.
        """

        matches = re.finditer(chessai.core.coordinate.COORDINATE_PATTERN, uci)
        coordinates = [match.group(0) for match in matches]
        if (len(coordinates) != 2):
            raise ValueError('An action must be a pair of coordinates'
                    + f" '{chessai.core.coordinate.COORDINATE_PATTERN.pattern}{chessai.core.coordinate.COORDINATE_PATTERN.pattern}',"
                    + f" got: '{uci}'.")

        start_coordinate = chessai.core.coordinate.Coordinate.from_uci(coordinates[0])
        end_coordinate = chessai.core.coordinate.Coordinate.from_uci(coordinates[1])

        return cls(start_coordinate, end_coordinate)

NULL_ACTION = Action()
