import enum

class Color(int, enum.Enum):
    """ An enum representing the side to move or the color of a piece. """
    BLACK = 0
    WHITE = 1

    def symbol(self) -> str:
        """ Returns 'w' for white and 'b' for black. """

        return 'w' if (self == Color.WHITE) else 'b'

    def opposite(self) -> 'Color':
        """ Returns the opposing color. """

        return Color.BLACK if (self == Color.WHITE) else Color.WHITE

    def __str__(self) -> str:
        return self.name.lower()

    def __repr__(self) -> str:
        return f"Color.{self.name}"

    def __bool__(self) -> bool:
        return bool(self.value)

# TODO(Lucas): Implement the functions detailed in the attribute docstrings.
# Update string enums.
class TerminationReason(enum.StrEnum):
    """ An enum representing the reason for a game to be over. """

    CHECKMATE = 'Checkmate'
    """ See chessai.core.gamestate.GameState.is_checkmate(). """

    STALEMATE = 'Stalemate'
    """ See chessai.core.gamestate.GameState.is_stalemate(). """

    INSUFFICIENT_MATERIAL = 'Insufficient Material'
    """ See chessai.core.gamestate.GameState.is_insufficient_material(). """

    SEVENTYFIVE_MOVES = 'Five-fold Repetition'
    """ See chessai.core.gamestate.GameState.is_fivefold_repition(). """

    FIFTY_MOVES = 'Fifty Moves'
    """ See chessai.core.gamestate.GameState.can_claim_fifty_moves()`. """

    THREEFOLD_REPETITION = 'Three-fold Repetition'
    """ See chessai.core.gamestate.GameState.can_claim_threefold_repetition()`. """

    VARIANT_WIN = 'Variant Win'
    """ See chessai.core.gamestate.GameState.is_variant_win()`. """

    VARIANT_LOSS = 'Variant Loss'
    """ See chessai.core.gamestate.GameState.is_variant_loss()`. """

    VARIANT_DRAW = 'Variant Draw'
    """ See chessai.core.gamestate.GameState.is_variant_draw()`. """

    IN_PROGRESS = 'In Progress'
    """ Indicates the game is still in progress (i.e., it has not yet terminated). """

    UNKNOWN = 'Unknown'
    """ The termination reason is unknown. """
