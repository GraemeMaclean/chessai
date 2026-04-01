import random
import typing

import chessai.core.search

def maze_tiny_search(
        problem: chessai.core.search.SearchProblem,
        heuristic: chessai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> chessai.core.search.SearchSolution:
    """
    Output a very specific set of actions meant for the `knights-errant-base` board.
    This (fake) search will generally not work on other boards.
    """

    actions = [
        chessai.core.action.Action(),
    ]

    return chessai.core.search.SearchSolution(actions, 0.0)
