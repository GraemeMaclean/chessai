"""
FEN (Forsyth-Edwards Notation) parsing and serialization.

All functions in this module are pure Python and do not depend on the
python-chess library.  They operate on the project's own types:
Square, Piece, Color, PieceType, and CastlingRights.

FEN format:
  <pieces> <turn> <castling> <en-passant> <halfmove-clock> <fullmove-number>

  pieces       — ranks 8..1, files a..h; '/' separates ranks; digits = empty squares
  turn         — 'w' or 'b'
  castling     — 'KQkq' subset or '-'
  en-passant   — target square in algebraic notation or '-'
  halfmove     — integer
  fullmove     — integer (starts at 1, increments after Black's move)

See: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
"""

import chessai.core.castling
import chessai.core.piece
import chessai.core.square
import chessai.core.types

# Maps the single-character FEN symbol to a (PieceType, Color) pair.
_FEN_SYMBOL_TO_PIECE: dict[str, tuple[chessai.core.types.PieceType, chessai.core.types.Color]] = {
    'P': (chessai.core.types.PieceType.PAWN,   chessai.core.types.Color.WHITE),
    'N': (chessai.core.types.PieceType.KNIGHT, chessai.core.types.Color.WHITE),
    'B': (chessai.core.types.PieceType.BISHOP, chessai.core.types.Color.WHITE),
    'R': (chessai.core.types.PieceType.ROOK,   chessai.core.types.Color.WHITE),
    'Q': (chessai.core.types.PieceType.QUEEN,  chessai.core.types.Color.WHITE),
    'K': (chessai.core.types.PieceType.KING,   chessai.core.types.Color.WHITE),
    'p': (chessai.core.types.PieceType.PAWN,   chessai.core.types.Color.BLACK),
    'n': (chessai.core.types.PieceType.KNIGHT, chessai.core.types.Color.BLACK),
    'b': (chessai.core.types.PieceType.BISHOP, chessai.core.types.Color.BLACK),
    'r': (chessai.core.types.PieceType.ROOK,   chessai.core.types.Color.BLACK),
    'q': (chessai.core.types.PieceType.QUEEN,  chessai.core.types.Color.BLACK),
    'k': (chessai.core.types.PieceType.KING,   chessai.core.types.Color.BLACK),
}

_PIECE_TO_FEN_SYMBOL: dict[tuple[chessai.core.types.PieceType, chessai.core.types.Color], str] = {
    v: k for (k, v) in _FEN_SYMBOL_TO_PIECE.items()
}

class ParsedFEN:
    """
    The raw data extracted from a FEN string.
    """

    __slots__ = (
        'pieces',
        'turn',
        'castling_rights',
        'en_passant_square',
        'halfmove_clock',
        'fullmove_number',
    )

    def __init__(self,
            pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece],
            turn: chessai.core.types.Color,
            castling_rights: chessai.core.castling.CastlingRights,
            en_passant_square: chessai.core.square.Square | None,
            halfmove_clock: int,
            fullmove_number: int,
            ) -> None:
        self.pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece] = pieces
        self.turn: chessai.core.types.Color = turn
        self.castling_rights: chessai.core.castling.CastlingRights = castling_rights
        self.en_passant_square: chessai.core.square.Square | None = en_passant_square
        self.halfmove_clock: int = halfmove_clock
        self.fullmove_number: int = fullmove_number

def parse(fen: str) -> ParsedFEN:
    """
    Parse a FEN string into a ParsedFEN.

    Raises ValueError if the FEN is malformed.

    See https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation .
    """

    fields = fen.strip().split()
    if (len(fields) != 6):
        raise ValueError(f"FEN must have exactly 6 fields, found {len(fields)}: '{fen}'.")

    pieces          = _parse_pieces(fields[0])
    turn            = _parse_turn(fields[1])
    castling_rights = chessai.core.castling.CastlingRights.from_fen_string(fields[2])
    en_passant      = _parse_en_passant(fields[3])
    halfmove_clock  = _parse_int_field(fields[4], 'halfmove clock', min_value = 0)
    fullmove_number = _parse_int_field(fields[5], 'fullmove number', min_value = 1)

    return ParsedFEN(
        pieces          = pieces,
        turn            = turn,
        castling_rights = castling_rights,
        en_passant_square = en_passant,
        halfmove_clock  = halfmove_clock,
        fullmove_number = fullmove_number,
    )

