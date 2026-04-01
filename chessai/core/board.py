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

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')
AGENT_PATTERN: re.Pattern = re.compile(r'^\d$')

FILE_EXTENSION = '.board'

DEFAULT_BOARD_CLASS: str = 'chessai.core.board.Board'

# TODO(Lucas): Continue adding the necessary methods for students to interact with the board.
class Board(edq.util.json.DictConverter):
    """
    The board for all chess games in chessai.
    A board holds the current state and history of the game.

    Boards should only be interacted with via their methods and not their member variables.
    """

    def __init__(self,
                 source: str,
                 start_fen: str = chess.STARTING_FEN,
                 search_target: chessai.core.square.Square | dict[str, typing.Any] | None = None,
                 **kwargs: typing.Any) -> None:
        """
        Construct a board.
        The board must be a valid board given by the starting FEN.
        """

        self.source: str = source
        """ Where this board was loaded from. """

        self._board = chess.Board(start_fen)
        """ The current board which stores the current state and the history. """

        if (isinstance(search_target, dict)):
            search_target = chessai.core.square.Square.from_dict(search_target)

        self.search_target: chessai.core.square.Square | None = search_target  # type: ignore
        """ Some boards (especially knight's errant problems) will have a specific square search target. """

        self.num_files : int = chessai.core.types.DEFAULT_BOARD_SIZE
        """ The number of files of the chess board. """

        self.num_ranks: int = chessai.core.types.DEFAULT_BOARD_SIZE
        """ The number of ranks of the chess board. """

        # TODO(Lucas): May not be able to check if the board is valid with search problems.
        # if (not self.is_valid()):
        #     raise ValueError("Invalid board format: '{start_fen}'.")

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

    def get_turn(self) -> bool:
        """ The side to move (chess.WHITE or chess.BLACK). """
        return self._board.turn

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

    def get_outcome(self) -> chess.Outcome | None:
        """ Gets the outcome of the game if it is over. """
        return self._board.outcome()

    def is_game_over(self) -> bool:
        """ Returns if the game is over. """
        return self._board.is_game_over()

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Returns if the move captures a piece. """
        return self._board.is_capture(action.get_move())

    def get_neighbors(self, start_square: chessai.core.square.Square) -> list[tuple[chessai.core.action.Action, chessai.core.square.Square]]:
        """
        Get squares that the piece at the given square can reach legally,
        and the action it would take to get there.

        Note that this is a high-throughput piece of code, and may contain optimizations.
        """

        neighbors: list[tuple[chessai.core.action.Action, chessai.core.square.Square]] = []

        attackers = self._board.attackers(self.get_turn(), start_square.to_chess_square())
        for square in attackers:
            end_square = chessai.core.square.Square.from_square(square)
            action = chessai.core.action.Action.from_squares(start_square, end_square)
            neighbors.append((action, end_square))

        return neighbors

    def _push(self, action: chessai.core.action.Action) -> None:
        """ Updates the square with the given move and puts it onto the move stack. """
        return self._board.push(action.get_move())

    def copy(self) -> 'Board':
        """ Create a deep copy of the board. """
        instance = self.__class__.__new__(self.__class__)
        instance._board = self._board.copy()
        return instance

    def to_pgn(self) -> str:
        """Serialize the board's game history to a PGN string."""
        game = chess.pgn.Game.from_board(self._board)
        exporter = chess.pgn.StringExporter()
        return game.accept(exporter)

    @classmethod
    def from_pgn(cls, pgn_string: str) -> 'Board':
        """ Reconstruct a Board from a PGN string, restoring the full move history. """
        instance = cls.__new__(cls)

        game = chess.pgn.read_game(io.StringIO(pgn_string))
        if (game is None):
            raise ValueError(f"Unable to read PGN of board: '{pgn_string}'.")

        # Replay the move history to get the current square.
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)

        instance._board = board
        return instance

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'pgn': self.to_pgn(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls.from_pgn(data.get('pgn', ''))

def is_valid_fen(fen: str) -> bool:
    """ Checks if a FEN is valid. """

    try:
        _ = chessai.core.board.Board('TEST', fen)
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

    board_class = options.get('class', DEFAULT_BOARD_CLASS)
    return chessai.util.reflection.new_object(board_class, source, board_text, **options)  # type: ignore[no-any-return]
