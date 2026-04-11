import logging
import random
import typing

import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
import chessai.puzzle.gamestate

class Game(chessai.core.game.Game):
    """
    A game following the standard rules of Pac-Man.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: chessai.core.board.Board,
            agent_infos: dict[chessai.core.types.Color, chessai.core.agentinfo.AgentInfo]) -> chessai.core.gamestate.GameState:
        return chessai.puzzle.gamestate.GameState(board = board, agent_infos = agent_infos)

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

        state = typing.cast(chessai.puzzle.gamestate.GameState, state)

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

        if (state.get_player() == state.get_dummy_player()):
            return self._process_dummy_turn(state, action, rng)

        if (action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action for agent {action_record.player}: '{action.uci()}' of type '{type(action)}'.")

        if (action not in state.next_puzzle_moves()):
            # TEST
            logging.debug("Found puzzle moves: '%s'.", state.next_puzzle_moves())
            logging.info("Incorrect action for agent '%s': '%s' of type '%s'.", action_record.player, action.uci(), type(action))
            state.game_over = True

        self._call_state_process_turn_full(state, action, rng)

        return state

    def check_end(self, state: chessai.core.gamestate.GameState) -> bool:
        """
        Check to see if the game is over.
        Return True if the game is now over, False otherwise.

        The agent wins by completing the move lines.
        """

        if (state.game_over):
            return True

        board = state.get_board()

        board = typing.cast(chessai.puzzle.board.Board, board)

        return (len(board.get_move_lines()) == 0)

    def _process_dummy_turn(self,
            state: chessai.core.gamestate.GameState,
            action: chessai.core.action.Action,
            rng: random.Random,
            ) -> chessai.core.gamestate.GameState:
        """ Process a dummy player turn by following a random move line. """

        if (not (isinstance(state, chessai.puzzle.gamestate.GameState))):
            raise ValueError(f"Puzzle games require a puzzle gamestate, got: '{type(state)}'.")

        if (action != chessai.core.action.Action()):
            raise ValueError(f"Dummy player: '{state.get_dummy_player()}' did not make a null move '{action.uci()}'.")

        overriden_action = state.override_dummy_move()

        self._call_state_process_turn_full(state, overriden_action, rng)

        return state
