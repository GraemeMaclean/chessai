import typing

import chess
import edq.util.json

import chessai.core.types

class Square(edq.util.json.DictConverter):
    """
    An immutable chess square on an 8x8 board.

    Squares are represented internally as a square index in [0, 63],
    following the standard chess convention:
      - Square 0  = a1 (file 0, rank 0) -- bottom-left from White's perspective
      - Square 63 = h8 (file 7, rank 7) -- top-right from White's perspective

    File increases left-to-right (a=0, h=7).
    Rank increases bottom-to-top (1=0, 8=7).
    """

    SQUARE_BOARD_SIZE: int = chessai.core.types.DEFAULT_BOARD_SIZE
    """ The number of files (columns) and ranks (rows) on a standard chess board. """

    NUM_SQUARES: int = SQUARE_BOARD_SIZE * SQUARE_BOARD_SIZE
    """ The total number of squares on a standard chess board. """

    def __init__(self, square: int) -> None:
        """
        Construct a Square from a square index in [0, 63].
        Prefer the named constructors (from_file_rank, from_square, from_name)
        for clarity.
        """

        if (square < 0 or square >= Square.NUM_SQUARES):
            raise ValueError(
                f"Square index {square} is out of range [0, {Square.NUM_SQUARES - 1}]."
            )

        self._square: int = square
        """
        The square index [0, 63].
        Cached as the hash value since square indices are already unique.
        """

    @classmethod
    def from_file_rank(cls, file: int, rank: int) -> 'Square':
        """
        Construct a Square from a (file, rank) pair.
        File and rank must both be in [0, 7].

        Example:
            Square.from_file_rank(0, 0)  # a1
            Square.from_file_rank(4, 3)  # e4
        """

        if (file < 0 or file >= Square.SQUARE_BOARD_SIZE):
            raise ValueError(f"File {file} is out of range [0, {Square.SQUARE_BOARD_SIZE - 1}].")

        if (rank < 0 or rank >= Square.SQUARE_BOARD_SIZE):
            raise ValueError(f"Rank {rank} is out of range [0, {Square.SQUARE_BOARD_SIZE - 1}].")

        return cls(chess.square(file, rank))

    @classmethod
    def from_square(cls, square: chess.Square) -> 'Square':
        """
        Construct a Square from a python-chess square constant.

        Example:
            Square.from_square(chess.E4)
            Square.from_square(chess.A1)
        """

        return cls(int(square))

    @classmethod
    def from_name(cls, name: str) -> 'Square':
        """
        Construct a Square from standard algebraic square name.

        Example:
            Square.from_name('e4')
            Square.from_name('a1')
        """

        square = chess.parse_square(name.lower())
        return cls(int(square))

    @property
    def square(self) -> int:
        """ The square index [0, 63]. Compatible with python-chess square constants. """
        return self._square

    @property
    def file(self) -> int:
        """ The file (column) of this square, in [0, 7]. a=0, h=7. """
        return chess.square_file(self._square)

    @property
    def rank(self) -> int:
        """ The rank (row) of this square, in [0, 7]. Rank 1=0, Rank 8=7. """
        return chess.square_rank(self._square)

    @property
    def name(self) -> str:
        """ The standard algebraic name of this square, e.g. 'e4'. """
        return chess.square_name(self._square)

    def offset(self, file_delta: int, rank_delta: int) -> 'Square | None':
        """
        Return the square reached by moving (file_delta, rank_delta) from this square,
        or None if the resulting square is off the board.
        """

        new_file = self.file + file_delta
        new_rank = self.rank + rank_delta

        if (new_file < 0 or new_file >= Square.SQUARE_BOARD_SIZE):
            return None

        if (new_rank < 0 or new_rank >= Square.SQUARE_BOARD_SIZE):
            return None

        return Square.from_file_rank(new_file, new_rank)

    def file_distance(self, other: 'Square') -> int:
        """ The absolute difference in file between this square and another. """
        return abs(self.file - other.file)

    def rank_distance(self, other: 'Square') -> int:
        """ The absolute difference in rank between this square and another. """
        return abs(self.rank - other.rank)

    def chebyshev_distance(self, other: 'Square') -> int:
        """
        The Chebyshev distance (chessboard distance) between two squares.
        This is the minimum number of king moves to travel between them.

        Useful as a building block for heuristics.
        """

        return max(self.file_distance(other), self.rank_distance(other))

    def manhattan_distance(self, other: 'Square') -> int:
        """
        The Manhattan distance between two squares.
        Note: this is NOT an admissible heuristic for knight movement,
        since a knight does not move in cardinal directions.
        Students should think carefully before using this in their heuristic.
        """

        return self.file_distance(other) + self.rank_distance(other)

    # def apply_action(self, action: chessai.core.action.Action) -> 'Square':
    #     """ Returns the Square that the action moves to. """

    #     start_square = action.get_start_square()
    #     if (self != start_square):
    #         raise ValueError(f"Actions applied must start from the same square: {action}")

    #     return action.get_end_square()

    def to_chess_square(self) -> chess.Square:
        """ Gets the Python chess library square. """
        return chess.square(self.file, self.rank)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'square': self._square,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> 'Square':
        return cls(data['square'])
