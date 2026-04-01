import io
import dataclasses
import enum
import os
import re
import typing

import chess
import chess.pgn
import edq.util.json

import chessai.core.action
import chessai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'boards')

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')
AGENT_PATTERN: re.Pattern = re.compile(r'^\d$')

FILE_EXTENSION = '.board'

DEFAULT_BOARD_CLASS: str = 'chessai.core.board.Board'
DEFAULT_BOARD_SIZE: int = 8

class Color(int, enum.Enum):
    """ An enum representing the side to move or the color of a piece. """
    WHITE = 1
    BLACK = 0

    @property
    def symbol(self) -> str:
        """ Retruns 'w' for white and 'b' for black. """
        return 'w' if self == Color.WHITE else 'b'

    def opposite(self) -> 'Color':
        """ Returns the opposing color — useful for switching sides after a move. """
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    def __str__(self) -> str:
        return self.name.lower()  # "white" or "black"

    def __repr__(self) -> str:
        return f"Color.{self.name}"

    def __bool__(self) -> bool:
        return bool(self.value)

class PieceType(str, enum.Enum):
    """ An enum representing the different chess pieces. """

    KING = 'k'
    QUEEN = 'q'
    KNIGHT = 'n'
    BISHOP = 'b'
    ROOK = 'r'
    PAWN = 'p'

    @property
    def symbol(self) -> str:
        """ Returns the lowercase symbol for this piece type. """
        return self.value

    @property
    def name_str(self) -> str:
        """ Returns the full name of this piece type. """
        return self.name.lower()

    @property
    def unicode_symbol(self, *, white: bool = True) -> str:
        """ Returns the unicode symbol for this piece type. """
        return UNICODE_PIECE_SYMBOLS[self.value.upper() if white else self.value]

    @property
    def chess_int(self) -> int:
        """ Returns the python-chess integer for this piece type. """
        return {
            PieceType.PAWN:   chess.PAWN,
            PieceType.KNIGHT: chess.KNIGHT,
            PieceType.BISHOP: chess.BISHOP,
            PieceType.ROOK:   chess.ROOK,
            PieceType.QUEEN:  chess.QUEEN,
            PieceType.KING:   chess.KING,
        }[self]

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"PieceType.{self.name}"

PIECE_SYMBOLS: dict[str, PieceType] = {piece.value: piece for piece in PieceType}

UNICODE_PIECE_SYMBOLS: dict[str, str] = {
    "R": "♖", "r": "♜",
    "N": "♘", "n": "♞",
    "B": "♗", "b": "♝",
    "Q": "♕", "q": "♛",
    "K": "♔", "k": "♚",
    "P": "♙", "p": "♟",
}

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

    SQUARE_BOARD_SIZE: int = DEFAULT_BOARD_SIZE
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

    def apply_action(self, action: chessai.core.action.Action) -> 'Square':
        """ Returns the Square that the action moves to. """

        start_square = action.get_start_square()
        if (self != start_square):
            raise ValueError(f"Actions applied must start from the same square: {action}")

        return action.get_end_square()

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

@dataclasses.dataclass
class Piece(edq.util.json.DictConverter):
    """ A piece with a type and color. """

    piece_type: PieceType
    """ The piece type. """

    color: Color
    """ The piece color. """

    def symbol(self) -> str:
        """
        Gets the symbol for the piece.
        Upper-case symbols are white pieces and lower-case symbols are black pieces.
        """

        symbol = self.piece_type.symbol
        return symbol.upper() if self.color else symbol

    def unicode_symbol(self, *, invert_color: bool = False) -> str:
        """ Gets the Unicode character for the piece. """
        symbol = self.symbol().swapcase() if invert_color else self.symbol()
        return UNICODE_PIECE_SYMBOLS[symbol]

    def __hash__(self) -> int:
        return hash((self.piece_type, self.color))

    def __repr__(self) -> str:
        return f"Piece.from_symbol({self.symbol()!r})"

    def __str__(self) -> str:
        return self.symbol()

    @classmethod
    def from_symbol(cls, symbol: str) -> Piece:
        """
        Creates Piece from a piece symbol.
        Raise a ValueError if the symbol is invalid.
        """
        return cls(PIECE_SYMBOLS[symbol.lower()], Color(symbol.isupper()))

    # def to_dict(self) -> dict[str, typing.Any]:
    #     return {
    #         'piece_type': self.piece_type,
    #         'color': self.color,
    #     }

    # @classmethod
    # def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
    #     return cls.from_pgn(data.get('pgn', ''))

