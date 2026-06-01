class CastlingRights(int):
    """
    Tracks which castling moves are still available, encoded as a 4-bit integer.

    In standard chess, each side starts with both kingside and queenside castling available,
    and rights are lost permanently when the king or the relevant rook moves (or is captured).
    """

    WHITE_KINGSIDE  = 0b0001
    WHITE_QUEENSIDE = 0b0010
    BLACK_KINGSIDE  = 0b0100
    BLACK_QUEENSIDE = 0b1000

    ALL  = 0b1111
    NONE = 0b0000

    def __new__(cls, value: int = 0b1111) -> 'CastlingRights':
        return super().__new__(cls, value & cls.ALL)

    @property
    def white_kingside(self) -> bool:
        """ Returns if white can castle on kingside. """

        return bool(self & self.WHITE_KINGSIDE)

    @property
    def white_queenside(self) -> bool:
        """ Returns if white can castle on queenside. """

        return bool(self & self.WHITE_QUEENSIDE)

    @property
    def black_kingside(self) -> bool:
        """ Returns if black can castle on kingside. """

        return bool(self & self.BLACK_KINGSIDE)

    @property
    def black_queenside(self) -> bool:
        """ Returns if black can castle on queenside. """

        return bool(self & self.BLACK_QUEENSIDE)

    def revoke_rights(self, other: 'CastlingRights') -> 'CastlingRights':
        """ Return a new CastlingRights with the given right(s) revoked. """

        return CastlingRights(self & ~other)

    def grant_rights(self, other: 'CastlingRights') -> 'CastlingRights':
        """ Return a new CastlingRights with the given right(s) granted. """

        return CastlingRights(self | other)

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
        """

        if (fen_field == '-'):
            return cls(value = cls.NONE)

        value = (
              (cls.WHITE_KINGSIDE  if ('K' in fen_field) else 0)
            | (cls.WHITE_QUEENSIDE if ('Q' in fen_field) else 0)
            | (cls.BLACK_KINGSIDE  if ('k' in fen_field) else 0)
            | (cls.BLACK_QUEENSIDE if ('q' in fen_field) else 0)
        )

        return cls(value)

    @classmethod
    def from_bools(cls,
            white_kingside:  bool = True,
            white_queenside: bool = True,
            black_kingside:  bool = True,
            black_queenside: bool = True,
            ) -> 'CastlingRights':
        """ Create castling rights from the given flags. """

        value = (
              (cls.WHITE_KINGSIDE  if white_kingside  else 0)
            | (cls.WHITE_QUEENSIDE if white_queenside else 0)
            | (cls.BLACK_KINGSIDE  if black_kingside  else 0)
            | (cls.BLACK_QUEENSIDE if black_queenside else 0)
        )

        return cls(value)

    def __str__(self) -> str:
        return self.to_fen_string()

    def __repr__(self) -> str:
        return f"CastlingRights({self.to_fen_string()}.)"

WHITE_KINGSIDE_RIGHTS  = CastlingRights(CastlingRights.WHITE_KINGSIDE)
WHITE_QUEENSIDE_RIGHTS = CastlingRights(CastlingRights.WHITE_QUEENSIDE)
BLACK_KINGSIDE_RIGHTS  = CastlingRights(CastlingRights.BLACK_KINGSIDE)
BLACK_QUEENSIDE_RIGHTS = CastlingRights(CastlingRights.BLACK_QUEENSIDE)
ALL_WHITE_RIGHTS       = CastlingRights(CastlingRights.WHITE_KINGSIDE | CastlingRights.WHITE_QUEENSIDE)
ALL_BLACK_RIGHTS       = CastlingRights(CastlingRights.BLACK_KINGSIDE | CastlingRights.BLACK_QUEENSIDE)
