import copy
import os
import re
import typing

import edq.util.json

import chessai.core.action
import chessai.core.castling
import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types
import chessai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'boards')

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')

FILE_EXTENSION = '.board'

DEFAULT_BOARD_CLASS: str = 'chessai.core.board.Board'

DEFAULT_BOARD_FILES: int = 8
DEFAULT_BOARD_RANKS: int = 8

DEFAULT_BOARD_SIZE: int = DEFAULT_BOARD_RANKS * DEFAULT_BOARD_FILES

# TODO(Lucas): Continue adding the necessary methods for students to interact with the board.
class Board(edq.util.json.DictConverter):
    """ The board holds the current coordinates of pieces on the board. """

    def __init__(self,
            pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] | None = None,
            num_files: int = DEFAULT_BOARD_FILES,
            num_ranks: int = DEFAULT_BOARD_RANKS,
            **kwargs: typing.Any) -> None:
        """
        Construct a board with the given dimensions and pieces.
        """

        if (pieces is None):
            pieces = {}

        self.pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] = pieces
        """ The pieces on the board, keyed by the coordinate they occupy. """

        self.num_files: int = num_files
        """ The number of files of the chess board. """

        self.num_ranks: int = num_ranks
        """ The number of ranks of the chess board. """

        if (not self.is_valid()):
            raise ValueError('Cannot construct an invalid board:'
                + f" files '{self.num_files}', ranks '{self.num_ranks}',"
                + f" pieces '{self.pieces}'.")

    def is_valid(self) -> bool:
        """ Checks if all of the pieces are in a valid position. """

        for (coordinate, _) in self.pieces.items():
            if (not self._is_within_bounds(coordinate)):
                return False

        return True

    def get(self, coordinate: chessai.core.coordinate.Coordinate) -> chessai.core.piece.Piece | None:
        """ Gets the piece at the given coordinate. """

        return self.pieces.get(coordinate, None)

    def has_piece(self, coordinate: chessai.core.coordinate.Coordinate) -> bool:
        """ Returns if the given coordinate has a piece. """

        return (self.get(coordinate) is not None)

    def all_pieces(self) -> list[chessai.core.piece.Piece]:
        """ Gets all of the pieces on the board. """

        return list(self.pieces.values())

    def all_coordinates(self) -> list[chessai.core.coordinate.Coordinate]:
        """ Gets all of the coordinates with a piece on the board. """

        return list(self.pieces.keys())

    def push(self, action: chessai.core.action.Action) -> bool:
        """ Apply an action to the board. """

        piece = self.pieces.pop(action.start_coordinate, None)
        if (piece is None):
            raise ValueError(f"There is no piece at the action's start coordinate: '{action.start_coordinate.uci()}'.")

        # Convert to the promotion piece.
        if (action.promotion is not None):
            piece = action.promotion

        if (not self._is_within_bounds(action.end_coordinate)):
            raise ValueError(f"Cannot push an action that moves the piece off of the board of size '{self.num_files}x{self.num_ranks}': '{action.end_coordinate}'.")

        target_piece = self.pieces.get(action.end_coordinate, None)

        self.pieces[action.end_coordinate] = piece

        return (target_piece is not None)

    def remove(self, coordinate: chessai.core.coordinate.Coordinate) -> None:
        """
        Remove the piece from the given coordinate.
        If there is no piece at the coordinate, the board is unchanged.
        """

        self.pieces.pop(coordinate, None)

    def set(self, piece: chessai.core.piece.Piece, coordinate: chessai.core.coordinate.Coordinate) -> None:
        """ Adds a piece to the specified coordinate, which must be within bounds. """

        if (not self._is_within_bounds(coordinate)):
            raise ValueError(f"Cannot remove a piece from an out of bounds coordinate on a board of size '{self.num_files}x{self.num_ranks}': '{coordinate}'.")

        self.pieces[coordinate] = piece

    def _is_within_bounds(self, coordinate) -> bool:
        """ Checks whether a coordinate is within the bounds of the board. """

        if ((coordinate.file < 0) or (coordinate.file >= self.num_files)):
            return False

        if ((coordinate.rank < 0) or (coordinate.rank >= self.num_ranks)):
            return False

        return True

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Returns if the move captures a piece. """

        if (self.get(action.start_coordinate) is None):
            raise ValueError(f"Action has a start coordinate that does not have a piece on the board: '{action.start_coordinate.uci()}'.")

        return (self.get(action.end_coordinate) is not None)

    def copy(self) -> 'Board':
        """ Create a deep copy of the board. """

        return copy.deepcopy(self)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'pieces': self.pieces,
            'num_files': self.num_files,
            'num_ranks': self.num_ranks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(**data)

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
    return load_string(text, **kwargs)

def load_string(text: str, **kwargs: typing.Any) -> Board:
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
    return chessai.util.reflection.new_object(board_class, board_text, **options)  # type: ignore[no-any-return]
