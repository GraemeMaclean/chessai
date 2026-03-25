"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import typing

import chess
import edq.util.json

UCI_NULL_MOVE: str = '0000'

class Action(edq.util.json.DictConverter):
    """
    The possible actions that an agent is allowed to take.

    Actions are strings in the Chess UCI format
    (https://en.wikipedia.org/wiki/Universal_Chess_Interface).
    """

    def __init__(self,
                 uci: str = UCI_NULL_MOVE):
        self.move = chess.Move.from_uci(uci)
        """ The move for the action. """

    def uci(self) -> str:
        """ Represent the agent action as a chess move in UCI format. """
        return self.move.uci()

    def get_move(self) -> chess.Move:
        """ Return the chess move corresponding to the action. """
        return self.move

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'uci': self.uci(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()
        return cls(**data)

NULL_ACTION = Action()
