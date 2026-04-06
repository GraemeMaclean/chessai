"""
This module handles containers for passing information from agents back to the game (via isolators).
"""

import typing

import edq.util.json
import edq.util.time

import chessai.core.action

class AgentAction(edq.util.json.DictConverter):
    """
    The full response by an agent when an action is requested.
    Agent's usually just provide actions, but more information can be supplied if necessary.
    """

    def __init__(self,
            action: chessai.core.action.Action | None = None,
            other_info: dict[str, typing.Any] | None = None,
            ) -> None:
        if (action is None):
            action = chessai.core.action.NULL_ACTION

        self.action: chessai.core.action.Action = action
        """ The action returned by the agent (or chessai.core.action.NULL_ACTION on a crash). """

        if (other_info is None):
            other_info = {}

        self.other_info: dict[str, typing.Any] = other_info
        """
        Additional information that the agent wishes to pass to the game.
        Specific games may use or ignore this information.

        All information put here must be trivially JSON serializable.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'action': self.action.to_dict() if (self.action is not None) else None,
            'other_info': self.other_info,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(
            action = chessai.core.action.Action.from_dict(data['action']) if data['action'] is not None else None,
            other_info = data.get('other_info', None),
        )

class AgentActionRecord(edq.util.json.DictConverter):
    """
    The full representation of requesting an action from an agent.
    In addition to the data supplied by the agent,
    this class contains administrative fields used to keep track of the agent.
    """

    def __init__(self,
            player: chessai.core.types.Color,
            agent_action: AgentAction | None,
            duration: edq.util.time.Duration,
            crashed: bool = False,
            timeout: bool = False,
            ) -> None:
        self.player: chessai.core.types.Color = player
        """ The player for the agent making this action. """

        self.agent_action: AgentAction | None = agent_action
        """ The information returned by the agent or None on a crash or timeout. """

        self.duration: edq.util.time.Duration = duration
        """ The duration (in MS) the agent took to compute this action. """

        self.crashed: bool = crashed
        """ Whether or not the agent crashed (e.g., raised an exception) when computing this action. """

        self.timeout: bool = timeout
        """ Whether or not the agent timed out when computing this action. """

    def get_action(self) -> chessai.core.action.Action:
        """ Get the agent's action. """

        if (self.agent_action is None):
            return chessai.core.action.NULL_ACTION

        return self.agent_action.action

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'player': self.player,
            'agent_action': self.agent_action.to_dict() if (self.agent_action is not None) else None,
            'duration': self.duration,
            'crashed': self.crashed,
            'timeout': self.timeout,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(
            player = data['player'],
            agent_action = AgentAction.from_dict(data['agent_action']) if data['agent_action'] is not None else None,
            duration = edq.util.time.Duration(data['duration']),
            crashed = data.get('crashed', False),
            timeout = data.get('timeout', False),
        )
