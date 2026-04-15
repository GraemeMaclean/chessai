import copy
import random
import typing

import edq.util.json

import chessai.core.action
import chessai.core.agentaction
import chessai.core.board
import chessai.core.castling
import chessai.core.fen
import chessai.core.piece
import chessai.core.coordinate
import chessai.core.types

DEFAULT_FEN: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class GameState(edq.util.json.DictConverter):
    """
    The base for all game states in chessai.
    A game state should contain all the information about the current state of the game.
    The board is not responsible for any mutable state.

    Game states should only be interacted with via their methods and not their member variables.
    """

    def __init__(self,
                 fen: str | None = None,
                 move_stack: list[chessai.core.action.Action] | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        if (fen is None):
            fen = DEFAULT_FEN

        # TODO(Lucas): Parse the board size from the FEN so we can give it to the board.
        parsed_fen = chessai.core.fen.parse(fen)

        self.board: chessai.core.board.Board = chessai.core.board.Board(parsed_fen.pieces)
        """ The board responsible for holding the position of pieces. """

        self.turn: chessai.core.types.Color = parsed_fen.turn
        """ The color of the current player. """

        self.castling_rights: chessai.core.castling.CastlingRights = parsed_fen.castling_rights
        """ The available castling moves. """

        self.en_passant_coordinate: chessai.core.coordinate.Coordinate | None = parsed_fen.en_passant_coordinate
        """ The en-passant target coordinate, or None. """

        self.halfmove_clock: int = parsed_fen.halfmove_clock
        """ The number of plies since the last pawn move or capture (50-move rule). """

        self.fullmove_number: int = parsed_fen.fullmove_number
        """ Increments after every black move, starting at 1. """

        if (move_stack is None):
            move_stack = []

        self.move_stack: list[chessai.core.action.Action] = move_stack
        """ The ordered history of all actions taken, starting with the oldest action. """

        self.seed: int = seed
        """ A utility seed that components using the game state may use to seed their own RNGs. """

        self.game_over: bool = game_over
        """ Indicates that this state represents a complete game. """

    def get_fen(self) -> str:
        """
        Serialize the current gamestate to a FEN string.

        Note that this operation looses the move history.
        """

        return chessai.core.fen.serialize(
            pieces            = self.board.pieces,
            turn              = self.turn,
            castling_rights   = self.castling_rights,
            en_passant_coordinate = self.en_passant_coordinate,
            halfmove_clock    = self.halfmove_clock,
            fullmove_number   = self.fullmove_number,
        )

    # -----------------------------------------------
    # Useful methods for students.
    # -----------------------------------------------

    def get_move_count(self) -> int:
        """ Returns the number of moves in the game. """

        return len(self.move_stack)

    def get_piece_coordinates(self,
                   piece_type: chessai.core.types.PieceType,
                   color: chessai.core.types.Color) -> list[chessai.core.coordinate.Coordinate]:
        """ Gets the pieces of the given type and color. """

        return self.board.get_piece_coordinates(piece_type, color)

    # TODO(Lucas)
    def get_search_targets(self) -> list[chessai.core.coordinate.Coordinate]:
        """ Gets the coordinates on the board that are search targets. """

        pass

    # TODO(Lucas)
    def get_legal_actions(self) -> list[chessai.core.action.Action]:
        """ Return the list of legal actions for the current player. """

        pass

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Return whether the given action captures a piece. """

        return self.board.is_capture(action)

    def get_neighbors(self, start_coordinate: chessai.core.coordinate.Coordinate) -> list[tuple[chessai.core.action.Action, chessai.core.coordinate.Coordinate]]:
        """ Get coordinates that the piece at the given coordinate can reach legally, and the action it would take to get there. """

        neighbors: list[tuple[chessai.core.action.Action, chessai.core.coordinate.Coordinate]] = []

        for action in self.get_legal_actions():
            # Skip the legal moves that are not from the starting coordinate.
            if (action.start_coordinate != start_coordinate):
                continue

            neighbors.append((action, action.end_coordinate))

        return neighbors

    # TODO(Lucas)
    def is_game_over(self) -> bool:
        """ Returns whether the game is over according to the board rules. """

        pass

    # TODO(Lucas)
    def get_winners(self) -> list[chessai.core.types.Color]:
        """
        Gets the list of winners from the game.
        An empty list signifies the game is in progress or it is a tie.
        """

        pass

    # TODO(Lucas)
    def get_termination_reason(self) -> chessai.core.types.TerminationReason:
        """ Return the reason the game ended. """

        pass

    # -----------------------------------------------
    # State mutation
    # -----------------------------------------------

    # TODO(Lucas): We may want to track the most recent piece taken.
    def push(self, action: chessai.core.action.Action) -> None:
        """ Updates the gamestate with the given action. """

        if (action not in self.get_legal_actions()):
            raise ValueError(f"Cannot push an illegal action: '{action}'.")

        # TODO(Lucas): Pass key info and not full FEN.
        # TODO(Lucas): Receive key info and update the gamestate accordingly.
        self.board.push(action)
        self.move_stack.append(action)

    # TODO(Lucas): We will want to tell the board if it needs to put a piece where we are undoing.
    def pop(self) -> None:
        """ Undoes the last action. """

        last_action = self.move_stack.pop()
        self.board.pop(last_action)

    # TODO(Lucas)
    def copy(self) -> 'GameState':
        """
        Get a deep copy of this state.

        Child classes are responsible for making any deep copies they need to.
        """

        new_state = copy.copy(self)

        new_state.castling_rights = self.castling_rights.copy()
        new_state.move_stack      = list(self.move_stack)
        new_state.board           = self.board.copy()

        return new_state

    def generate_successor(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> 'GameState':
        """
        Create a new deep copy of this state that represents the current agent taking the given action.
        To just apply an action to the current state, use process_turn().
        """

        successor = self.copy()
        successor.process_turn_full(action, rng, **kwargs)

        return successor

    # -----------------------------------------------
    # Functions used for agents to follow the flow of the game.
    # -----------------------------------------------

    def game_start(self) -> None:
        """
        Indicate that the game is starting.
        This will initialize some state.
        """

    def agents_game_start(self, agent_responses: dict[chessai.core.types.Color, chessai.core.agentaction.AgentActionRecord]) -> None:
        """ Indicate that agents have been started. """

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        """
        Indicate that the game has ended.
        The state should take any final actions and return the player colors of the winning agents (if any) and the score of the game.
        """

        return ([], 0)

    def process_agent_timeout(self, player: chessai.core.types.Color) -> None:
        """
        Notify the state that the given agent has timed out.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_agent_crash(self, player: chessai.core.types.Color) -> None:
        """
        Notify the state that the given agent has crashed.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_game_timeout(self) -> None:
        """
        Notify the state that the game has reached the maximum number of turns without ending.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_turn(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        self.push(action)

    def process_turn_full(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This will modify the current state.
        First procecss_turn() will be called,
        then any bookkeeping will be performed.
        Child classes should prefer overriding the simpler process_turn().

        To get a copy of a potential successor state, use generate_successor().
        """

        # If the game is over, don't do anyhting.
        # This case can come up when planning agent actions and generating successors.
        if (self.game_over):
            return

        self.process_turn(action, rng, **kwargs)

    # TODO(Lucas)
    def to_pgn(self) -> str:
        """Serialize the gamestate to a PGN string."""

        pass

    # TODO(Lucas)
    @classmethod
    def from_pgn(cls, pgn_string: str) -> 'GameState':
        """ Reconstruct a Board from a PGN string, restoring the full move history. """

        pass

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'fen':        self.get_fen(),
            'move_stack': [action.to_dict() for action in self.move_stack],
            'seed':       self.seed,
            'game_over':  self.game_over,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        board = chessai.core.board.Board.from_dict(data['board'])
        move_stack = [
            chessai.core.action.Action.from_dict(a)
            for a in data.get('move_stack', [])
        ]
        return cls(
            fen        = data.get('fen', None),
            move_stack = move_stack,
            seed       = data.get('seed', -1),
            game_over  = data.get('game_over', False),
        )

@typing.runtime_checkable
class AgentStateEvaluationFunction(typing.Protocol):
    """
    A function that can be used to score a game state.
    """

    def __call__(self,
            state: GameState,
            action: chessai.core.action.Action | None = None,
            agent: typing.Any | None = None,
            **kwargs: typing.Any) -> float:
        """
        Compute a score for a state that the provided agent can use to decide actions.
        The current state is the only required argument, the others are optional.
        Passing the agent asking for this evaluation is a simple way to pass persistent state
        (like pre-computed heuristics) from the agent to this function.
        """

def base_eval(
        state: GameState,
        action: chessai.core.action.Action | None = None,
        agent: typing.Any | None = None,
        **kwargs: typing.Any) -> float:
    """
    The most basic evaluation function, which just uses the difference in piece value on the board.
    """

    piece_values: dict[chessai.core.types.PieceType, int] = {
        chessai.core.types.PieceType.PAWN: 1,
        chessai.core.types.PieceType.KNIGHT: 3,
        chessai.core.types.PieceType.BISHOP: 3,
        chessai.core.types.PieceType.ROOK: 5,
        chessai.core.types.PieceType.QUEEN: 9,
        chessai.core.types.PieceType.KING: 9999,
    }

    # The difference in pieces from white's perspective.
    board_value = 0
    for (piece_type, piece_value) in piece_values.items():
        white_piece_count = len(state.get_piece_coordinates(piece_type, chessai.core.types.Color.WHITE))
        black_piece_count = len(state.get_piece_coordinates(piece_type, chessai.core.types.Color.BLACK))
        piece_count = white_piece_count - black_piece_count

        board_value += (piece_count * piece_value)

    if (state.turn == chessai.core.types.Color.WHITE):
        return board_value

    # The piece difference is the opposite for black.
    return -1 * board_value
