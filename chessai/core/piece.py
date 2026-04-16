import abc
import dataclasses
import enum

import edq.util.json

import chessai.core.coordinate
import chessai.core.types

@dataclasses.dataclass
class Piece(edq.util.json.DictConverter):
    """ A piece with a type and color. """

    piece_type: chessai.core.types.PieceType
    """ The piece type. """

    color: chessai.core.types.Color
    """ The piece color. """

    def symbol(self) -> str:
        """
        Gets the symbol for the piece.
        Upper-case symbols are white pieces and lower-case symbols are black pieces.
        """

        symbol = self.piece_type.symbol

        if (self.color == chessai.core.types.Color.WHITE):
            return symbol.upper()
        else:
            return symbol.lower()

    def unicode_symbol(self, *, invert_color: bool = False) -> str:
        """ Gets the Unicode character for the piece. """

        if invert_color:
            symbol = self.symbol().swapcase()
        else:
            symbol = self.symbol()

        return chessai.core.types.UNICODE_PIECE_SYMBOLS[symbol]

    def __hash__(self) -> int:
        return hash((self.piece_type, self.color))

    def __repr__(self) -> str:
        return f"Piece.from_symbol({self.symbol()!r})"

    def __str__(self) -> str:
        return self.symbol()

    @classmethod
    def from_symbol(cls, symbol: str) -> 'Piece':
        """
        Creates Piece from a piece symbol.
        Raise a ValueError if the symbol is invalid.
        """

        return cls(chessai.core.types.PIECE_SYMBOLS[symbol.lower()], chessai.core.types.Color(symbol.isupper()))

class MoveKind(enum.Enum):
    """ An enum to encode the types of movement. """
    
    NORMAL  = enum.auto()
    """ Standard move, capable of capture and movement. """

    CAPTURE = enum.auto()
    """ Movement that can only be done if it captures a piece. """

    PUSH    = enum.auto()
    """ Movement that can only be used to move, not capture. """

@dataclasses.dataclass(frozen = True)
class MoveVector:
    """
    A movement rule for a piece.
    If slides is True, then the vector can be repeated until the piece captures or the end of the board.
    """

    file_delta: int
    """ The direction of the movement on the file. """

    rank_delta: int
    """ The direction of the movement on the rank. """

    slides: bool = False
    """ Whether the vector can be repeated until a capture or the end of the board. """

    kind: MoveKind = MoveKind.NORMAL
    """ Determines if the movement is used for movement, capture, or both. """

class PieceMover(abc.ABC):
    """
    Defines the movement rules for a piece type in terms of the directions of the movement and if it slides.
    The movement is game agnostic, so it does not define if the movement is legal.
    """

    @abc.abstractmethod
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        """ Returns the movement vectors for this piece. """

class KingMover(PieceMover):
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        return [
            MoveVector( 1,  0),
            MoveVector( 1,  1),
            MoveVector( 1, -1),
            MoveVector(-1,  0),
            MoveVector(-1,  1),
            MoveVector(-1, -1),
            MoveVector( 0,  1),
            MoveVector( 0, -1),
        ]

class QueenMover(PieceMover):
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        return [
            MoveVector( 1,  0, slides = True),
            MoveVector( 1,  1, slides = True),
            MoveVector( 1, -1, slides = True),
            MoveVector(-1,  0, slides = True),
            MoveVector(-1,  1, slides = True),
            MoveVector(-1, -1, slides = True),
            MoveVector( 0,  1, slides = True),
            MoveVector( 0, -1, slides = True),
        ]

class RookMover(PieceMover):
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        return [
            MoveVector( 1,  0, slides = True),
            MoveVector(-1,  0, slides = True),
            MoveVector( 0,  1, slides = True),
            MoveVector( 0, -1, slides = True),
        ]

class BishopMover(PieceMover):
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        return [
            MoveVector( 1,  1, slides = True),
            MoveVector(-1,  1, slides = True),
            MoveVector( 1, -1, slides = True),
            MoveVector(-1, -1, slides = True),
        ]

class KnightMover(PieceMover):
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        return [
            MoveVector( 2,  1),
            MoveVector( 2, -1),
            MoveVector(-2,  1),
            MoveVector(-2, -1),
            MoveVector( 1,  2),
            MoveVector( 1, -2),
            MoveVector(-1,  2),
            MoveVector(-1, -2),
        ]

class PawnMover(PieceMover):
    def move_vectors(self, color: chessai.core.types.Color, origin: chessai.core.coordinate.Coordinate) -> list[MoveVector]:
        if (color == chessai.core.types.Color.WHITE):
            direction = 1
        else:
            direction = -1

        return [
            MoveVector(0,  direction, kind = MoveKind.PUSH),
            MoveVector(1,  direction, kind = MoveKind.CAPTURE),
            MoveVector(-1, direction, kind = MoveKind.CAPTURE),
        ]

_MOVEMENT_REGISTRY: dict[chessai.core.types.PieceType, PieceMover] = {
    chessai.core.types.PieceType.KING:   KingMover(),
    chessai.core.types.PieceType.QUEEN:  QueenMover(),
    chessai.core.types.PieceType.ROOK:   RookMover(),
    chessai.core.types.PieceType.BISHOP: BishopMover(),
    chessai.core.types.PieceType.KNIGHT: KnightMover(),
    chessai.core.types.PieceType.PAWN:   PawnMover(),
}

def get_mover(piece_type: chessai.core.types.PieceType) -> PieceMover:
    """ Get the piece movement rules of a piece. """

    mover = _MOVEMENT_REGISTRY.get(piece_type, None)
    if (mover is None):
        raise KeyError(f"No mover registered for piece type: '{piece_type}'.")

    return mover

def register_mover(piece_type: chessai.core.types.PieceType, mover: PieceMover) -> None:
    """ Register a custom piece type's movement rules. """

    _MOVEMENT_REGISTRY[piece_type] = mover
