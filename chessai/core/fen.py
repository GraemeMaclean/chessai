"""
FEN (Forsyth-Edwards Notation) parsing and serialization.

FEN format:
  [#<files>x<ranks>] <pieces> <turn> <castling> <en-passant> <halfmove-clock> <fullmove-number>

  dimensions   -- optional '#<files>x<ranks>' (e.g. '#8x8'); defaults to 8x8 if omitted
  pieces       -- ranks 8..1, files a..h; '/' separates ranks; digits = empty coordinates
  turn         -- 'w' or 'b'
  castling     -- 'KQkq' subset or '-'
  en-passant   -- target coordinate in algebraic notation or '-'
  halfmove     -- integer
  fullmove     -- integer (starts at 1, increments after Black's move)

The dimensions field is a chessai extension and is not part of the standard FEN spec.
Standard FEN strings (6 fields) are accepted without modification.

See: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation .
"""

import re

import chessai.core.board
import chessai.core.castling
import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

DIMENSIONS_PATTERN: re.Pattern = re.compile(r'^#(\d+)x(\d+)$')

class ParsedFEN:
    """
    The raw data extracted from a FEN string.
    """

    __slots__ = (
        'pieces',
        'turn',
        'castling_rights',
        'en_passant_coordinate',
        'halfmove_clock',
        'fullmove_number',
        'num_files',
        'num_ranks',
    )

    def __init__(self,
            pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece],
            turn: chessai.core.types.Color,
            castling_rights: chessai.core.castling.CastlingRights,
            en_passant_coordinate: chessai.core.coordinate.Coordinate | None,
            halfmove_clock: int,
            fullmove_number: int,
            num_files: int = chessai.core.board.DEFAULT_BOARD_FILES,
            num_ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS,
            ) -> None:
        self.pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] = pieces
        self.turn: chessai.core.types.Color = turn
        self.castling_rights: chessai.core.castling.CastlingRights = castling_rights
        self.en_passant_coordinate: chessai.core.coordinate.Coordinate | None = en_passant_coordinate
        self.halfmove_clock: int = halfmove_clock
        self.fullmove_number: int = fullmove_number
        self.num_files: int = num_files
        self.num_ranks: int = num_ranks

def parse(fen: str) -> ParsedFEN:
    """
    Parse a FEN string into a ParsedFEN.

    Accepts standard 6-field FEN strings as well as the chessai extended
    7-field format with an optional '<files>x<ranks>' dimensions field.

    Raises ValueError if the FEN is malformed.

    See https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation .
    """

    fields = fen.strip().split()
    if (len(fields) not in (6, 7)):
        raise ValueError(f"FEN must have 6 or 7 fields, found {len(fields)}: '{fen}'.")

    num_files = chessai.core.board.DEFAULT_BOARD_FILES
    num_ranks = chessai.core.board.DEFAULT_BOARD_RANKS

    if (len(fields) == 7):
        (num_files, num_ranks) = _parse_dimensions(fields.pop(0))

    pieces          = _parse_pieces(fields[0], num_files, num_ranks)
    turn            = _parse_turn(fields[1])
    castling_rights = chessai.core.castling.CastlingRights.from_fen_string(fields[2])
    en_passant      = _parse_en_passant(fields[3])
    halfmove_clock  = _parse_int_field(fields[4], 'halfmove clock', min_value = 0)
    fullmove_number = _parse_int_field(fields[5], 'fullmove number', min_value = 1)

    return ParsedFEN(
        pieces                = pieces,
        turn                  = turn,
        castling_rights       = castling_rights,
        en_passant_coordinate = en_passant,
        halfmove_clock        = halfmove_clock,
        fullmove_number       = fullmove_number,
        num_files             = num_files,
        num_ranks             = num_ranks,
    )

