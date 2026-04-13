import random
import typing

import chessai.core.action
import chessai.core.gamestate

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

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

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        winners = self.get_winners()

        # Score is based on white's perspective using standard chess scoring.
        if (chessai.core.types.Color.WHITE in winners):
            score = 1.0
        elif (chessai.core.types.Color.BLACK in winners):
            score = 0.0
        else:
            score = 0.5

        return (winners, score)
