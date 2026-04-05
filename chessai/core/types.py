import enum

import chess

DEFAULT_BOARD_SIZE: int = 8

class Color(int, enum.Enum):
    """ An enum representing the side to move or the color of a piece. """
    BLACK = 0
    WHITE = 1

    @property
    def symbol(self) -> str:
        """ Retruns 'w' for white and 'b' for black. """

        return 'w' if (self == Color.WHITE) else 'b'

    def opposite(self) -> 'Color':
        """ Returns the opposing color. """

        return Color.BLACK if (self == Color.WHITE) else Color.WHITE

    def __str__(self) -> str:
        return self.name.lower()  # "white" or "black"

    def __repr__(self) -> str:
        return f"Color.{self.name}"

    def __bool__(self) -> bool:
        return bool(self.value)

class TerminationReason(enum.Enum):
    """ An enum representing the reason for a game to be over. """

    CHECKMATE = enum.auto()
    """ See chessai.core.board.Board.is_checkmate(). """

    STALEMATE = enum.auto()
    """ See chessai.core.board.Board.is_stalemate(). """

    INSUFFICIENT_MATERIAL = enum.auto()
    """ See chessai.core.board.Board.is_stalemate(). """

    SEVENTYFIVE_MOVES = enum.auto()
    """ See chessai.core.board.Board.is_fivefold_repition(). """

    FIFTY_MOVES = enum.auto()
    """ See chessai.core.board.Board.can_claim_fifty_moves()`. """

    THREEFOLD_REPETITION = enum.auto()
    """ See chessai.core.board.Board.can_claim_threefold_repetition()`. """

    VARIANT_WIN = enum.auto()
    """ See chessai.core.board.Board.is_variant_win()`. """

    VARIANT_LOSS = enum.auto()
    """ See chessai.core.board.Board.is_variant_loss()`. """

    VARIANT_DRAW = enum.auto()
    """ See chessai.core.board.Board.is_variant_draw()`. """

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

    def unicode_symbol(self, team: Color = Color.WHITE) -> str:
        """ Returns the unicode symbol for this piece type. """

        return UNICODE_PIECE_SYMBOLS[self.value.upper() if (team == Color.WHITE) else self.value]

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
