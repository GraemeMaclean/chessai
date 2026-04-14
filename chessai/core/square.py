import typing

import edq.util.json

import chessai.core.board

SQUARES_KEY: str = 'squares'

FILE_ALPHABET: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

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

    def __init__(self,
                 square: int,
                 files: int = chessai.core.board.DEFAULT_BOARD_FILES,
                 ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS) -> None:
        """ Construct a Square from a square index in [0, files * ranks]. """

        self.square: int = square
        """ The square index [0, BOARD_SIZE]. """

        self.files = files
        """ The number of files on the board this square belongs to. """

        self.ranks = ranks
        """ The number of ranks on the board this square belongs to. """

    @classmethod
    def from_file_rank(cls, file: int, rank: int,
            files: int = chessai.core.board.DEFAULT_BOARD_FILES,
            ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS) -> 'Square':
        """ Construct a Square from a (file, rank) pair. """

        if ((file < 0) or (file >= files)):
            raise ValueError(f"File {file} is out of range [0, {files - 1}].")

        if (rank < 0 or rank >= ranks):
            raise ValueError(f"Rank {rank} is out of range [0, {ranks - 1}].")

        # TODO(Lucas): Check this logic
        square_number = (file * files) + (rank)

        return cls(square_number, files, ranks)

    @classmethod
    def from_name(cls,
            name: str,
            files: chessai.core.board.DEFAULT_BOARD_FILES,
            ranks: chessai.core.board.DEFAULT_BOARD_RANKS) -> 'Square':
        """ Construct a Square from standard algebraic square name. """

        square = chess.parse_square(name.lower())
        return cls(int(square))

    def file(self) -> int:
        """ The file (column) of this square, in [0, files]. a=0, b=1, c=2... """

        return (self.square // self.files)

    def rank(self) -> int:
        """ The rank (row) of this square, in [0, ranks]. Rank 1=0, Rank 2=1... """

        return (self.square % self.ranks)

    def name(self) -> str:
        """ The standard algebraic name of this square, e.g. 'e4'. """

        file = self.file()
        file_name = ''
        while (file > len(FILE_ALPHABET)):
            file_name += FILE_ALPHABET[-1]
            file -= len(FILE_ALPHABET)

        file_name += FILE_ALPHABET[file]

        rank = str(self.rank())

        return file_name + rank

    def offset(self, file_delta: int, rank_delta: int) -> 'Square | None':
        """
        Return the square reached by moving (file_delta, rank_delta) from this square,
        or None if the resulting square is off the board.
        """

        new_file = self.file + file_delta
        new_rank = self.rank + rank_delta

        if ((new_file < 0) or (new_file >= self.files)):
            return None

        if ((new_rank < 0) or (new_rank >= self.ranks)):
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

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'square': self.square,
            'files': self.files,
            'ranks': self.ranks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> 'Square':
        return cls(
                data['square'],
                data.get('files', chessai.core.board.DEFAULT_BOARD_FILES),
                data.get('ranks', chessai.core.board.DEFAULT_BOARD_FILES),
            )

def squares_from_dict(data: dict[str, typing.Any],
            files: int = chessai.core.board.DEFAULT_BOARD_FILES,
            ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS) -> list[Square]:
    """
    Get a list of squares from a dict.
    The 'squares' key will be checked.
    """

    clean_squares: list[Square] = []

    raw_squares = data.get(SQUARES_KEY, [])
    if (isinstance(raw_squares, str)):
        raw_squares = raw_squares.split(',')

    for raw_square in raw_squares:
        clean_square = None

        if (isinstance(raw_square, dict)):
            clean_square = Square.from_dict(raw_square)
        elif (isinstance(raw_square, int)):
            clean_square = Square(raw_square, files, ranks)
        elif (isinstance(raw_square, str)):
            clean_square = Square(int(raw_square), files, ranks)

        if (clean_square is not None):
            clean_squares.append(clean_square)

    return clean_squares
