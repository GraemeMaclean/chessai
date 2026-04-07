import random
import typing

import chessai.core.action
import chessai.core.board
import chessai.core.gamestate
import chessai.core.types

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a Puzzle game. """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        # The dummy player for the current game is the opposite of the puzzle's starting player.
        self.dummy_player: chessai.core.types.Color = board.get_player().opposite()

        super().__init__(board, seed, game_over, **kwargs)

        # TODO(Lucas): How do we want to track puzzle moves.

    # TODO(Lucas): Should we store puzzle moves and check each turn, or analyze at the end?
    def process_turn(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        board = self.get_board()
        board._push(action)

        self._update_move_lines(action)

    # TODO(Lucas): What denotes a complete game?
    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        if (len(board.get_move_lines()) == 0):
            return ([self.dummy_player.opposite()], 0)

        return ([self.dummy_player], 0)

    def get_dummy_player(self) -> chessai.core.types.Color:
        """ Returns the dummy player for this puzzle. """

        return self.dummy_player

    def get_move_lines(self) -> list[list[chessai.core.action.Action]]:
        """ Get the move lines that the puzzle accepts as a solution. """

        return self.board.get_move_lines()

    def override_dummy_move(self) -> chessai.core.action.Action:
        """ Override the dummy player's move by selecting a continuation from one of the move lines. """

        if (self.get_player() != self.dummy_player):
            raise ValueError(f"Non dummy player's cannot override a dummy move: '{self.get_player()}'.")

        move_lines = self.get_move_lines()

        # TODO(Lucas): If tests are flaky, we will need to seed the randomness.
        # Select a random move line to continue.
        move_line = random.sample(move_lines, 1)
        if (len(move_line) > 0):
            return move_line[0]

        return chessai.core.action.Action()

    def _update_move_lines(self, action: chessai.core.action.Action) -> None:
        """ Update the possible puzzle lines based on the action taken. """

        move_lines = self.board.update_move_lines(action)
