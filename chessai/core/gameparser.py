import enum
import os
import random
import re
import typing

import edq.util.json

import chessai.core.action
import chessai.core.board
import chessai.core.castling
import chessai.core.coordinate
import chessai.core.gamestate
import chessai.core.piece
import chessai.core.types

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
GAMES_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'games')

PGN_FILE_EXTENSION = '.pgn'

# File parsing patterns.
SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')

# PGN parsing patterns.
TAG_PATTERN: re.Pattern= re.compile(r"^\[([A-Za-z0-9][A-Za-z0-9_+#=:-]*)\s+\"([^\r]*)\"\]\s*$")
TAG_NAME_PATTERN: re.Pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_+#=:-]*\Z")
MOVETEXT_PATTERN: re.Pattern = re.compile(r"""
    (
        [NBKRQ]?[a-h]?[1-8]?[\-x]?[a-h][1-8](?:=?[nbrqkNBRQK])?
        |[PNBRQK]?@[a-h][1-8]
        |--
        |Z0
        |0000
        |@@@@
        |O-O(?:-O)?
        |0-0(?:-0)?
    )
    |(\{.*})
    |(\{.*)
    |(;.*)
    |(\$[0-9]+)
    |(\()
    |(\))
    |(\*|1-0|0-1|1/2-1/2)
    |([\?!]{1,2})
    """, re.DOTALL | re.VERBOSE)

SKIP_MOVETEXT_REGEX = re.compile(r""";|\{|\}""")

FEN_HEADER_KEY: str = 'FEN'

class StandardPGNHeaders(enum.StrEnum):
    """
    The standard seven PGN headers.
    """

    EVENT = 'Event'
    """ The name of the tournament or match event. """

    SITE = 'Site'
    """ The location of the event. """

    DATE = 'Date'
    """ The starting date of the game. """

    ROUND = 'Round'
    """ The playing round ordinal of the game. """

    WHITE = 'White'
    """ The player of the white pieces. """

    BLACK = 'Black'
    """ The player of the black pieces. """

    RESULT = 'Result'
    """ The result of the game. """

class StandardHeadersDict(dict):
    """
    A dictionary that only allows StandardPGNHeaders as keys.

    These seven standard tags will always be present in the headers:
     - Event: the name of the tournament or match event
     - Site: the location of the event
     - Date: the starting date of the game
     - Round: the playing round ordinal of the game
     - White: the player of the white pieces
     - Black: the player of the black pieces
     - Result: the result of the game

    To see the full description of the possible headers and their format,
    see https://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm#c8.1 .
    """

    def __setitem__(self, key: StandardPGNHeaders, value: str) -> None:
        if (not isinstance(key, StandardPGNHeaders)):
            raise TypeError(f"Key must be an instance of StandardPGNHeaders, not {type(key).__name__}.")

        super().__setitem__(key, value)

    def is_complete(self) -> bool:
        """ Returns if all standard headers are present in the dictionary. """

        return (set(self.keys()) == set(StandardPGNHeaders))

class PGNResult(enum.StrEnum):
    """ The possible game endings denoted in a PGN. """

    WHITE_WIN = '1-0'
    """ White won the game. """

    BLACK_WIN = '0-1'
    """ Black won the game. """

    TIE = '1/2-1/2'
    """ The game was a tie. """

    IN_PROGRESS = '*'
    """ The game is still in progress. """

    UNKNOWN = 'Unknown'
    """ The ending of the game is unknown. """

class ParsedPGN(edq.util.json.DictConverter):
    """
    The parsed result of a single PGN game.
    """

    def __init__(self,
                 headers: StandardHeadersDict[StandardPGNHeaders, str] | None = None,
                 optional_headers: dict[str, typing.Any] | None = None,
                 starting_fen: str | None = None,
                 initial_actions: list[chessai.core.action.Action] | None = None,
                 comments: list[str] | None = None,
                 result: PGNResult = PGNResult.UNKNOWN) -> None:

        if (headers is None):
            headers = StandardHeadersDict()

        self.headers: StandardHeadersDict[StandardPGNHeaders, str] = headers
        """ The standard headers from a single PGN game. """

        if (optional_headers is None):
            optional_headers = {}

        self.optional_headers: dict[str, typing.Any] = optional_headers
        """ Any additional headers parsed from the PGN. """

        self.starting_fen: str | None = starting_fen
        """ The starting FEN for the game, which is often omitted to denote the default FEN. """

        if (initial_actions is None):
            initial_actions = []

        self.initial_actions: list[chessai.core.action.Action] = initial_actions
        """
        The moves in the game, written in Short Algebraic Notation.

        See https://en.wikipedia.org/wiki/Algebraic_notation_(chess) .
        """

        if (comments is None):
            comments = []

        self.comments: list[str] = comments
        """ The comments found in the game. """

        self.result: PGNResult = result
        """ The result of the PGN or if the game is still in progress. """

    def get_starting_fen(self) -> str | None:
        """ Get the optional FEN header from the PGN. """

        return self.optional_headers.get(FEN_HEADER_KEY, None)

