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

class MoveRecord(edq.util.json.DictConverter):
    """
    A record of a move, containing everything needed to perfectly undo it.

    The captured_piece_coordinate is stored separately from action.end_coordinate
    because en-passant captures a pawn that is not on the destination square.
    """

    def __init__(self,
                 action: chessai.core.action.Action,
                 captured_piece: chessai.core.piece.Piece | None = None,
                 captured_piece_coordinate: 'chessai.core.coordinate.Coordinate | None' = None,
                 rook_action: 'chessai.core.action.Action | None' = None,
                 was_promotion: bool = False,
                 previous_castling_rights: 'chessai.core.castling.CastlingRights | None' = None,
                 previous_en_passant: 'chessai.core.coordinate.Coordinate | None' = None,
                 previous_halfmove_clock: int = 0) -> None:

        self.action: chessai.core.action.Action = action
        """ The action taken that caused this move record. """

        self.captured_piece: chessai.core.piece.Piece | None = captured_piece
        """ The piece that was captured, or None. """

        self.captured_piece_coordinate: chessai.core.coordinate.Coordinate | None = captured_piece_coordinate
        """
        Where the captured piece actually was.
        For normal captures this equals action.end_coordinate.
        For en-passant this is one rank behind the destination.
        """

        self.rook_action: chessai.core.action.Action | None = rook_action
        """ The rook's start/end coordinates during a castle, so pop() can reverse it. """

        self.was_promotion: bool = was_promotion
        """ If True, the piece at end_coordinate is a promoted piece and must be demoted back to a pawn on pop(). """

        # Metadata that the gamestate is responsible for managing.
        self.previous_castling_rights: chessai.core.castling.CastlingRights | None = previous_castling_rights
        self.previous_en_passant: chessai.core.coordinate.Coordinate | None = previous_en_passant
        self.previous_halfmove_clock: int = previous_halfmove_clock

    def to_dict(self) -> dict:
        return {
            'action': self.action.to_dict(),
            'captured_piece': self.captured_piece.to_dict() if self.captured_piece else None,
            'captured_piece_coordinate': self.captured_piece_coordinate.to_dict() if self.captured_piece_coordinate else None,
            'rook_action': self.rook_action.to_dict() if self.rook_action else None,
            'was_promotion': self.was_promotion,
            'previous_castling_rights': self.previous_castling_rights.to_dict() if self.previous_castling_rights else None,
            'previous_en_passant': self.previous_en_passant.to_dict() if self.previous_en_passant else None,
            'previous_halfmove_clock': self.previous_halfmove_clock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MoveRecord':
        captured_piece = data.get('captured_piece', None)
        if (captured_piece is not None):
            captured_piece = chessai.core.piece.Piece.from_dict(captured_piece)

        captured_piece_coordinate = data.get('captured_piece_coordinate', None)
        if (captured_piece_coordinate is not None):
            captured_piece_coordinate = chessai.core.coordinate.Coordinate.from_dict(captured_piece_coordinate)

        rook_action = data.get('rook_action', None)
        if (rook_action is not None):
            rook_action = chessai.core.action.Action.from_dict(rook_action)

        previous_castling_rights = data.get('previous_castling_rights', None)
        if (previous_castling_rights is not None):
            previous_castling_rights = chessai.core.action.Action.from_dict(previous_castling_rights)

        previous_en_passant = data.get('previous_en_passant', None)
        if (previous_en_passant is not None):
            previous_en_passant = chessai.core.action.Action.from_dict(previous_en_passant)

        return cls(
            action                    = chessai.core.action.Action.from_dict(data['action']),
            captured_piece            = captured_piece,
            captured_piece_coordinate = captured_piece_coordinate,
            rook_action               = rook_action,
            was_promotion             = data.get('was_promotion', False),
            previous_castling_rights  = previous_castling_rights,
            previous_en_passant       = previous_en_passant,
            previous_halfmove_clock   = data.get('previous_halfmove_clock', 0),
        )

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

    def push(self, action: chessai.core.action.Action) -> MoveRecord:
        """
        Apply an action to the board and return a MoveRecord sufficient to undo it.

        Handles three special cases:
        - Castling:    also moves the rook.
        - En-passant:  removes the captured pawn from its actual square.
        - Promotion:   replaces the pawn with the promoted piece type.

        The GameState is responsible for detecting these cases by inspecting the
        returned MoveRecord and updating its own metadata (castling rights,
        en-passant coordinate, clocks) before appending the record to the stack.
        """

        piece = self.pieces.get(action.start_coordinate)
        if (piece is None):
            raise ValueError(f"There is no piece at the action's start coordinate: '{action.start_coordinate.uci()}'.")

        # Detect special move types before mutating anything.
        is_castling = (
            (piece.piece_type == chessai.core.types.PieceType.KING)
            and (action.start_coordinate.file_distance(action.end_coordinate) > 1)
        )

        # En-passant: a pawn moves diagonally to an empty square.
        is_en_passant = (
            (piece.piece_type == chessai.core.types.PieceType.PAWN)
            and (action.start_coordinate.file_distance(action.end_coordinate) == 1)
            and (self.get(action.end_coordinate) is None)
        )

        # Build the rook action for castling.
        rook_action: chessai.core.action.Action | None = None

        if (is_castling):
            back_rank = action.start_coordinate.rank

            if (action.end_coordinate.file > action.start_coordinate.file):
                # Kingside: rook moves from the h-file to just right of the king's destination.
                rook_start = chessai.core.coordinate.Coordinate(self.num_files - 1, back_rank)
                rook_end   = chessai.core.coordinate.Coordinate(action.end_coordinate.file - 1, back_rank)
            else:
                # Queenside: rook moves from the a-file to just left of the king's destination.
                rook_start = chessai.core.coordinate.Coordinate(0, back_rank)
                rook_end   = chessai.core.coordinate.Coordinate(action.end_coordinate.file + 1, back_rank)

            rook_action = chessai.core.action.Action(rook_start, rook_end)

        # Identify the captured piece and where it actually sits.
        captured_piece_coordinate: chessai.core.coordinate.Coordinate | None = None
        captured_piece: chessai.core.piece.Piece | None = None

        if (is_en_passant):
            # The captured pawn is on the same rank as the moving pawn, on the destination file.
            captured_piece_coordinate = chessai.core.coordinate.Coordinate(
                action.end_coordinate.file,
                action.start_coordinate.rank,
            )

            captured_piece = self.pieces.get(captured_piece_coordinate)
        elif (self.get(action.end_coordinate) is not None):
            captured_piece_coordinate = action.end_coordinate
            captured_piece = self.get(action.end_coordinate)

        # Move the king.
        self.pieces.pop(action.start_coordinate)
        self.pieces[action.end_coordinate] = piece

        # Handle promotion by replacing the pawn with the promoted piece.
        if (action.promotion is not None):
            self.pieces[action.end_coordinate] = chessai.core.piece.Piece(action.promotion, piece.color)

        # Move the rook for castling.
        if (rook_action is not None):
            rook = self.pieces.pop(rook_action.start_coordinate, None)
            if (rook is not None):
                self.pieces[rook_action.end_coordinate] = rook

        # Remove the en-passant captured pawn from its actual square.
        if (is_en_passant and captured_piece_coordinate is not None):
            self.pieces.pop(captured_piece_coordinate, None)

        return MoveRecord(
            action                    = action,
            captured_piece            = captured_piece,
            captured_piece_coordinate = captured_piece_coordinate,
            rook_action               = rook_action,
            was_promotion             = (action.promotion is not None),
        )

    def pop(self, record: MoveRecord) -> None:
        """
        Undo the board mutation described by record.
        Must be called with records in LIFO order.
        """

        action = record.action

        # Retrieve the piece from where the action ended.
        # For promotions this will be the promoted piece, so we need to restore the pawn.
        piece = self.pieces.pop(action.end_coordinate, None)
        if (piece is None):
            raise ValueError(f"Cannot pop: no piece at end coordinate '{action.end_coordinate.uci()}'.")

        # Restore the original pawn if this was a promotion.
        if (record.was_promotion):
            piece = chessai.core.piece.Piece(chessai.core.types.PieceType.PAWN, piece.color)

        # Restore the moving piece to its origin.
        self.pieces[action.start_coordinate] = piece

        # Restore the captured piece to where it actually was.
        if (record.captured_piece is not None and record.captured_piece_coordinate is not None):
            self.pieces[record.captured_piece_coordinate] = record.captured_piece

        # Undo the rook move for castling.
        if (record.rook_action is not None):
            rook = self.pieces.pop(record.rook_action.end_coordinate, None)
            if (rook is not None):
                self.pieces[record.rook_action.start_coordinate] = rook

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
