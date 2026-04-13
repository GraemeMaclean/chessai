import copy
import io
import os
import re
import typing

import chess
import chess.pgn
import edq.util.json

import chessai.core.action
import chessai.core.square
import chessai.core.types
import chessai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'boards')

AGENT_PATTERN: re.Pattern = re.compile(r'^\d$')
INT_PATTERN: re.Pattern = re.compile(r'\d+')
SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')

FILE_EXTENSION = '.board'

DEFAULT_BOARD_CLASS: str = 'chessai.core.board.Board'
DEFAULT_FEN: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# TODO(Lucas): Continue adding the necessary methods for students to interact with the board.
class Board(edq.util.json.DictConverter):
    """
    The board for all chess games in chessai.
    A board holds the current state and history of the game.

    Boards should only be interacted with via their methods and not their member variables.
    """

    def __init__(self,
            source: str,
            start_fen: str = DEFAULT_FEN,
            search_targets: list[chessai.core.square.Square] | dict[str, typing.Any] | None = None,
            check_validity: bool = False,
            **kwargs: typing.Any) -> None:
        """
        Construct a board.
        The board must be a valid board given by the starting FEN if check_validity is true.
        """

        self.source: str = source
        """ Where this board was loaded from. """

        self._board = chess.Board(start_fen)
        """ The current board which stores the current state and the history. """

        self.num_files: int = chessai.core.types.DEFAULT_BOARD_SIZE
        """ The number of files of the chess board. """

        self.num_ranks: int = chessai.core.types.DEFAULT_BOARD_SIZE
        """ The number of ranks of the chess board. """

        if (search_targets is None):
            search_targets = []

        self.search_targets: list[chessai.core.square.Square] = search_targets  # type: ignore
        """ The targets of the piece tour search. """

        # Convert the string case into the dict case.
        if (isinstance(search_targets, str)):
            search_targets = {
                chessai.core.square.SQUARES_KEY: search_targets
            }

        if (isinstance(search_targets, dict)):
            self.search_targets = chessai.core.square.squares_from_dict(search_targets)

        if (check_validity and (not self.is_valid())):
            raise ValueError("Invalid board format: '{start_fen}'.")

    @property
    def files(self) -> int:
        """ The files (columns) of this square, in [0, 7]. a=0, h=7. """

        return self.num_files

    @property
    def ranks(self) -> int:
        """ The number of ranks (rows) of this board, in [0, 7]. Rank 1=0, Rank 8=7. """

        return self.num_ranks

    def is_valid(self) -> bool:
        """ Checks if the board is in a valid square. """

        return self._board.is_valid()

    def get_turn(self) -> chessai.core.types.Color:
        """ The side to move (chessai.core.types.WHITE or chessai.core.types.BLACK). """

        return chessai.core.types.Color(self._board.turn)

    def get_fullmove_number(self) -> int:
        """ Counts move pairs. Starts at 1 and is incremented after every move of the black side. """

        return self._board.fullmove_number

    def get_legal_moves(self) -> chess.LegalMoveGenerator:
        """ Returns a dynamic list of the legal moves. """

        return self._board.legal_moves

    def get_fen(self) -> str:
        """ Gets a FEN representation of the current board square. """

        return self._board.fen()

    def get_pieces(self,
                   piece_type: chessai.core.types.PieceType,
                   color: chessai.core.types.Color) -> list[chessai.core.square.Square]:
        """ Gets the pieces of the given type and color. """

        squares: list[chessai.core.square.Square] = []

        chess_squares = self._board.pieces(piece_type.chess_int, bool(color))
        for chess_square in chess_squares:
            squares.append(chessai.core.square.Square.from_square(chess_square))

        return squares

    def get_winners(self) -> list[chessai.core.types.Color]:
        """
        Gets the list of winners from the game.
        If the game is not over, it will be considered a tie.
        """

        outcome = self._board.outcome()
        if (outcome is None):
            return []

        if (outcome.winner is None):
            return []

        return [chessai.core.types.Color(outcome.winner)]

    def get_termination_reason(self) -> chessai.core.types.TerminationReason:
        """ Get the reason for the game ending. """

        outcome = self._board.outcome()
        if (outcome is None):
            return chessai.core.types.TerminationReason.IN_PROGRESS

        return chessai.core.types.TerminationReason.from_chess_termination(outcome.termination)

    def is_game_over(self, claim_draw: bool = False) -> bool:
        """ Returns if the game is over. """

        return self._board.is_game_over(claim_draw)

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Returns if the move captures a piece. """

        return self._board.is_capture(action.get_move())

    def get_neighbors(self, start_square: chessai.core.square.Square) -> list[tuple[chessai.core.action.Action, chessai.core.square.Square]]:
        """
        Get squares that the piece at the given square can reach legally,
        and the action it would take to get there.
        """

        neighbors: list[tuple[chessai.core.action.Action, chessai.core.square.Square]] = []

        for move in self.get_legal_moves():
            # Skip the legal moves that are not from the starting square.
            if (chessai.core.square.Square.from_square(move.from_square) != start_square):
                continue

            end_square = chessai.core.square.Square.from_square(move.to_square)
            action = chessai.core.action.Action(move.uci())
            neighbors.append((action, end_square))

        return neighbors

    def get_move_count(self) -> int:
        """ Returns the number of moves in the game. """

        return len(self._board.move_stack)

    def get_search_targets(self) -> list[chessai.core.square.Square]:
        """ Returns the search target of the board. """

        return self.search_targets

    def remove_search_target(self, square: chessai.core.square.Square) -> None:
        """
        Remove a search target from the board.
        If the square is not a search target, the board is unchanged.
        """

        if (square not in self.search_targets):
            return

        self.search_targets.remove(square)

    def _push(self, action: chessai.core.action.Action) -> None:
        """ Updates the square with the given move and puts it onto the move stack. """

        return self._board.push(action.get_move())

    def copy(self) -> 'Board':
        """ Create a deep copy of the board. """

        instance = self.__class__.__new__(self.__class__)
        instance.source = self.source
        instance._board = self._board.copy()
        instance.num_files = self.num_files
        instance.num_ranks = self.num_ranks
        instance.search_targets = copy.deepcopy(self.search_targets)
        return instance

    def to_pgn(self) -> str:
        """Serialize the board's game history to a PGN string."""

        game = chess.pgn.Game.from_board(self._board)
        exporter = chess.pgn.StringExporter()
        return game.accept(exporter)

    @classmethod
    def from_pgn(cls, pgn_string: str,
             search_targets: list[chessai.core.square.Square] | dict[str, typing.Any] | None = None,
             ) -> 'Board':
        """ Reconstruct a Board from a PGN string, restoring the full move history. """

        game = chess.pgn.read_game(io.StringIO(pgn_string))
        if (game is None):
            raise ValueError(f"Unable to read PGN of board: '{pgn_string}'.")

        # Replay the move history to get the final FEN.
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)

        return cls('pgn', board.fen(), search_targets)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'pgn': self.to_pgn(),
            'search_targets': self.search_targets,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls.from_pgn(data.get('pgn', ''), data.get('search_targets', None))

