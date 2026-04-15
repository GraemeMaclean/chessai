import random
import typing

import chessai.core.action
import chessai.core.board
import chessai.core.gamestate

TIME_PENALTY: int = 1
""" Number of points lost each round. """

POSITION_POINTS: int = 10
""" Points for reaching a search position. """

BOARD_CLEAR_POINTS: int = 500
""" Points for reaching all search positions on the board. """

LOSE_POINTS: int = -500
""" Points for not finding a solution. """

CRASH_POINTS = -1000000
""" Points for crashing the game. """

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a Tour game. """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 fen: str | None = None,
                 pieces: dict[chessai.core.coordinate.Coordinate, chessai.core.piece.Piece] | None = None,
                 turn: chessai.core.types.Color | None = None,
                 castling_rights: chessai.core.castling.CastlingRights | None = None,
                 en_passant_square: chessai.core.coordinate.Coordinate | None | int = -1,
                 halfmove_clock: int | None = None,
                 fullmove_number: int | None = None,
                 move_stack: list[chessai.core.action.Action] | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 search_targets: list[chessai.core.coordinate.Coordinate] | dict[str, typing.Any] | None = None,
                 **kwargs: typing.Any) -> None:
        super().__init__(board, fen, pieces, turn, castling_rights,
                 en_passant_square, halfmove_clock, fullmove_number,
                 move_stack, seed, game_over, **kwargs)

        self.score: int = 0
        """ The score for the Tour. """

        if (search_targets is None):
            search_targets = []

        self.search_targets: list[chessai.core.coordinate.Coordinate] = search_targets  # type: ignore
        """ The targets of the piece tour search. """

        # Convert the string case into the dict case.
        if (isinstance(search_targets, str)):
            search_targets = {
                chessai.core.coordinate.COORDINATES_KEY: search_targets
            }

        if (isinstance(search_targets, dict)):
            self.search_targets = chessai.core.coordinate.squares_from_dict(search_targets)

        # A Tour problem must have at least one search target.
        if (len(self.search_targets) == 0):
            raise ValueError("Cannot create a Tour game state without at least one search target.")

    def remove_search_target(self, square: chessai.core.coordinate.Coordinate) -> None:
        """
        Remove a search target from the gamestate.
        If the square is not a search target, the state is unchanged.
        """

        if (square not in self.search_targets):
            return

        self.search_targets.remove(square)

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

        destination_square = action.end_square
        search_targets = self.board.get_search_targets()
        if (destination_square in search_targets):
            # Get points for reaching a search target.
            self.board.remove_search_target(destination_square)
            self.score += POSITION_POINTS

        # The agent always loses a point each turn.
        self.score -= TIME_PENALTY

    def process_agent_timeout(self, player: chessai.core.types.Color) -> None:
        # Treat timeouts like crashes.
        self.process_agent_crash(player)

    def process_agent_crash(self, player: chessai.core.types.Color) -> None:
        super().process_agent_crash(player)

        if (player == chessai.core.types.Color.WHITE):
            self.score += CRASH_POINTS

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        search_targets = self.board.get_search_targets()

        # The agent wins if they reach all of the search targets.
        if (len(search_targets) == 0):

            self.score += BOARD_CLEAR_POINTS

            return ([chessai.core.types.Color.WHITE], self.score)

        return ([chessai.core.types.Color.BLACK], self.score)