def serialize(
        pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece],
        turn: chessai.core.types.Color,
        castling_rights: chessai.core.castling.CastlingRights,
        en_passant_coordinate: chessai.core.coordinate.Coordinate | None,
        halfmove_clock: int,
        fullmove_number: int,
        num_files: int = chessai.core.board.DEFAULT_BOARD_FILES,
        num_ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS,
        ) -> str:
    """
    Serialize game state fields back into a FEN string.

    For standard 8x8 boards the dimensions field is omitted, producing a
    spec-compliant FEN string. For non-standard board sizes the chessai
    dimensions extension is appended.
    """

    piece_field    = _serialize_pieces(pieces, num_files, num_ranks)
    turn_field     = 'w' if (turn == chessai.core.types.Color.WHITE) else 'b'
    castling_field = castling_rights.to_fen_string()
    ep_field       = en_passant_coordinate.uci() if (en_passant_coordinate is not None) else '-'

    fen = f"{piece_field} {turn_field} {castling_field} {ep_field} {halfmove_clock} {fullmove_number}"

    is_standard_size = (
        (num_files == chessai.core.board.DEFAULT_BOARD_FILES)
        and (num_ranks == chessai.core.board.DEFAULT_BOARD_RANKS)
    )

    if (not is_standard_size):
        fen = f"#{num_files}x{num_ranks} {fen}"

    return fen

def _parse_dimensions(dimensions_field: str) -> tuple[int, int]:
    """
    Parse the optional chessai dimensions field '<files>x<ranks>'.

    Returns a (num_files, num_ranks) tuple.
    Raises ValueError if the field is malformed or contains non-positive values.
    """

    match = DIMENSIONS_PATTERN.fullmatch(dimensions_field)
    if (match is None):
        raise ValueError(
            "FEN dimensions field must be '#<files>x<ranks>' (e.g. '#8x8'),"
            + f" got: '{dimensions_field}'."
        )

    num_files = int(match.group(1))
    num_ranks = int(match.group(2))

    if (num_files < 1):
        raise ValueError(f"FEN dimensions num_files must be >= 1, got: {num_files}.")

    if (num_ranks < 1):
        raise ValueError(f"FEN dimensions num_ranks must be >= 1, got: {num_ranks}.")

    return (num_files, num_ranks)

def _parse_pieces(
            piece_field: str,
            num_files: int = chessai.core.board.DEFAULT_BOARD_FILES,
            num_ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS,
        ) -> dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece]:
    """
    Parse the piece-placement field of a FEN string.

    FEN ranks are ordered 8..1 (rank 8 is first), files a..h left-to-right.
    """

    ranks = piece_field.split('/')
    if (len(ranks) != num_ranks):
        raise ValueError(
            f"FEN piece field must have {num_ranks} ranks"
            + f" separated by '/', found {len(ranks)}: '{piece_field}'."
        )

    known_piece_symbols = chessai.core.piece.get_registered_piece_symbols()
    pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] = {}

    for (rank_index, rank_str) in enumerate(ranks):
        # FEN rank 8 is index 0 in the string, which is rank 7 in [0, 7].
        rank = (num_ranks - 1) - rank_index
        file = 0

        for char in rank_str:
            if (char.isdigit()):
                file += int(char)
            elif (char in known_piece_symbols):
                if (file >= num_files):
                    raise ValueError(f"Too many pieces on rank {rank + 1} in FEN: '{piece_field}'.")

                coordinate = chessai.core.coordinate.Coordinate(file, rank)
                pieces[coordinate] = chessai.core.piece.get_registered_piece(char)
                file += 1
            else:
                raise ValueError(f"Unknown character '{char}' in FEN piece field: '{piece_field}'.")

        if (file != num_files):
            raise ValueError(
                f"Rank {rank + 1} has {file} files, expected"
                + f" {num_files}: '{piece_field}'."
            )

    return pieces

def _serialize_pieces(pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece],
        num_files: int = chessai.core.board.DEFAULT_BOARD_FILES,
        num_ranks: int = chessai.core.board.DEFAULT_BOARD_RANKS) -> str:
    """
    Serialize a piece map into the piece-placement field of a FEN string.
    """

    ranks: list[str] = []

    for rank_index in range(num_ranks):
        # FEN rank 8 comes first, so we descend from rank 7 to rank 0.
        rank = (num_ranks - 1) - rank_index
        empty_count = 0
        rank_str = ''

        for file in range(num_files):
            coordinate = chessai.core.coordinate.Coordinate(file, rank)
            piece = pieces.get(coordinate)

            if (piece is None):
                empty_count += 1
            else:
                if (empty_count > 0):
                    rank_str += str(empty_count)
                    empty_count = 0

                symbol = piece.symbol()
                if (symbol is None):
                    raise ValueError(f"Cannot serialize piece {piece} at {coordinate}")

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

def _parse_en_passant(ep_field: str) -> chessai.core.coordinate.Coordinate | None:
    if (ep_field == '-'):
        return None

    try:
        return chessai.core.coordinate.Coordinate.from_uci(ep_field)
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