def is_valid_fen(fen: str) -> bool:
    """ Checks if a FEN is valid. """

    try:
        _ = Board('TEST', fen)
    except ValueError:
        return False

    return True

def load_path(path: str, **kwargs: typing.Any) -> Board:
    """
    Load a board from a file.
    If the given path does not exist,
    try to prefix the path with the standard board directory and suffix with the standard extension.
    """

    raw_path = path

    # If the path does not exist, try the boards directory.
    if (not os.path.exists(path)):
        path = os.path.join(BOARDS_DIR, path)

        # If this path does not have a good extension, add one.
        if (os.path.splitext(path)[-1] != FILE_EXTENSION):
            path = path + FILE_EXTENSION

    if (not os.path.exists(path)):
        raise ValueError(f"Could not find board, path does not exist: '{raw_path}'.")

    text = edq.util.dirent.read_file(path, strip = False)
    return load_string(raw_path, text, **kwargs)

def load_string(source: str, text: str, **kwargs: typing.Any) -> Board:
    """ Load a board from a string. """

    separator_index = -1
    lines = text.split("\n")

    for (i, line) in enumerate(lines):
        if (SEPARATOR_PATTERN.match(line)):
            separator_index = i
            break

    if (separator_index == -1):
        # No separator was found.
        options_text = ''
        board_text = "\n".join(lines)
    else:
        options_text = "\n".join(lines[:separator_index])
        board_text = "\n".join(lines[(separator_index + 1):])

    options_text = options_text.strip()
    if (len(options_text) == 0):
        options = {}
    else:
        options = edq.util.json.loads(options_text)

    options.update(kwargs)

    target_squares = options.get(chessai.core.square.SQUARES_KEY, None)

    # If search targets were given by the CLI, override the search targets found in the file.
    if (target_squares is not None):
        options['search_targets'] = target_squares

    search_targets = options.pop('search_targets', None)

    board_class = options.get('class', DEFAULT_BOARD_CLASS)
    return chessai.util.reflection.new_object(board_class, source, board_text, search_targets, **options)  # type: ignore[no-any-return]

def parse_board(raw_board: typing.Any, **kwargs) -> Board:
    """
    Try to parse a board from a number of formats.
    Takes the board as given, or loads it from a path.
    """

    if (raw_board is None):
        board = Board('none')
    elif (is_valid_fen(raw_board)):
        board = Board('FEN', raw_board, kwargs.get(chessai.core.square.SQUARES_KEY, None))
    elif (isinstance(raw_board, Board)):
        board = raw_board
    else:
        board = load_path(raw_board, **kwargs)

    return board