def serialize(
        pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece],
        turn: chessai.core.types.Color,
        castling_rights: chessai.core.castling.CastlingRights,
        en_passant_square: chessai.core.square.Square | None,
        halfmove_clock: int,
        fullmove_number: int,
        ) -> str:
    """ Serialize game state fields back into a FEN string. """

    piece_field    = _serialize_pieces(pieces)
    turn_field     = 'w' if (turn == chessai.core.types.Color.WHITE) else 'b'
    castling_field = castling_rights.to_fen_string()
    ep_field       = en_passant_square.name if (en_passant_square is not None) else '-'

    return f"{piece_field} {turn_field} {castling_field} {ep_field} {halfmove_clock} {fullmove_number}"

def _parse_pieces(
        piece_field: str,
) -> dict[chessai.core.square.Square, chessai.core.piece.Piece]:
    """
    Parse the piece-placement field of a FEN string.

    FEN ranks are ordered 8..1 (rank 8 is first), files a..h left-to-right.
    """

    ranks = piece_field.split('/')
    if (len(ranks) != chessai.core.types.DEFAULT_BOARD_SIZE):
        raise ValueError(
            f"FEN piece field must have {chessai.core.types.DEFAULT_BOARD_SIZE} ranks"
            + f" separated by '/', found {len(ranks)}: '{piece_field}'."
        )

    pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece] = {}

    for (rank_index, rank_str) in enumerate(ranks):
        # FEN rank 8 is index 0 in the string, which is rank 7 in [0, 7].
        rank = chessai.core.types.DEFAULT_BOARD_SIZE - 1 - rank_index
        file = 0

        for char in rank_str:
            if (char.isdigit()):
                file += int(char)
            elif (char in _FEN_SYMBOL_TO_PIECE):
                if (file >= chessai.core.types.DEFAULT_BOARD_SIZE):
                    raise ValueError(f"Too many pieces on rank {rank + 1} in FEN: '{piece_field}'.")

                square = chessai.core.square.Square.from_file_rank(file, rank)
                piece_type, color = _FEN_SYMBOL_TO_PIECE[char]
                pieces[square] = chessai.core.piece.Piece(piece_type, color)
                file += 1
            else:
                raise ValueError(f"Unknown character '{char}' in FEN piece field: '{piece_field}'.")

        if (file != chessai.core.types.DEFAULT_BOARD_SIZE):
            raise ValueError(
                f"Rank {rank + 1} has {file} files, expected"
                + f" {chessai.core.types.DEFAULT_BOARD_SIZE}: '{piece_field}'."
            )

    return pieces

def _serialize_pieces(pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece]) -> str:
    """
    Serialize a piece map into the piece-placement field of a FEN string.
    """

    ranks: list[str] = []

    for rank_index in range(chessai.core.types.DEFAULT_BOARD_SIZE):
        # FEN rank 8 comes first, so we descend from rank 7 to rank 0.
        rank = chessai.core.types.DEFAULT_BOARD_SIZE - 1 - rank_index
        empty_count = 0
        rank_str = ''

        for file in range(chessai.core.types.DEFAULT_BOARD_SIZE):
            square = chessai.core.square.Square.from_file_rank(file, rank)
            piece = pieces.get(square)

            if (piece is None):
                empty_count += 1
            else:
                if (empty_count > 0):
                    rank_str += str(empty_count)
                    empty_count = 0
                symbol = _PIECE_TO_FEN_SYMBOL.get((piece.piece_type, piece.color))
                if (symbol is None):
                    raise ValueError(f"Cannot serialize piece {piece} at {square}")
                rank_str += symbol

        if (empty_count > 0):
            rank_str += str(empty_count)

        ranks.append(rank_str)

    return '/'.join(ranks)

def _parse_turn(turn_field: str) -> chessai.core.types.Color:
    if (turn_field == 'w'):
        return chessai.core.types.Color.WHITE

    if (turn_field == 'b'):
        return chessai.core.types.Color.BLACK

    raise ValueError(f"FEN turn field must be 'w' or 'b', found: '{turn_field}'.")

def _parse_en_passant(ep_field: str) -> chessai.core.square.Square | None:
    if (ep_field == '-'):
        return None
    try:
        return chessai.core.square.Square.from_name(ep_field)
    except Exception as exc:
        raise ValueError(f"Invalid FEN en-passant field: '{ep_field}'.") from exc

def _parse_int_field(raw: str, label: str, min_value: int = 0) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"FEN {label} must be an integer, found: '{raw}'.") from exc

    if (value < min_value):
        raise ValueError(f"FEN {label} must be >= {min_value}, found: {value}.")

    return value
