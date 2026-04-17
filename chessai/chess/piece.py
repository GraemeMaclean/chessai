import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

UNICODE_PIECE_SYMBOLS: dict[str, str] = {
    "R": "♖", "r": "♜",
    "N": "♘", "n": "♞",
    "B": "♗", "b": "♝",
    "Q": "♕", "q": "♛",
    "K": "♔", "k": "♚",
    "P": "♙", "p": "♟",
}

class King(chessai.core.piece.Piece):
    """ The King in chess. """

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'K'

        return 'k'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self, origin: chessai.core.coordinate.Coordinate) -> list[chessai.core.piece.MoveVector]:
        return [
            chessai.core.piece.MoveVector( 1,  0),
            chessai.core.piece.MoveVector( 1,  1),
            chessai.core.piece.MoveVector( 1, -1),
            chessai.core.piece.MoveVector(-1,  0),
            chessai.core.piece.MoveVector(-1,  1),
            chessai.core.piece.MoveVector(-1, -1),
            chessai.core.piece.MoveVector( 0,  1),
            chessai.core.piece.MoveVector( 0, -1),
        ]

class Queen(chessai.core.piece.Piece):
    """ The Queen in chess. """

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'Q'

        return 'q'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self, origin: chessai.core.coordinate.Coordinate) -> list[chessai.core.piece.MoveVector]:
        return [
            chessai.core.piece.MoveVector( 1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector( 1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 1, -1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1, -1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0, -1, num_repetitions = -1),
        ]

class Rook(chessai.core.piece.Piece):
    """ The Rook in chess. """

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'R'

        return 'r'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self, origin: chessai.core.coordinate.Coordinate) -> list[chessai.core.piece.MoveVector]:
        return [
            chessai.core.piece.MoveVector( 1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  0, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 0, -1, num_repetitions = -1),
        ]

class Bishop(chessai.core.piece.Piece):
    """ The Bishop in chess. """

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'B'

        return 'b'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self, origin: chessai.core.coordinate.Coordinate) -> list[chessai.core.piece.MoveVector]:
        return [
            chessai.core.piece.MoveVector( 1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1,  1, num_repetitions = -1),
            chessai.core.piece.MoveVector( 1, -1, num_repetitions = -1),
            chessai.core.piece.MoveVector(-1, -1, num_repetitions = -1),
        ]

class Knight(chessai.core.piece.Piece):
    """ The Knight in chess. """

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'K'

        return 'k'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self, origin: chessai.core.coordinate.Coordinate) -> list[chessai.core.piece.MoveVector]:
        return [
            chessai.core.piece.MoveVector( 2,  1),
            chessai.core.piece.MoveVector( 2, -1),
            chessai.core.piece.MoveVector(-2,  1),
            chessai.core.piece.MoveVector(-2, -1),
            chessai.core.piece.MoveVector( 1,  2),
            chessai.core.piece.MoveVector( 1, -2),
            chessai.core.piece.MoveVector(-1,  2),
            chessai.core.piece.MoveVector(-1, -2),
        ]

class Pawn(chessai.core.piece.Piece):
    """ The Pawn in chess. """

    def symbol(self) -> str:
        if (self.color == chessai.core.types.Color.WHITE):
            return 'P'

        return 'p'

    def unicode_symbol(self) -> str:
        return UNICODE_PIECE_SYMBOLS[self.symbol()]

    def move_vectors(self, origin: chessai.core.coordinate.Coordinate) -> list[chessai.core.piece.MoveVector]:
        if (self.color == chessai.core.types.Color.WHITE):
            direction = 1
        else:
            direction = -1

        return [
            chessai.core.piece.MoveVector(0,  direction, kind = chessai.core.piece.MoveKind.PUSH),
            chessai.core.piece.MoveVector(1,  direction, kind = chessai.core.piece.MoveKind.CAPTURE),
            chessai.core.piece.MoveVector(-1, direction, kind = chessai.core.piece.MoveKind.CAPTURE),
        ]
