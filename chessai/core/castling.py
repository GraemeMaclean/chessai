import typing

import edq.util.json

class CastlingRights(edq.util.json.DictConverter):
    """
    Tracks which castling moves are still available.

    In standard chess, each side starts with both kingside and queenside
    castling available, and rights are lost permanently when the king or
    the relevant rook moves (or is captured).
    """

    def __init__(self,
            white_kingside: bool = True,
            white_queenside: bool = True,
            black_kingside: bool = True,
            black_queenside: bool = True,
            ) -> None:
        self.white_kingside: bool = white_kingside
        self.white_queenside: bool = white_queenside
        self.black_kingside: bool = black_kingside
        self.black_queenside: bool = black_queenside

    def none(self) -> bool:
        """ Return True if no castling rights remain. """
        return not (
            self.white_kingside
            or self.white_queenside
            or self.black_kingside
            or self.black_queenside
        )

    def to_fen_string(self) -> str:
        """
        Encode castling rights as a FEN castling field.
        Returns '-' if no rights remain.
        """

        result = ''
        if (self.white_kingside):
            result += 'K'

        if (self.white_queenside):
            result += 'Q'

        if (self.black_kingside):
            result += 'k'

        if (self.black_queenside):
            result += 'q'

        if (len(result) == 0):
            return '-'

        return result

    @classmethod
    def from_fen_string(cls, fen_field: str) -> 'CastlingRights':
        """
        Parse the castling field of a FEN string.

        Args:
            fen_field: The castling portion of a FEN string, e.g. 'KQkq' or '-'.
        """

        if (fen_field == '-'):
            return cls(False, False, False, False)

        return cls(
            white_kingside  = ('K' in fen_field),
            white_queenside = ('Q' in fen_field),
            black_kingside  = ('k' in fen_field),
            black_queenside = ('q' in fen_field),
        )

    def copy(self) -> 'CastlingRights':
        """ Get a deep copy of these castline rights. """

        return CastlingRights(
            self.white_kingside,
            self.white_queenside,
            self.black_kingside,
            self.black_queenside,
        )

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, CastlingRights)):
            return False
        return (
            self.white_kingside  == other.white_kingside
            and self.white_queenside == other.white_queenside
            and self.black_kingside  == other.black_kingside
            and self.black_queenside == other.black_queenside
        )

    def __repr__(self) -> str:
        return f"CastlingRights({self.to_fen_string()}.)"

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'white_kingside':  self.white_kingside,
            'white_queenside': self.white_queenside,
            'black_kingside':  self.black_kingside,
            'black_queenside': self.black_queenside,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> 'CastlingRights':
        return cls(
            white_kingside  = data.get('white_kingside',  True),
            white_queenside = data.get('white_queenside', True),
            black_kingside  = data.get('black_kingside',  True),
            black_queenside = data.get('black_queenside', True),
        )
