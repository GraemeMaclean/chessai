import edq.testing.unittest

import chessai.core.gamestate
import chessai.core.coordinate
import chessai.core.action
import chessai.core.types

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test chessai.core.gamestate.GameState functionality. """

    def test_default_state(self):
        """ Test default gamestate for some basic properties. """

        state = chessai.core.gamestate.GameState()

        # Basic State
        self.assertEqual(state.get_fen(), chessai.core.gamestate.DEFAULT_FEN)
        self.assertEqual(state.turn, chessai.core.types.Color.WHITE)

        # Core Functions
        self.assertFalse(state.is_game_over())
        self.assertEqual(state.get_move_count(), 0)

        # Legal moves
        legal_actions = state.get_legal_actions()
        self.assertNotEqual(len(legal_actions), 0)

        # Make sure each action is well-formed.
        for legal_action in legal_actions:
            self.assertIsNotNone(legal_action.start_coordinate)
            self.assertIsNotNone(legal_action.end_coordinate)
            self.assertNotEqual(legal_action.start_coordinate, legal_action.end_coordinate)

        # Push an action and observe the resulting state.
        chosen_action = legal_actions[0]
        original_board = state.board.copy()
        state.push(chosen_action)

        # Check it updated the basic state.
        self.assertEqual(state.turn, chessai.core.types.Color.BLACK)
        self.assertNotEqual(state.get_fen(), chessai.core.gamestate.DEFAULT_FEN)

        # Check state history.
        self.assertEqual(state.get_move_count(), 1)
        self.assertEqual(state.move_stack[-1], chosen_action)
        self.assertEqual(len(state.board_stack), 1)
        self.assertEqual(state.board_stack[-1], original_board)

    def test_generate_successor_does_not_modify_original(self):
        """ Test generate successor properly deep copies the state. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]

        successor = state.generate_successor(move)

        # Original should remain unchanged
        self.assertEqual(state.get_move_count(), 0)
        self.assertEqual(successor.get_move_count(), 1)
        self.assertNotEqual(state.turn, successor.turn)

    def test_get_neighbors_filters_by_start_coordinate(self):
        """ Test get neighbors returns actions only from the start coordinate. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        start = move.start_coordinate

        neighbors = state.get_neighbors(start)

        for (action, _) in neighbors:
            self.assertEqual(action.start_coordinate, start)

    def test_push_illegal_move_raises(self):
        """ Test illegal moves raise errors. """

        state = chessai.core.gamestate.GameState()

        fake_move = chessai.core.action.Action()

        with self.assertRaises(ValueError):
            state.push(fake_move)
