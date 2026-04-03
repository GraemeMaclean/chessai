import typing

import chessai.core.action
import chessai.core.gamestate
import chessai.core.search
import chessai.core.square
import chessai.core.types
import chessai.search.common
import chessai.util.alias

class PositionSearchNode(chessai.core.search.SearchNode):
    """
    A search node for the position search problem.
    The state for this problem is simple,
    it is just the current position being searched.
    """

    def __init__(self, position: chessai.core.square.Square, board: chessai.core.board.Board) -> None:
        self.position: chessai.core.square.Square = position
        """ The current position being searched. """

        self.board: chessai.core.board.Board = board
        """ The snapshot of the board at this search node. """

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
            goal_positions: list[chessai.core.square.Square] | None = None,
            start_position: chessai.core.square.Square | None = None,
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
        """ Keep track of the board so we can navigate. """

        if (goal_positions is None):
            if (len(self.board.search_targets) == 0):
                raise ValueError("Cannot create a position search problem without at least one goal position.")

            goal_positions = self.board.search_targets

        self.goal_positions: list[chessai.core.square.Square] = goal_positions
        """ The positions to search for. """

        if (start_position is None):
            # TODO(Lucas): Will need to generalize this once we open up the piece offerings.
            positions = game_state.get_board().get_pieces(chessai.core.types.PieceType.KNIGHT, chessai.core.types.Color.WHITE)
            if (len(positions) > 0):
                start_position = positions[0]

        if (start_position is None):
            raise ValueError("Could not find starting position.")

        self.start_position: chessai.core.square.Square = start_position
        """ The position to start from. """

        self.start_board: chessai.core.board.Board = self.board.copy()
        """ The board the problem started from. """

        if (isinstance(cost_function, str)):
            cost_function = typing.cast(chessai.core.search.CostFunction, chessai.util.reflection.fetch(cost_function))

        self._cost_function: chessai.core.search.CostFunction = cost_function
        """ The function used to score search nodes. """

    def get_starting_node(self) -> PositionSearchNode:
        return PositionSearchNode(self.start_position, self.start_board)

    def is_goal_node(self, node: PositionSearchNode) -> bool:
        return (node.position in self.goal_positions)
        # return (self.goal_position == node.position)

    def complete(self, goal_node: PositionSearchNode) -> None:
        # Mark the final node in the history.
        self.position_history.append(goal_node.position)

    def get_successor_nodes(self, node: PositionSearchNode) -> list[chessai.core.search.SuccessorInfo]:
        successors = []

        # Check all the neighbors.
        for (action, position) in node.board.get_neighbors(node.position):
            next_board = node.board.copy()
            next_board._push(action)

            # Push a null move for black.
            next_board._push(chessai.core.action.Action())

            next_node = PositionSearchNode(position, next_board)
            cost = self._cost_function(next_node)

            successors.append(chessai.core.search.SuccessorInfo(next_node, action, cost))

        # Do bookkeeping on the states/positions we visited.
        self.expanded_node_count += 1
        if (node not in self.visited_nodes):
            self.position_history.append(node.position)

        return successors
