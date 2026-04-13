import random

import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
import chessai.tour.gamestate

class Game(chessai.core.game.Game):
    """
    A game following the standard rules of Pac-Man.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: chessai.core.board.Board,
            agent_infos: dict[chessai.core.types.Color, chessai.core.agentinfo.AgentInfo]) -> chessai.core.gamestate.GameState:
        return chessai.tour.gamestate.GameState(board = board, agent_infos = agent_infos)

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

        if (state.get_player() == chessai.core.types.Color.BLACK):
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

        if (state.game_over):
            return True

        return (len(state.get_search_targets()) == 0)

    def _handle_black_turn(self, state: chessai.core.gamestate.GameState,
                    action: chessai.core.action.Action,
                    rng: random.Random) -> chessai.core.gamestate.GameState:
        """
        Black is not expected to be an agent in tour games.
        So, it may make null moves to pass the turn back to white.
        """

        self._call_state_process_turn_full(state, action, rng)

        return state
