import logging
import random
import typing

import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
import chessai.puzzle.board
import chessai.puzzle.gamestate

class Game(chessai.core.game.Game):
    """
    A game following the rules of a chess puzzle.

    The agent wins by completing any one of the board's valid move lines.
    The opposing side is played by a dummy agent that follows a scripted continuation.

    The game ends as soon as:
      - The agent plays a move that satisfies the final step of a move line (puzzle solved).
      - The agent plays a move that is not consistent with ANY remaining move line (puzzle failed).
    """

    def get_initial_state(self,
            rng: random.Random,
            fen: str | None = None) -> chessai.core.gamestate.GameState:
        return chessai.puzzle.gamestate.GameState(fen = fen)

    def process_turn(self,
            state: chessai.core.gamestate.GameState,
            action_record: chessai.core.agentaction.AgentActionRecord,
            result: chessai.core.game.GameResult,
            rng: random.Random,
            ) -> chessai.core.gamestate.GameState:
        """
        Process the given agent action and return an updated game state.
        The returned game state may be a copy or modified version of the passed-in game state.
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

        if (state.turn == state.get_dummy_player()):
            return self._process_dummy_turn(state, action, rng)

        if (action not in state.get_legal_actions()):
            raise ValueError(
                f"Illegal action for agent {action_record.player}: "
                f"'{action.uci()}' of type '{type(action)}'."
            )

        # Check whether the move follows any of the remaining move lines.
        if (action not in state.next_puzzle_moves()):
            logging.debug("Found puzzle moves: '%s'.", state.next_puzzle_moves())
            logging.info(
                "Incorrect action for agent '%s': '%s' of type '%s'.",
                action_record.player, action.uci(), type(action),
            )

            # The agent failed to solve the puzzle, so the game is over.
            state.game_over = True

        self._call_state_process_turn_full(state, action, rng)

        return state

    def check_end(self, state: chessai.core.gamestate.GameState) -> bool:
        if state.game_over:
            return True

        board = typing.cast(chessai.puzzle.board.Board, state.board)

        return (len(board.get_move_lines()) == 0)

    def _process_dummy_turn(self,
            state: chessai.core.gamestate.GameState,
            action: chessai.core.action.Action,
            rng: random.Random,
            ) -> chessai.core.gamestate.GameState:
        """ Process a dummy player turn by following a random move line. """

        if (not isinstance(state, chessai.puzzle.gamestate.GameState)):
            raise ValueError(
                f"Puzzle games require a puzzle gamestate, got: '{type(state)}'."
            )

        if (action != chessai.core.action.Action()):
            raise ValueError(
                f"Dummy player: '{state.get_dummy_player()}' did not make a "
                f"null move '{action.uci()}'."
            )

        overriden_action = state.override_dummy_move(rng)

        self._call_state_process_turn_full(state, overriden_action, rng)

        return state
