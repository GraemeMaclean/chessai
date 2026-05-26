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

        clean_pieces: dict[int, dict[int, chessai.core.piece.Piece]] = {file: {} for file in range(num_files)}

        for (coordinate, piece) in pieces.items():
            if (coordinate.rank not in clean_pieces):
                raise ValueError('Cannot place a piece that is out of bounds:'
                                 + f" files '{num_files}', ranks '{num_ranks}',"
                                 + f" rank: '{coordinate.rank}'.")

            clean_pieces[coordinate.file][coordinate.rank] = piece

        self.pieces: dict[int, dict[int, chessai.core.piece.Piece]] = clean_pieces
        """ The pieces on the board, first keyed by the file and then by the rank. """

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

        for file in range(self.num_files):
            for rank in self.pieces[file].keys():
                if (not self.is_within_bounds(file, rank)):
                    return False

        return True

    def get(self, file: int, rank: int) -> chessai.core.piece.Piece | None:
        """ Gets the piece at the given file and rank pair. """

        if (file not in self.pieces):
            return None

        return self.pieces[file].get(rank, None)

    def get_coordinate_map(self) -> dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece]:
        """ Gets all pieces on the board in a dictionary of coordinates to pieces. """

        piece_items: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] = {}

        for file in self.pieces.keys():
            for (rank, piece) in self.pieces[file].items():
                piece_items[chessai.core.coordinate.Coordinate(file, rank)] = piece

        return piece_items

    def has_piece(self, coordinate: chessai.core.coordinate.Coordinate) -> bool:
        """ Returns if the given coordinate has a piece. """

        return (self.pieces[coordinate.file].get(coordinate.rank, None) is not None)

    def all_pieces(self) -> list[chessai.core.piece.Piece]:
        """ Gets all of the pieces on the board. """

        pieces: list[chessai.core.piece.Piece] = []

        for file in self.pieces.keys():
            for piece in self.pieces[file].values():
                pieces.append(piece)

        return pieces

    def all_coordinates(self) -> list[chessai.core.coordinate.Coordinate]:
        """ Gets all of the coordinates with a piece on the board. """

        coordinates: list[chessai.core.coordinate.Coordinate] = []

        for file in self.pieces.keys():
            for rank in self.pieces[file].keys():
                coordinates.append(chessai.core.coordinate.Coordinate(file, rank))

        return coordinates

    def push(self, action: chessai.core.action.MoveAction) -> bool:
        """
        Apply an action to the board.
        Returns whether the action captured a piece.
        """

        piece = self.pieces[action.start_coordinate.file].pop(action.start_coordinate.rank, None)
        if (piece is None):
            raise ValueError(f"There is no piece at the action's start coordinate: '{action.start_coordinate.uci()}'.")

        # Convert to the promotion piece.
        if (isinstance(action, chessai.core.action.PromotionAction) and (action.promotion is not None)):
            piece = action.promotion

        if (not self.is_within_bounds(action.end_coordinate.file, action.end_coordinate.rank)):
            raise ValueError("Cannot push an action that moves the piece off of the board of size"
                + f" '{self.num_files}x{self.num_ranks}': '{action.end_coordinate}'.")

        target_piece = self.pieces[action.end_coordinate.file].get(action.end_coordinate.rank, None)

        self.pieces[action.end_coordinate.file][action.end_coordinate.rank] = piece

        return (target_piece is not None)

    def remove(self, coordinate: chessai.core.coordinate.Coordinate) -> None:
        """
        Remove the piece from the given coordinate.
        If there is no piece at the coordinate, the board is unchanged.
        """

        self.pieces[coordinate.file].pop(coordinate.rank, None)

    def set(self, piece: chessai.core.piece.Piece, coordinate: chessai.core.coordinate.Coordinate) -> None:
        """ Adds a piece to the specified coordinate, which must be within bounds. """

        if (not self.is_within_bounds(coordinate.file, coordinate.rank)):
            raise ValueError("Cannot remove a piece from an out of bounds coordinate on a board of size"
                + f" '{self.num_files}x{self.num_ranks}': '{coordinate}'.")

        self.pieces[coordinate.file][coordinate.rank] = piece

    def is_within_bounds(self, file: int, rank: int) -> bool:
        """ Checks whether the given file and rank are within the bounds of the board. """

        if ((file < 0) or (file >= self.num_files)):
            return False

        if ((rank < 0) or (rank >= self.num_ranks)):
            return False

        return True

    def is_capture(self, action: chessai.core.action.MoveAction) -> bool:
        """ Returns if the move captures a piece. """

        return (self.get(action.end_coordinate.file, action.end_coordinate.rank) is not None)

    def to_fen_piece_field(self) -> str:
        """ Convert the board into the piece-placement field of a FEN string. """

        ranks: list[str] = []

        for rank_index in range(self.num_ranks):
            # FEN ranks come from highest first, so we descend from (num_ranks - 1) to rank 0.
            rank = (self.num_ranks - 1) - rank_index
            empty_count = 0

            for file in range(self.num_files):
                piece = self.pieces[file].get(rank, None)

                if (piece is None):
                    empty_count += 1
                else:
                    if (empty_count > 0):
                        ranks.append(str(empty_count))
                        empty_count = 0

                    symbol = piece.symbol()
                    if (symbol is None):
                        raise ValueError(f"Cannot serialize piece '{piece}' at rank '{rank}' and file '{file}'.")

                    ranks.append(symbol)

            if (empty_count > 0):
                ranks.append(str(empty_count))

            # Add rank separator except after last rank.
            if (rank_index < (self.num_ranks - 1)):
                ranks.append('/')

        return ''.join(ranks)

    def copy(self) -> 'Board':
        """ Create a deep copy of the board. """

        new_board = copy.copy(self)

        new_board.pieces = {file: ranks.copy() for file, ranks in self.pieces.items()}

        return new_board

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'pieces': self.pieces,
            'num_files': self.num_files,
            'num_ranks': self.num_ranks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(**data)
