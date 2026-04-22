import random
import typing

import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
import chessai.tour.gamestate

class Game(chessai.core.game.Game):
    """
    A tour game where the objective is to navigate a piece to the designated coordinates.
    """

    def __init__(self,
            game_info: chessai.core.game.GameInfo,
            fen: str,
            save_path: str | None = None,
            is_replay: bool = False,
            search_targets: list[chessai.core.coordinate.Coordinate] | dict[str, typing.Any] | None = None) -> None:
        super().__init__(game_info, fen, save_path, is_replay)

        if (search_targets is None):
            search_targets = []

        # Convert the string case into the dict case.
        if (isinstance(search_targets, str)):
            search_targets = {
                chessai.core.coordinate.COORDINATES_KEY: search_targets
            }

        if (isinstance(search_targets, dict)):
            search_targets = chessai.core.coordinate.coordinates_from_dict(search_targets)

        self.search_targets: list[chessai.core.coordinate.Coordinate] = search_targets
        """ The search targets of this game. """

    def get_initial_state(self,
            rng: random.Random,
            fen: str | None = None) -> chessai.core.gamestate.GameState:
        initial_state = chessai.tour.gamestate.GameState(fen = fen, search_targets = self.search_targets)
        if (len(self.search_targets) == 0):
            self.search_targets = initial_state.parsed_fen.search_targets

        return initial_state

    def process_turn(self,
            state: chessai.core.gamestate.GameState,
            action_record: chessai.core.agentaction.AgentActionRecord,
            result: chessai.core.game.GameResult,
            rng: random.Random,
            ) -> chessai.core.gamestate.GameState:
        """
        Process the given agent action and return an updated game state.
        The returned game state may be a copy or modified version of the passed in game state.
        """

        # The agent has timed out.
        if (action_record.timeout):
            result.timeout_agent_teams.append(action_record.player)
            state.process_agent_timeout(action_record.player)
            return state

        # The agent has crashed.
        if (action_record.crashed):
            result.crash_agent_teams.append(action_record.player)
            state.process_agent_crash(action_record.player)
            return state

        action = action_record.get_action()

        if (state.turn == chessai.core.types.Color.BLACK):
            return self._handle_black_turn(state, action, rng)

        if (action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action for agent {action_record.player}: '{action.uci()}' of type '{type(action)}'.")

        self._call_state_process_turn_full(state, action, rng)

        return state

    def check_end(self, state: chessai.core.gamestate.GameState) -> bool:
        """
        Check to see if the game is over.
        Return True if the game is now over, False otherwise.

        White wins by reaching all target squares.
        """

        state = typing.cast(chessai.tour.gamestate.GameState, state)

        if (state.game_over):
            return True

        return (len(state.search_targets) == 0)

    def _handle_black_turn(self, state: chessai.core.gamestate.GameState,
                    action: chessai.core.action.Action,
                    rng: random.Random) -> chessai.core.gamestate.GameState:
        """
        Black is not expected to be an agent in tour games.
        So, it may make null moves to pass the turn back to white.
        """

        self._call_state_process_turn_full(state, action, rng)

        return state