# TODO(Lucas): Continue adding the necessary methods for students to interact with the board.
class Board(edq.util.json.DictConverter):
    """
    The board for all chess games in chessai.
    A board holds the current state and history of the game.

    Boards should only be interacted with via their methods and not their member variables.
    """

    def __init__(self,
                 source: str,
                 start_fen: str = chess.STARTING_FEN,
                 search_target: Square | dict[str, typing.Any] | None = None,
                 **kwargs: typing.Any) -> None:
        """
        Construct a board.
        The board must be a valid board given by the starting FEN.
        """

        self.source: str = source
        """ Where this board was loaded from. """

        self._board = chess.Board(start_fen)
        """ The current board which stores the current state and the history. """

        if (isinstance(search_target, dict)):
            search_target = Square.from_dict(search_target)

        self.search_target: Square | None = search_target  # type: ignore
        """ Some boards (especially knight's errant problems) will have a specific square search target. """

        self.num_files : int = DEFAULT_BOARD_SIZE
        """ The number of files of the chess board. """

        self.num_ranks: int = DEFAULT_BOARD_SIZE
        """ The number of ranks of the chess board. """

        # TODO(Lucas): May not be able to check if the board is valid with search problems.
        # if (not self.is_valid()):
        #     raise ValueError("Invalid board format: '{start_fen}'.")

    @property
    def files(self) -> int:
        """ The files (columns) of this square, in [0, 7]. a=0, h=7. """
        return self.num_files

    @property
    def ranks(self) -> int:
        """ The number of ranks (rows) of this board, in [0, 7]. Rank 1=0, Rank 8=7. """
        return self.num_ranks

    def is_valid(self) -> bool:
        """ Checks if the board is in a valid square. """
        return self._board.is_valid()

    def get_turn(self) -> bool:
        """ The side to move (chess.WHITE or chess.BLACK). """
        return self._board.turn

    def get_fullmove_number(self) -> int:
        """ Counts move pairs. Starts at 1 and is incremented after every move of the black side. """
        return self._board.fullmove_number

    def get_legal_moves(self) -> chess.LegalMoveGenerator:
        """ Returns a dynamic list of the legal moves. """
        return self._board.legal_moves

    def get_fen(self) -> str:
        """ Gets a FEN representation of the current board square. """
        return self._board.fen()

    def get_pieces(self,
                   piece_type: PieceType,
                   color: Color) -> chess.SquareSet:
        """ Gets the pieces of the given type and color. """
        return self._board.pieces(piece_type.chess_int, bool(color))

    def get_outcome(self) -> chess.Outcome | None:
        """ Gets the outcome of the game if it is over. """
        return self._board.outcome()

    def is_game_over(self) -> bool:
        """ Returns if the game is over. """
        return self._board.is_game_over()

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Returns if the move captures a piece. """
        return self._board.is_capture(action.get_move())

    def get_neighbors(self, start_square: Square) -> list[tuple[chessai.core.action.Action, Square]]:
        """
        Get squares that the piece at the given square can reach legally,
        and the action it would take to get there.

        Note that this is a high-throughput piece of code, and may contain optimizations.
        """

        neighbors: list[tuple[chessai.core.action.Action, Square]] = []

        attackers = self._board.attackers(self.get_turn(), start_square.to_chess_square())
        for square in attackers:
            end_square = Square.from_square(square)
            action = chessai.core.action.Action.from_squares(start_square, end_square)
            neighbors.append((action, end_square))

        return neighbors

    def _push(self, action: chessai.core.action.Action) -> None:
        """ Updates the square with the given move and puts it onto the move stack. """
        return self._board.push(action.get_move())

    def copy(self) -> 'Board':
        """ Create a deep copy of the board. """
        instance = self.__class__.__new__(self.__class__)
        instance._board = self._board.copy()
        return instance

    def to_pgn(self) -> str:
        """Serialize the board's game history to a PGN string."""
        game = chess.pgn.Game.from_board(self._board)
        exporter = chess.pgn.StringExporter()
        return game.accept(exporter)

    @classmethod
    def from_pgn(cls, pgn_string: str) -> 'Board':
        """ Reconstruct a Board from a PGN string, restoring the full move history. """
        instance = cls.__new__(cls)

        game = chess.pgn.read_game(io.StringIO(pgn_string))
        if (game is None):
            raise ValueError(f"Unable to read PGN of board: '{pgn_string}'.")

        # Replay the move history to get the current square.
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)

        instance._board = board
        return instance

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'pgn': self.to_pgn(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls.from_pgn(data.get('pgn', ''))

def is_valid_fen(fen: str) -> bool:
    """ Checks if a FEN is valid. """

    try:
        _ = chessai.core.board.Board('TEST', fen)
    except ValueError:
        return False

    return True

def load_path(path: str, **kwargs: typing.Any) -> Board:
    """
    Load a board from a file.
    If the given path does not exist,
    try to prefix the path with the standard board directory and suffix with the standard extension.
    """

    raw_path = path

    # If the path does not exist, try the boards directory.
    if (not os.path.exists(path)):
        path = os.path.join(BOARDS_DIR, path)

        # If this path does not have a good extension, add one.
        if (os.path.splitext(path)[-1] != FILE_EXTENSION):
            path = path + FILE_EXTENSION

    if (not os.path.exists(path)):
        raise ValueError(f"Could not find board, path does not exist: '{raw_path}'.")

    text = edq.util.dirent.read_file(path, strip = False)
    return load_string(raw_path, text, **kwargs)

def load_string(source: str, text: str, **kwargs: typing.Any) -> Board:
    """ Load a board from a string. """

    separator_index = -1
    lines = text.split("\n")

    for (i, line) in enumerate(lines):
        if (SEPARATOR_PATTERN.match(line)):
            separator_index = i
            break

    if (separator_index == -1):
        # No separator was found.
        options_text = ''
        board_text = "\n".join(lines)
    else:
        options_text = "\n".join(lines[:separator_index])
        board_text = "\n".join(lines[(separator_index + 1):])

    options_text = options_text.strip()
    if (len(options_text) == 0):
        options = {}
    else:
        options = edq.util.json.loads(options_text)

    options.update(kwargs)

    board_class = options.get('class', DEFAULT_BOARD_CLASS)
    return chessai.util.reflection.new_object(board_class, source, board_text, **options)  # type: ignore[no-any-return]
