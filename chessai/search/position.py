import typing

import chessai.core.action
import chessai.core.gamestate
import chessai.core.search
import chessai.search.common
import chessai.util.alias

DEFAULT_GOAL_POSITION: chessai.core.board.Square = chessai.core.board.Square.from_file_rank(1, 1)

class PositionSearchNode(chessai.core.search.SearchNode):
    """
    A search node for the position search problem.
    The state for this problem is simple,
    it is just the current position being searched.
    """

    def __init__(self, position: chessai.core.board.Square) -> None:
        self.position: chessai.core.board.Square = position
        """ The current position being searched. """

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, PositionSearchNode)):
            return False

        return (self.position < other.position)

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, PositionSearchNode)):
            return False

        return (self.position == other.position)

    def __hash__(self) -> int:
        return hash(self.position)

class PositionSearchProblem(chessai.core.search.SearchProblem[PositionSearchNode]):
    """
    A search problem for finding a specific position on the board.
    """

    def __init__(self,
            game_state: chessai.core.gamestate.GameState,
            goal_position: chessai.core.board.Square | None = None,
            start_position: chessai.core.board.Square | None = None,
            cost_function: chessai.core.search.CostFunction | str = chessai.util.alias.COST_FUNC_UNIT.long,
            **kwargs: typing.Any) -> None:
        """
        Create a positional search problem.

        If no goal position is provided, the board's search target will be used,
            if that does not exist, then DEFAULT_GOAL_POSITION will be used.
        If no start position is provided, the current agent's position will be used.
        If no cost function is provided, chessai.util.alias.COST_FUNC_UNIT will be used.
        """

        super().__init__()

        self.board: chessai.core.board.Board = game_state.board
        """ Keep track of the board so we can navigate walls. """

        if (goal_position is None):
            if (self.board.search_target is not None):
                goal_position = self.board.search_target
            else:
                goal_position = DEFAULT_GOAL_POSITION

        self.goal_position: chessai.core.board.Square = goal_position
        """ The position to search for. """

        if (start_position is None):
            start_position = game_state.get_white_knight_position()

        if (start_position is None):
            raise ValueError("Could not find starting position.")

        self.start_position: chessai.core.board.Square = start_position
        """ The position to start from. """

        if (isinstance(cost_function, str)):
            cost_function = typing.cast(chessai.core.search.CostFunction, chessai.util.reflection.fetch(cost_function))

        self._cost_function: chessai.core.search.CostFunction = cost_function
        """ The function used to score search nodes. """

    def get_starting_node(self) -> PositionSearchNode:
        return PositionSearchNode(self.start_position)

    def is_goal_node(self, node: PositionSearchNode) -> bool:
        return (self.goal_position == node.position)

    def complete(self, goal_node: PositionSearchNode) -> None:
        # Mark the final node in the history.
        self.position_history.append(goal_node.position)

    def get_successor_nodes(self, node: PositionSearchNode) -> list[chessai.core.search.SuccessorInfo]:
        successors = []

        # Check all the non-wall neighbors.
        for (action, position) in self.board.get_neighbors(node.position):
            next_node = PositionSearchNode(position)
            cost = self._cost_function(next_node)

            successors.append(chessai.core.search.SuccessorInfo(next_node, action, cost))

        # Do bookkeeping on the states/positions we visited.
        self.expanded_node_count += 1
        if (node not in self.visited_nodes):
            self.position_history.append(node.position)

        return successors
