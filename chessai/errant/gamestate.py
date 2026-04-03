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
    """ A game state specific to a Knight's Errant game. """

    def __init__(self,
                 board: chessai.core.board.Board | None = None,
                 seed: int = -1,
                 game_over: bool = False,
                 **kwargs: typing.Any) -> None:
        super().__init__(board, seed, game_over, **kwargs)

        self.score: int = 0
        """ The score for the Knight's Errant. """

        # A Knight's Errant problem must have a search target.
        if (len(self.board.get_search_targets()) == 0):
            raise ValueError("Cannot create a errant game state without a search target.")

    def process_turn(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        board = self.get_board()
        board._push(action)

        destination_square = action.get_end_square()
        search_targets = self.board.get_search_targets()
        if (destination_square in search_targets):
            # Get points for reaching a search target.
            self.board.remove_search_target(destination_square)
            self.score += POSITION_POINTS

        # The agent always loses a point each turn.
        self.score -= TIME_PENALTY

    def process_agent_timeout(self, player: bool) -> None:
        # Treat timeouts like crashes.
        self.process_agent_crash(player)

    def process_agent_crash(self, player: bool) -> None:
        super().process_agent_crash(player)

        if (player == chessai.core.types.Color.WHITE):
            self.score += CRASH_POINTS

    def game_complete(self) -> list[bool]:
        search_targets = self.board.get_search_targets()

        # The agent wins if they reach all of the search targets.
        if (len(search_targets) == 0):
            return [bool(chessai.core.types.Color.WHITE)]

        return [bool(chessai.core.types.Color.BLACK)]
