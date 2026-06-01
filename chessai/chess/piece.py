import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

UNICODE_PIECE_SYMBOLS: dict[str, str] = {
    "r": "♖", "R": "♜",
    "n": "♘", "N": "♞",
    "b": "♗", "B": "♝",
    "q": "♕", "Q": "♛",
    "k": "♔", "K": "♚",
    "p": "♙", "P": "♟",
}

class King(chessai.core.piece.Piece, symbols = ('K', 'k')):
    """ The King in chess. """

    _move_vectors: list[chessai.core.piece.MoveVector] = [
            chessai.core.piece.MoveVector( 1,  0),
            chessai.core.piece.MoveVector( 1,  1),
            chessai.core.piece.MoveVector( 1, -1),
            chessai.core.piece.MoveVector(-1,  0),
            chessai.core.piece.MoveVector(-1,  1),
            chessai.core.piece.MoveVector(-1, -1),
            chessai.core.piece.MoveVector( 0,  1),
            chessai.core.piece.MoveVector( 0, -1),
        ]

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'K'

        return 'k'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors

class Queen(chessai.core.piece.Piece, symbols = ('Q', 'q')):
    """ The Queen in chess. """

    _move_vectors: list[chessai.core.piece.MoveVector] = [
            chessai.core.piece.MoveVector( 1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector( 1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 1, -1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1, -1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0, -1, num_repetitions = -1),
        ]

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'Q'

        return 'q'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors

class Rook(chessai.core.piece.Piece, symbols = ('R', 'r')):
    """ The Rook in chess. """

    _move_vectors: list[chessai.core.piece.MoveVector] = [
            chessai.core.piece.MoveVector( 1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0, -1, num_repetitions = -1),
        ]

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'R'

        return 'r'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors

class Bishop(chessai.core.piece.Piece, symbols = ('B', 'b')):
    """ The Bishop in chess. """

    _move_vectors: list[chessai.core.piece.MoveVector] = [
            chessai.core.piece.MoveVector( 1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 1, -1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1, -1, num_repetitions = -1),
        ]

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'B'

        return 'b'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors

class Knight(chessai.core.piece.Piece, symbols = ('N', 'n')):
    """ The Knight in chess. """

    _move_vectors: list[chessai.core.piece.MoveVector] = [
            chessai.core.piece.MoveVector( 2,  1),
            chessai.core.piece.MoveVector( 2, -1),
            chessai.core.piece.MoveVector(-2,  1),
            chessai.core.piece.MoveVector(-2, -1),
            chessai.core.piece.MoveVector( 1,  2),
            chessai.core.piece.MoveVector( 1, -2),
            chessai.core.piece.MoveVector(-1,  2),
            chessai.core.piece.MoveVector(-1, -2),
        ]

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'N'

        return 'n'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors

class Pawn(chessai.core.piece.Piece, symbols = ('P', 'p')):
    """ The Pawn in chess. """

    _move_vectors: dict[chessai.core.types.Color, list[chessai.core.piece.MoveVector]] = {
        chessai.core.types.Color.WHITE: [
            chessai.core.piece.MoveVector( 0,  1, kind = chessai.core.piece.MoveKind.PUSH),
            chessai.core.piece.MoveVector( 1,  1, kind = chessai.core.piece.MoveKind.CAPTURE),
            chessai.core.piece.MoveVector(-1,  1, kind = chessai.core.piece.MoveKind.CAPTURE),
        ],
        chessai.core.types.Color.BLACK: [
            chessai.core.piece.MoveVector( 0, -1, kind = chessai.core.piece.MoveKind.PUSH),
            chessai.core.piece.MoveVector( 1, -1, kind = chessai.core.piece.MoveKind.CAPTURE),
            chessai.core.piece.MoveVector(-1, -1, kind = chessai.core.piece.MoveKind.CAPTURE),
        ],
    }

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'P'

        return 'p'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self) -> list[chessai.core.piece.MoveVector]:
        return self._move_vectors[self.color]
