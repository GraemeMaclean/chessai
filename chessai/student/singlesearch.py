"""
In this file, you will implement code relating to simple single-agent searches.

For Assignment 1, you will be working on the Knight's Errant problem:
given a starting square and a target square on a chessboard, find the
minimum number of moves for a knight to travel between them.

You will implement four search algorithms:
  - Depth First Search (DFS)
  - Breadth First Search (BFS)
  - Uniform Cost Search (UCS)
  - A* Search

You will also implement heuristics for A* and analyze their admissibility
and consistency in your written report.
"""

import random
import typing

import chessai.core.search
import chessai.search.common

def depth_first_search(
        problem: chessai.core.search.SearchProblem,
        heuristic: chessai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> chessai.core.search.SearchSolution:
    """
    A chessai.core.search.SearchProblemSolver that implements depth first search (DFS).
    This means that it will search the deepest nodes in the search tree first.
    See: https://en.wikipedia.org/wiki/Depth-first_search .
    """

    # *** Your Code Here ***
    raise NotImplementedError('depth_first_search')

def breadth_first_search(
        problem: chessai.core.search.SearchProblem,
        heuristic: chessai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> chessai.core.search.SearchSolution:
    """
    A chessai.core.search.SearchProblemSolver that implements breadth first search (BFS).
    This means that it will search nodes based on what level in search tree they appear.
    See: https://en.wikipedia.org/wiki/Breadth-first_search .
    """

    # *** Your Code Here ***
    raise NotImplementedError('breadth_first_search')

def uniform_cost_search(
        problem: chessai.core.search.SearchProblem,
        heuristic: chessai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> chessai.core.search.SearchSolution:
    """
    A chessai.core.search.SearchProblemSolver that implements uniform cost search (UCS).
    This means that it will search nodes with a lower total cost first.
    See: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Practical_optimizations_and_infinite_graphs .
    """

    # *** Your Code Here ***
    raise NotImplementedError('uniform_cost_search')

def astar_search(
        problem: chessai.core.search.SearchProblem,
        heuristic: chessai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> chessai.core.search.SearchSolution:
    """
    A chessai.core.search.SearchProblemSolver that implements A* search (pronounced "A Star search").
    This means that it will search nodes with a lower combined cost and heuristic first.
    See: https://en.wikipedia.org/wiki/A*_search_algorithm .
    """

    # *** Your Code Here ***
    raise NotImplementedError('astar_search')


class KnightsErrantSearchNode(chessai.core.search.SearchNode):
    """
    A search node representing a state in the Knight's Errant problem.

    The state must encode everything the search needs to determine:
      1. Where the knight currently is.
      2. Whether the goal has been reached.

    For the basic Knight's Errant problem (single target square),
    the position alone is sufficient. But think carefully:
    if you were to extend this to visiting multiple squares,
    what additional information would your state need to track?
    """

    def __init__(self) -> None:
        """
        Construct a search node for the Knight's Errant problem.
        You may add arguments to this constructor as needed.
        """

        # *** Your Code Here ***
        # Remember that you can also add arguments to your constructor.

class KnightsErrantSearchProblem(chessai.core.search.SearchProblem[KnightsErrantSearchNode]):
    """
    A search problem for moving a knight from a start square to a target square
    in the minimum number of moves.

    The board is a standard 8x8 chessboard. Squares are represented as
    (file, rank) tuples where file and rank are both in [0, 7].
    For example, (0, 0) is a1, (7, 7) is h8.

    A knight moves in an 'L' shape: two squares in one direction and
    one square perpendicular. A knight on (r, c) can reach up to 8 squares.
    """

    def __init__(self,
            start: tuple[int, int],
            target: tuple[int, int],
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self._start = start
        self._target = target

        # *** Your Code Here (if needed) ***

    def get_starting_node(self) -> KnightsErrantSearchNode:
        # *** Your Code Here ***
        raise NotImplementedError('KnightsErrantSearchProblem.get_starting_node')

    def is_goal_node(self, node: KnightsErrantSearchNode) -> bool:
        # *** Your Code Here ***
        raise NotImplementedError('KnightsErrantSearchProblem.is_goal_node')

    def get_successor_nodes(self, node: KnightsErrantSearchNode) -> list[chessai.core.search.SuccessorInfo]:
        """
        Return a list of (successor_node, action, cost) tuples representing
        all valid moves from the current node.

        Remember that a knight cannot move off the board.
        """

        # *** Your Code Here ***
        raise NotImplementedError('KnightsErrantSearchProblem.get_successor_nodes')

def knights_errant_heuristic(
        node: KnightsErrantSearchNode,
        problem: KnightsErrantSearchProblem,
        **kwargs: typing.Any) -> float:
    """
    A heuristic for the Knight's Errant problem.

    Your heuristic must be ADMISSIBLE: it must never overestimate the
    true cost to reach the goal. Formally, for all nodes n:
        h(n) <= h*(n)
    where h*(n) is the true optimal cost from n to the goal.

    For full credit, your heuristic should also be CONSISTENT (monotone):
        h(n) <= cost(n, n') + h(n')
    for every successor n' of n.

    You must prove admissibility (and ideally consistency) in your written report.
    A non-trivial heuristic that is both admissible and consistent and meaningfully
    reduces the number of nodes expanded compared to UCS will receive full credit.

    Hint: Think about the minimum possible number of moves a knight could ever
    make to close a given distance, ignoring board boundaries.
    """

    # *** Your Code Here ***
    return chessai.search.common.null_heuristic(node, problem)  # Default: trivial heuristic.
