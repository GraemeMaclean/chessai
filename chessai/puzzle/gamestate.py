import random
import typing

import chessai.core.action
import chessai.core.board
import chessai.core.gamestate
import chessai.core.types
import chessai.puzzle.board

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a Puzzle game. """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 puzzle_solved: bool = False,
                 **kwargs: typing.Any) -> None:
        super().__init__(board, seed, game_over, **kwargs)

        # The dummy player for the current game is the opposite of the puzzle's starting player.
        self.dummy_player: chessai.core.types.Color = self.get_player().opposite()

        self.puzzle_solved: bool = puzzle_solved
        """
        Set to True when the agent has successfully completed one of the move lines.
        """

        self.board = typing.cast(chessai.puzzle.board.Board, self.board)

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

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        """
        Determine the outcome of the puzzle.

        The puzzle agent wins with score 1.0 if they fully completed one of the valid move lines.
        Otherwise the agent loses with score 0.0.
        """

        agent = self.dummy_player.opposite()

        if self.puzzle_solved:
            return ([agent], 1.0)

        return ([self.dummy_player], 0.0)

    def get_dummy_player(self) -> chessai.core.types.Color:
        """ Returns the dummy player for this puzzle. """

        return self.dummy_player

    def get_move_lines(self) -> list[list[chessai.core.action.Action]]:
        """ Get the move lines that the puzzle accepts as a solution. """

        self.board = typing.cast(chessai.puzzle.board.Board, self.board)

        return self.board.get_move_lines()

    def next_puzzle_moves(self) -> list[chessai.core.action.Action]:
        """ Get the list of possible next moves in the puzzle. """

        puzzle_moves = []

        move_lines = self.get_move_lines()
        for move_line in move_lines:
            if (len(move_line) > 0):
                puzzle_moves.append(move_line[0])

        return puzzle_moves

    def override_dummy_move(self, rng: random.Random) -> chessai.core.action.Action:
        """ Override the dummy player's move by selecting a continuation from one of the move lines. """

        if (self.get_player() != self.dummy_player):
            raise ValueError(f"Non dummy player's cannot override a dummy move: '{self.get_player()}'.")

        possible_moves = self.next_puzzle_moves()
        if (len(possible_moves) == 0):
            raise ValueError('Unable to find a valid continuation of the puzzle for the dummy agent.')

        chosen_move_list = rng.sample(possible_moves, 1)
        chosen_move = chosen_move_list[0]
        if (chosen_move not in self.get_legal_actions()):
            raise ValueError(f"Puzzle has a dummy move that is invalid: '{self.get_player()}', '{chosen_move.uci()}', '{self.board.get_fen()}'.")

        return chosen_move

    def _update_move_lines(self, action: chessai.core.action.Action) -> bool:
        """
        Update the possible puzzle lines based on the action taken.

        Returns whether the action matched at least one move line.
        """

        self.board = typing.cast(chessai.puzzle.board.Board, self.board)

        matched = self.board.update_move_lines(action)

        # If the action matched a move line and there are no remaining move lines, the puzzle is solved.
        if matched and len(self.board.get_move_lines()) == 0:
            self.puzzle_solved = True

        return matched
