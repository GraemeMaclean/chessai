import argparse
# import json
import logging
import random
import typing

# import edq.util.json

import chessai.core.agentinfo
import chessai.core.board
import chessai.core.game
import chessai.core.gamestate
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

    def __init__(self,
            game_info: chessai.core.game.GameInfo,
            fen: str,
            save_path: str | None = None,
            is_replay: bool = False,
            move_lines: list[list[chessai.core.action.Action]] | dict[str, typing.Any] | None = None) -> None:
        super().__init__(game_info, fen, save_path, is_replay)

        if (move_lines is None):
            move_lines = []

        # Convert the string case into the dict case.
        if (isinstance(move_lines, str)):
            move_lines = {
                chessai.core.action.ACTION_KEY: move_lines
            }

        if (isinstance(move_lines, dict)):
            move_lines = chessai.core.action.actions_list_from_dict(move_lines)

        self.move_lines: list[list[chessai.core.action.Action]] = move_lines
        """ The move lines of this puzzle. """

        self.start_move_lines: list[list[chessai.core.action.Action]] = move_lines.copy()
        """ The starting move lines of the puzzle, which will remain static throughout the game. """

    def process_args(self, args: argparse.Namespace) -> None:
        if (args.move_lines is not None):
            move_lines = {
                chessai.core.action.ACTION_KEY: args.move_lines
            }

            self.move_lines = chessai.core.action.actions_list_from_dict(move_lines)
            self.start_move_lines = self.move_lines.copy()

    def get_initial_state(self,
            rng: random.Random,
            fen: str | None = None) -> chessai.core.gamestate.GameState:
        # Let the gamestate parse the FEN so we can look for move lines from a file.
        initial_state = chessai.puzzle.gamestate.GameState(fen = fen)

        if ((len(self.move_lines) == 0) and (initial_state.parsed_fen.options is not None)):
            raw_move_lines = {
                chessai.core.action.ACTION_KEY: initial_state.parsed_fen.options.get('move_lines', None)
            }

            self.move_lines = chessai.core.action.actions_list_from_dict(raw_move_lines)
            self.start_move_lines = self.move_lines.copy()

        return initial_state

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

        if (state.turn == state.dummy_player):
            action = self._override_dummy_move(state, rng)

        if (action not in state.get_legal_actions()):
            raise ValueError(
                f"Illegal action for agent {action_record.player}: "
                f"'{action.uci()}' of type '{type(action)}'."
            )

        # Check whether the move follows any of the remaining move lines.
        if (action not in self._next_puzzle_moves()):
            logging.debug("Found puzzle moves: '%s'.", self._next_puzzle_moves())
            logging.info(
                "Incorrect action for agent '%s': '%s' of type '%s'.",
                action_record.player, action.uci(), type(action),
            )

            # The agent failed to solve the puzzle, so the game is over.
            state.game_over = True
            return state

        self._call_state_process_turn_full(state, action, rng)

        # Progress the move lines of the puzzle.
        self._update_move_lines(state, action)

        return state

    def check_end(self, state: chessai.core.gamestate.GameState) -> bool:
        if state.game_over:
            return True

        state = typing.cast(chessai.puzzle.gamestate.GameState, state)

        return (len(self.move_lines) == 0)

    def _override_dummy_move(self, state: chessai.puzzle.gamestate.GameState, rng: random.Random) -> chessai.core.action.Action:
        """ Override the dummy player's move by selecting a continuation from one of the move lines. """

        if (state.turn != state.dummy_player):
            raise ValueError(f"Non dummy player's cannot override a dummy move: '{state.turn}'.")

        possible_moves = self._next_puzzle_moves()
        if (len(possible_moves) == 0):
            raise ValueError('Unable to find a valid continuation of the puzzle for the dummy agent.')

        chosen_move_list = rng.sample(possible_moves, 1)
        chosen_move = chosen_move_list[0]
        if (chosen_move not in state.get_legal_actions()):
            raise ValueError(f"Puzzle has a dummy move that is invalid: '{state.turn}', '{chosen_move.uci()}', '{state.get_fen()}'.")

        return chosen_move

    def _next_puzzle_moves(self) -> list[chessai.core.action.Action]:
        """ Get the list of possible next moves in the puzzle. """

        puzzle_moves = []

        move_lines = self.move_lines
        for move_line in move_lines:
            if (len(move_line) > 0):
                puzzle_moves.append(move_line[0])

        return puzzle_moves

    def _update_move_lines(self, state: chessai.puzzle.gamestate.GameState, action: chessai.core.action.Action) -> bool:
        """
        Update the possible puzzle lines based on the action taken.

        Returns whether the action matched at least one move line.
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

        # If the action matched a move line and there are no remaining move lines, the puzzle is solved.
        if matched_move_line and len(self.move_lines) == 0:
            state.puzzle_solved = True

        return matched_move_line
