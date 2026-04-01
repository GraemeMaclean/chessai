import dataclasses

import edq.util.json

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
        return symbol.upper() if self.color else symbol

    def unicode_symbol(self, *, invert_color: bool = False) -> str:
        """ Gets the Unicode character for the piece. """
        symbol = self.symbol().swapcase() if invert_color else self.symbol()
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

    # def to_dict(self) -> dict[str, typing.Any]:
    #     return {
    #         'piece_type': self.piece_type,
    #         'color': self.color,
    #     }

    # @classmethod
    # def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
    #     return cls.from_pgn(data.get('pgn', ''))
