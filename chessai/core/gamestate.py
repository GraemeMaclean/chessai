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
                 board_stack: list[chessai.core.board.Board] | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        if (fen is None):
            fen = DEFAULT_FEN

        # TODO(Lucas): Parse the board size from the FEN so we can give it to the board.
        self.parsed_fen: chessai.core.fen.ParsedFEN = chessai.core.fen.parse(fen)
        """ The full information received from the augmented FEN. """

        self.board: chessai.core.board.Board = chessai.core.board.Board(self.parsed_fen.pieces, self.parsed_fen.num_files, self.parsed_fen.num_ranks)
        """ The board responsible for holding the position of pieces. """

        self.turn: chessai.core.types.Color = self.parsed_fen.turn
        """ The color of the current player. """

        self.castling_rights: chessai.core.castling.CastlingRights = self.parsed_fen.castling_rights
        """ The available castling moves. """

        self.en_passant_coordinate: chessai.core.coordinate.Coordinate | None = self.parsed_fen.en_passant_coordinate
        """ The en-passant target coordinate, or None. """

        self.halfmove_clock: int = self.parsed_fen.halfmove_clock
        """ The number of plies since the last pawn move or capture (50-move rule). """

        self.fullmove_number: int = self.parsed_fen.fullmove_number
        """ Increments after every black move, starting at 1. """

        if (move_stack is None):
            move_stack = []

        self.move_stack: list[chessai.core.action.Action] = move_stack
        """ The ordered history of all actions taken, starting with the oldest action. """

        if (board_stack is None):
            board_stack = []

        self.board_stack: list[chessai.core.board.Board] = board_stack
        """ The ordered history of all boards, starting with the oldest board. """

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
            num_files         = self.board.num_files,
            num_ranks         = self.board.num_ranks,
        )

    # -----------------------------------------------
    # Useful methods for students.
    # -----------------------------------------------

    def get_move_count(self) -> int:
        """ Returns the number of moves in the game. """

        return len(self.move_stack)

    def get_legal_actions(self) -> list[chessai.core.action.Action]:
        """ Return the list of legal actions for the current player. """

        legal_actions: list[chessai.core.action.Action] = []
        pseudo_legal_moves = self._get_pseudo_legal_moves()

        for action in pseudo_legal_moves:
            # Get the piece before pushing (needed for special move processing).
            piece = self.board.get(action.start_coordinate)
            if piece is None:
                continue

            # Generate a successor state to test if this move is legal.
            successor: 'GameState' = self.copy()

            # Apply the move to the test state.
            successor.board.push(action)
            successor._process_special_move(action, piece)

            # Advance the turn for checking for check.
            successor.turn = self.turn.opposite()

            # Check if this move leaves our king in check (making it illegal).
            if (not successor.is_check(self.turn)):
                legal_actions.append(action)

        return legal_actions

    def is_capture(self, action: chessai.core.action.Action) -> bool:
        """ Return whether the given action captures a piece. """

        return self.board.is_capture(action)

    def get_neighbors(self,
                      start_coordinate: chessai.core.coordinate.Coordinate
            ) -> list[tuple[chessai.core.action.Action, chessai.core.coordinate.Coordinate]]:
        """ Get coordinates that the piece at the given coordinate can reach legally, and the action it would take to get there. """

        neighbors: list[tuple[chessai.core.action.Action, chessai.core.coordinate.Coordinate]] = []

        for action in self.get_legal_actions():
            # Skip the legal moves that are not from the starting coordinate.
            if (action.start_coordinate != start_coordinate):
                continue

            neighbors.append((action, action.end_coordinate))

        return neighbors

    def is_check(self, color: chessai.core.types.Color) -> bool:
        """ Determines if the given color, not the state's color, is in check. """

        return False

    def is_checkmate(self) -> bool:
        """ Determines if the current player is in checkmate. """

        legal_actions = self.get_legal_actions()
        return ((len(legal_actions) == 0) and self.is_check(self.turn))

    def is_stalemate(self) -> bool:
        """ Determines if the current player is in stalemate. """

        legal_actions = self.get_legal_actions()
        return ((len(legal_actions) == 0) and (not self.is_check(self.turn)))

    def is_insufficient_material(self):
        """ Processes if there is insufficient material to get a checkmate for all colors. """

        return False

    def is_game_over(self) -> bool:
        """ Returns whether the game is over according to the board rules. """

        if (self.game_over):
            return True

        if (self.is_checkmate()):
            return True

        if (self.is_stalemate()):
            return True

        if (self.is_insufficient_material()):
            return True

        return False

    def get_winners(self) -> list[chessai.core.types.Color]:
        """
        Gets the list of winners from the game.
        An empty list signifies the game is in progress or it is a tie.
        """

        if (self.is_checkmate()):
            return [self.turn.opposite()]

        return []

    def get_termination_reason(self) -> chessai.core.types.TerminationReason:
        """ Return the reason the game ended. """

        return chessai.core.types.TerminationReason.UNKNOWN

    # -----------------------------------------------
    # State mutation
    # -----------------------------------------------

    # We also need to track if an action updates en-passant or castling rights.
    def push(self, action: chessai.core.action.Action) -> None:
        """ Apply action to the game state and update all metadata. """

        piece = self.board.get(action.start_coordinate)
        if (piece is None):
            raise ValueError(f"Cannot push an action from an empty coordinate: '{action.uci()}'.")

        self.board_stack.append(self.board.copy())

        # Allow games to process any special moves.
        is_special_capture, self.en_passant_coordinate = self._process_special_move(action, piece)

        # Apply the action to the board and receive the updates.
        is_capture = self.board.push(action)

        # Allow for subclasses to reset clocks on special actions.
        reset_clock = self._should_reset_halfmove_clock(action, piece)

        # Update the clocks.
        self._progress_state(action, (reset_clock or is_capture or is_special_capture))

    def _progress_state(self, action: chessai.core.action.Action, reset_clock: bool) -> None:
        """ A helper function to update the basic state of the game. """

        if (reset_clock):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if (self.turn == chessai.core.types.Color.BLACK):
            self.fullmove_number += 1

        # Advance the turn.
        self.turn = self.turn.opposite()

        self.move_stack.append(action)

    def _get_pseudo_legal_moves(self) -> list[chessai.core.action.Action]:
        """ Get all of the actions that can be taken on this gamestate, regardless if it violates pins or checks. """

        return self._expand_movement_vectors()

    def _expand_movement_vectors(self) -> list[chessai.core.action.Action]:
        """
        Expands all movement vectors from the pieces on the board.
        Pieces will move until they can capture or reach the end of the board.
        There are no other special rules applied.
        """

        actions: list[chessai.core.action.Action] = []

        for (coordinate, piece) in self.board.pieces.items():
            if (piece.color != self.turn):
                continue

            movement_vectors = piece.move_vectors(coordinate)
            for movement_vector in movement_vectors:
                current_coordinate = coordinate

                num_repetitions = movement_vector.num_repetitions
                while ((num_repetitions == -1) or (num_repetitions > 0)):
                    current_coordinate = current_coordinate.offset(movement_vector.file_delta, movement_vector.rank_delta)
                    if (not self.board._is_within_bounds(current_coordinate)):
                        break

                    occupant = self.board.get(current_coordinate)

                    is_occupied = occupant is not None
                    is_enemy    = (occupant is not None) and (occupant.color != piece.color)
                    is_ally     = (occupant is not None) and (occupant.color == piece.color)

                    # No movement type can move on top of an ally.
                    if (is_ally):
                        break

                    # Push movement types cannot capture.
                    if ((movement_vector.kind == chessai.core.piece.MoveKind.PUSH) and is_occupied):
                        break

                    # Capture movement types must target an enemy.
                    if ((movement_vector.kind == chessai.core.piece.MoveKind.CAPTURE) and (not is_enemy)):
                        break

                    actions.append(chessai.core.action.Action(coordinate, current_coordinate))

                    if (is_occupied):
                        break

                    if (num_repetitions != -1):
                        num_repetitions -= 1

        return actions

    def _should_reset_halfmove_clock(self, action: chessai.core.action.Action, piece: chessai.core.piece.Piece) -> bool:
        """ A helper function that allows gamestates to signal if the halfmove clock should be reset after an action. """

        return False

    def _process_special_move(self,
                              action: chessai.core.action.Action,
                              piece: chessai.core.piece.Piece)-> tuple[bool, chessai.core.coordinate.Coordinate | None]:
        """ A helper function that allows gamestates to do any additional processing for special moves. """

        return False, None

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

        # If the game is over, don't do anything.
        # This case can come up when planning agent actions and generating successors.
        if (self.is_game_over()):
            return

        self.process_turn(action, rng, **kwargs)
        return

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'fen':         self.get_fen(),
            'move_stack':  [action.to_dict() for action in self.move_stack],
            'board_stack': [board.to_dict() for board in self.board_stack],
            'seed':        self.seed,
            'game_over':   self.game_over,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        raw_move_stack = data.get('move_stack', [])
        move_stack = []
        for move in raw_move_stack:
            move_stack.append(move.from_dict())

        raw_board_stack = data.get('board_stack', [])
        board_stack = []
        for board in raw_board_stack:
            board_stack.append(board.from_dict())

        return cls(
            fen         = data.get('fen', None),
            move_stack  = move_stack,
            board_stack = board_stack,
            seed        = data.get('seed', -1),
            game_over   = data.get('game_over', False),
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
