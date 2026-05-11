"""
Common search utilities.
"""

import typing

import chessai.core.board
import chessai.core.search
import chessai.core.coordinate

def unit_cost_function(node: chessai.core.search.SearchNode, **kwargs: typing.Any) -> float:
    """
    One of the most simple search functions,
    always return 1 (a single unit).
    """

    return 1.0

def longitudinal_cost_function(node: chessai.core.search.SearchNode, base: float = 1.0, **kwargs: typing.Any) -> float:
    """
    If the search node has a "position" attribute,
    use that to assign a score based on its longitudinal position (its file).
    If there is no "position" attribute, just use unit cost.

    The cost will be `base ^ node.position.file`.
    """

    if (hasattr(node, 'position') and isinstance(getattr(node, 'position'), chessai.core.coordinate.Coordinate)):
        return float(base ** getattr(node, 'position').file)

    return unit_cost_function(node, **kwargs)

def stay_east_cost_function(node: chessai.core.search.SearchNode, **kwargs: typing.Any) -> float:
    """
    A longitudinal_cost_function that prioritizes staying east.
    """

    return longitudinal_cost_function(node, base = 0.5)

def stay_west_cost_function(node: chessai.core.search.SearchNode, **kwargs: typing.Any) -> float:
    """
    A longitudinal_cost_function that prioritizes staying west.
    """

    return longitudinal_cost_function(node, base = 2.0)

def null_heuristic(node: chessai.core.search.SearchNode, problem: chessai.core.search.SearchProblem, **kwargs: typing.Any) -> float:
    """ A trivial heuristic that returns a constant. """

    return 0.0