def parse_pgn(pgn: str, state_class: typing.Type[chessai.core.gamestate.GameState]) -> ParsedPGN | None:
    """
    Parse a single PGN string into a ParsedPGN.

    Raises ValueError if the PGN is malformed.
    See https://en.wikipedia.org/wiki/Portable_Game_Notation .
    """

    lines = pgn.splitlines()

    index = 0

    headers: StandardHeadersDict = StandardHeadersDict()
    optional_headers: dict[str, typing.Any] = {}

    # Parse the header fields.
    for i, line in enumerate(lines):
        # Track where we are in the lines.
        index = i

        clean_line = line.strip()

        # Skip empty lines.
        if (len(line) == 0):
            continue

        # Skip comments.
        if (_is_pgn_comment_line(clean_line)):
            continue

        # Headers must begin with an open bracket.
        if (not clean_line.startswith("[")):
            break

        tag_match = TAG_PATTERN.match(clean_line)

        # Ignore malformed tags.
        if (not tag_match):
            continue

        tag_header_key = tag_match.group(1)
        tag_header_value = tag_match.group(2)

        # Determine if this is a standard header key or not.
        if (tag_header_key in StandardPGNHeaders):
            headers[StandardPGNHeaders(tag_header_key)] = tag_header_value
        else:
            optional_headers[tag_header_key] = tag_header_value

    # No game found.
    if (len(headers) == 0):
        return None

    # Ensure all required headers are present.
    if (not headers.is_complete()):
        expected_headers = [header.value for header in StandardPGNHeaders]
        actual_headers = [header.value for header in headers.keys()]
        raise ValueError(f"Did not find all required headers. Expected: '{expected_headers}', Found: '{actual_headers}'.")

    # Start scanning for moves from the end of the headers.
    lines = lines[index:]

    # Set up a gamestate to follow along and parse SANs.
    fen = optional_headers.get(FEN_HEADER_KEY, None)
    state = state_class(fen = fen)
    rng = random.Random(1)

    initial_actions: list[chessai.core.action.Action] = []
    comments: list[str] = []
    result: PGNResult = PGNResult.UNKNOWN

    in_comment = False
    comment_buffer: list[str] = []

    skip_variation_depth = 0

    for line in lines:
        line = line.strip()

        if (not line):
            break

        # Skip whole-line comments.
        if _is_pgn_comment_line(line):
            continue

        i = 0
        while (i < len(line)):
            if in_comment:
                end_idx = line.find("}", i)

                # The rest of the line is part of the comment.
                if (end_idx == -1):
                    comment_buffer.append(line[i:])
                    break

                # Add the remainder of the comment and continue processing the current line.
                comment_buffer.append(line[i:end_idx])
                comments.append("\n".join(comment_buffer).strip())

                comment_buffer = []
                in_comment = False

                continue

            match = MOVETEXT_PATTERN.match(line, i)

            if (not match):
                i += 1
                continue

            token = match.group(0)
            i = match.end()

            # Handle block comments {...}.
            if token.startswith("{"):
                content = token[1:]

                end_index = content.find("}")

                if (end_index == -1):
                    # Track part of a multi-line comment.
                    in_comment = True
                    comment_buffer.append(content)
                else:
                    # Add the in-line comment and continue processing this line.
                    comments.append(content[:end_index].strip())

                continue

            # Skip variations (...) entirely.
            if (token == "("):
                skip_variation_depth += 1
                continue

            if (token == ")"):
                if (skip_variation_depth > 0):
                    skip_variation_depth -= 1

                continue

            if (skip_variation_depth > 0):
                continue

            # Skip line comments.
            if token.startswith(";"):
                break

            # Skip move numbers like "1." or "23.".
            if token.endswith("."):
                continue

            # Skip results.
            if (token in ["1-0", "0-1", "1/2-1/2", "*"]):
                result = PGNResult(token)
                break

            # Skip NAGs / annotations.
            if (token.startswith("$") or (token in ["!", "?", "!!", "??", "!?", "?!"])):
                continue

            # Otherwise, this must be a SAN move.
            action = state.get_action_from_san(token)
            if (action == chessai.core.action.NULL_ACTION):
                raise ValueError(f"Unable to find a legal action for the SAN: '{token}'.")

            state.process_turn_full(action, rng)
            initial_actions.append(action)

    return ParsedPGN(
        headers          = headers,
        optional_headers = optional_headers,
        initial_actions  = initial_actions,
        comments         = comments,
        result           = result,
    )

def _is_pgn_comment_line(line: str) -> bool:
    """
    Returns if the line is a comment.

    A line is a comment in a PGN if it  starts with a '%' or ';'.
    """

    line = line.strip()
    if (len(line) == 0):
        return True

    if (line[0] == '%'):
        return True

    if (line[0] == ';'):
        return True

    return False
