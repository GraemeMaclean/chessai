import edq.testing.unittest

import chessai.core.gamestate
import chessai.core.coordinate
import chessai.core.action
import chessai.core.types

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test chessai.core.gamestate.GameState functionality. """

    def test_fen_roundtrip(self):
        """ Test the gamestate preserves the starting FEN. """

        state = chessai.core.gamestate.GameState()
        fen = state.get_fen()
        assert fen == chessai.core.gamestate.DEFAULT_FEN

    def test_default_state_properties(self):
        """ Test starting state has valid state. """

        state = chessai.core.gamestate.GameState()

        assert state.turn == chessai.core.types.Color.WHITE
        assert state.get_move_count() == 0
        assert state.game_over is False

    def test_starting_position_has_legal_moves(self):
        """ Test default board has legal moves. """

        state = chessai.core.gamestate.GameState()

        moves = state.get_legal_actions()

        # This should NEVER be zero in a correct implementation
        assert len(moves) > 0, "Legal moves should not be empty in starting position"

    def test_legal_moves_are_consistent(self):
        """ Test all legal moves are well formed. """

        state = chessai.core.gamestate.GameState()

        moves = state.get_legal_actions()

        # Ensure all moves have valid structure
        for move in moves:
            assert move.start_coordinate is not None
            assert move.end_coordinate is not None

    def test_push_updates_turn(self):
        """ Test pushing an action advances the turn. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        original_turn = state.turn

        state.push(move)

        assert state.turn != original_turn

    def test_push_updates_move_stack(self):
        """ Test pushing an action updates the move stack. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        state.push(move)

        assert state.get_move_count() == 1
        assert state.move_stack[-1] == move

    def test_push_updates_board_stack(self):
        """ Test pushing an action updates the board stack. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        state.push(move)

        assert len(state.board_stack) == 1

    def test_generate_successor_does_not_modify_original(self):
        """ Test generate successor properly deep copies the state. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]

        successor = state.generate_successor(move)

        # Original should remain unchanged
        assert state.get_move_count() == 0
        assert successor.get_move_count() == 1

    def test_successor_turn_switch(self):
        """ Test turns are properly switched for each successor. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        successor = state.generate_successor(move)

        assert successor.turn != state.turn

    def test_get_neighbors_filters_by_start_coordinate(self):
        """ Test get neighbors returns actions only from the start coordinate. """

        state = chessai.core.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        start = move.start_coordinate

        neighbors = state.get_neighbors(start)

        for (action, _) in neighbors:
            assert action.start_coordinate == start

    def test_push_illegal_move_raises(self):
        """ Test illegal moves raise errors. """

        state = chessai.core.gamestate.GameState()

        fake_move = chessai.core.action.Action(
            start_coordinate = chessai.core.coordinate.Coordinate(0, 0),
            end_coordinate = chessai.core.coordinate.Coordinate(0, 5),
        )

        with self.assertRaises(ValueError):
            state.push(fake_move)

    def test_copy_is_independent(self):
        """ Test that copying a gamestate is a deep copy. """

        state = chessai.core.gamestate.GameState()
        state_copy = state.copy()

        assert state is not state_copy
        assert state.board is not state_copy.board
        assert state.move_stack is not state_copy.move_stack
