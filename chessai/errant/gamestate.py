import random
import typing

import chessai.core.action
import chessai.core.board
import chessai.core.gamestate

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
        if (self.board.get_search_target() is None):
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

    def process_agent_timeout(self, player: bool) -> None:
        # Treat timeouts like crashes.
        self.process_agent_crash(player)

    def process_agent_crash(self, player: bool) -> None:
        super().process_agent_crash(player)

        if (player == chessai.core.types.Color.WHITE):
            self.score += CRASH_POINTS

    def game_complete(self) -> list[bool]:
        search_target = self.board.get_search_target()

        # The Knight wins if they reach the target square.
        if (search_target in self.board.get_pieces(chessai.core.types.PieceType.KNIGHT, chessai.core.types.Color.WHITE)):
            return [bool(chessai.core.types.Color.WHITE)]

        return [bool(chessai.core.types.Color.BLACK)]
