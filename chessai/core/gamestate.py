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
import chessai.core.square
import chessai.core.types

class GameState(edq.util.json.DictConverter):
    """
    The base for all game states in chessai.
    A game state should contain all the information about the current state of the game.
    The board is not responsible for any mutable state.

    Game states should only be interacted with via their methods and not their member variables.

    Fields:
        board             — stateless rules engine
        pieces            — current piece positions (Square -> Piece)
        turn              — whose move it is (Color)
        castling_rights   — which castling moves are still legal
        en_passant_square — current en-passant target square, or None
        halfmove_clock    — the number of plies since last pawn move or capture
        fullmove_number   — increments after every black move (starts at 1)
        move_stack        — ordered history of actions (oldest first)
        game_over         — True once the game has ended
        seed              — utility seed for agent RNGs

    Initialization:
        The FEN string is used to populate the gamestate.
        Individual fields may override those found in the FEN.
    """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 fen: str | None = None,
                 pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece] | None = None,
                 turn: chessai.core.types.Color | None = None,
                 castling_rights: chessai.core.castling.CastlingRights | None = None,
                 en_passant_square: chessai.core.square.Square | None | int = -1,
                 halfmove_clock: int | None = None,
                 fullmove_number: int | None = None,
                 move_stack: list[chessai.core.action.Action] | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        if (board is None):
            raise ValueError("Cannot construct a game state without a board.")

        self.board: chessai.core.board.Board = board
        """ The stateless board which enforces the rules. """

        if (fen is None):
            fen = board.initial_fen

        parsed_fen = chessai.core.fen.parse(fen)

        if (pieces is None):
            pieces = parsed_fen.pieces

        self.pieces: dict[chessai.core.square.Square, chessai.core.piece.Piece]
        """ The current piece positions. """

        if (turn is None):
            turn = parsed_fen.turn

        self.turn: chessai.core.types.Color = turn
        """ The color of the current player. """

        if (castling_rights is None):
            castling_rights = parsed_fen.castling_rights

        self.castling_rights: chessai.core.castling.CastlingRights = castling_rights
        """ The available castling moves. """

        # As None is a valid en passant square, we use a strange default value (-1).
        # If it is any integer, a default value was passed so the user is not trying to override the square to be None.
        if (isinstance(en_passant_square, int)):
            en_passant_square = parsed_fen.en_passant_square

        self.en_passant_square: chessai.core.square.Square | None = en_passant_square
        """
        The en-passant target square, or None.
        Passing None explicitly means to override the value to be None.
        If the default value (any int) is used to signal that the en-passant square from the FEN should be used.
        """

        if (halfmove_clock is None):
            halfmove_clock = parsed_fen.halfmove_clock

        self.halfmove_clock: int = halfmove_clock
        """ The number of plies since the last pawn move or capture (50-move rule). """

        if (fullmove_number is None):
            fullmove_number = parsed_fen.fullmove_number

        self.fullmove_number: int = fullmove_number
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
            pieces            = self.pieces,
            turn              = self.turn,
            castling_rights   = self.castling_rights,
            en_passant_square = self.en_passant_square,
            halfmove_clock    = self.halfmove_clock,
            fullmove_number   = self.fullmove_number,
        )

    # -----------------------------------------------
    # Useful methods for students.
    # -----------------------------------------------

    def get_move_count(self) -> int:
        """ Returns the number of moves in the game. """

        return len(self.move_stack)

    def get_pieces(self, piece_type: chessai.core.types.PieceType, color: chessai.core.types.Color) -> list[chessai.core.square.Square]:
        """ Return the squares occupied by pieces of the given type and color. """

        squares = []

        for (square, piece) in self.pieces.items():
            if ((piece_type != piece.piece_type) or (color != piece.color)):
                continue

            squares.append(square)

        return squares

    def get_search_targets(self) -> list[chessai.core.square.Square]:
        """ Gets the squares on the board that are search targets. """

        return self.board.get_search_targets()

    def get_legal_actions(self) -> list[chessai.core.action.Action]:
        """ Return the list of legal actions for the current player. """

        return self.board.get_legal_moves(self.get_fen())

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Return whether the given action captures a piece. """

        return self.board.is_capture(self.get_fen(), action)

    def get_neighbors(self,
            start_square: chessai.core.square.Square,
            ) -> list[tuple[chessai.core.action.Action, chessai.core.square.Square]]:
        """
        Return all squares reachable from the given square and the action needed to reach each one.
        """

        return self.board.get_neighbors(self.get_fen(), start_square)

    def is_game_over(self) -> bool:
        """ Returns whether the game is over according to the board rules. """

        return self.board.is_game_over(self.get_fen())

    def get_winners(self) -> list[chessai.core.types.Color]:
        """
        Gets the list of winners from the game.
        An empty list signifies the game is in progress or it is a tie.
        """

        return self.board.get_winners(self.get_fen())

    def get_termination_reason(self) -> chessai.core.types.TerminationReason:
        """ Return the reason the game ended. """

        return self.board.get_termination_reason(self.get_fen())

    # -----------------------------------------------
    # State mutation
    # -----------------------------------------------

    def push(self, action: chessai.core.action.Action) -> None:
        """ Updates the gamestate with the given action. """

        if (action not in self.get_legal_actions()):
            raise ValueError(f"Cannot push an illegal action: '{action}'.")

        # TODO(Lucas): Pass key info and not full FEN.
        # TODO(Lucas): Receive key info and update the gamestate accordingly.
        result_fen = self.board.apply_move(self.get_fen(), action)
        parsed = chessai.core.fen.parse(result_fen)

        self.pieces            = parsed.pieces
        self.turn              = parsed.turn
        self.castling_rights   = parsed.castling_rights
        self.en_passant_square = parsed.en_passant_square
        self.halfmove_clock    = parsed.halfmove_clock
        self.fullmove_number   = parsed.fullmove_number
        self.move_stack.append(action)

    def copy(self) -> 'GameState':
        """
        Get a deep copy of this state.

        Child classes are responsible for making any deep copies they need to.
        """

        new_state = copy.copy(self)

        new_state.pieces          = dict(self.pieces)
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

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'board':      self.board.to_dict(),
            'fen':        self.get_fen(),
            'move_stack': [a.to_dict() for a in self.move_stack],
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
            board      = board,
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
        white_piece_count = len(state.get_pieces(piece_type, chessai.core.types.Color.WHITE))
        black_piece_count = len(state.get_pieces(piece_type, chessai.core.types.Color.BLACK))
        piece_count = white_piece_count - black_piece_count

        board_value += (piece_count * piece_value)

    if (state.get_player() == chessai.core.types.Color.WHITE):
        return board_value

    # The piece difference is the opposite for black.
    return -1 * board_value
