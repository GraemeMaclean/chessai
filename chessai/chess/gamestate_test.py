import edq.testing.unittest

import chessai.chess.gamestate
import chessai.core.gamestate
import chessai.core.coordinate
import chessai.core.action
import chessai.core.types

class GameStateTest(edq.testing.unittest.BaseTest):
    """ Test chessai.chess.gamestate.GameState functionality. """

    def test_default_state(self):
        """ Test default gamestate for some basic properties. """

        state = chessai.chess.gamestate.GameState()

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

        state = chessai.chess.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]

        successor = state.generate_successor(move)

        # Original should remain unchanged
        self.assertEqual(state.get_move_count(), 0)
        self.assertEqual(successor.get_move_count(), 1)
        self.assertNotEqual(state.turn, successor.turn)

    def test_get_neighbors_filters_by_start_coordinate(self):
        """ Test get neighbors returns actions only from the start coordinate. """

        state = chessai.chess.gamestate.GameState()
        moves = state.get_legal_actions()

        move = moves[0]
        start = move.start_coordinate

        neighbors = state.get_neighbors(start)

        for (action, _) in neighbors:
            self.assertEqual(action.start_coordinate, start)

    def test_push_illegal_move_raises(self):
        """ Test illegal moves raise errors. """

        state = chessai.chess.gamestate.GameState()

        fake_move = chessai.core.action.Action(
            start_coordinate = chessai.core.coordinate.Coordinate(0, 0),
            end_coordinate = chessai.core.coordinate.Coordinate(0, 5),
        )

        with self.assertRaises(ValueError):
            state.push(fake_move)

    def test_legal_moves(self):
        """ Test the legal move generator. """

        # [(FEN, expected_moves, is_checkmate, is_stalemate), ...]
        test_cases: list[tuple[str | None, list[str], bool, bool]] = [
            (
                None,
                [
                    'a2a3', 'a2a4', 'b2b3', 'b2b4', 'c2c3', 'c2c4',
                    'd2d3', 'd2d4', 'e2e3', 'e2e4', 'f2f3', 'f2f4',
                    'g2g3', 'g2g4', 'h2h3', 'h2h4', 'b1a3', 'b1c3',
                    'g1f3', 'g1h3',
                ],
                False,
                False,
            ),
            (
                'rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3',
                [],
                True,
                False,
            ),
            (
                'r1bqkbnr/pppp1Qpp/8/4P3/2Bn4/8/PPPP1PPP/RNB1KBNR b KQkq - 0 5',
                [],
                True,
                False,
            ),
            (
                '7k/6R1/8/5N2/7R/8/8/K7 b - - 0 1',
                [],
                True,
                False,
            ),
            (
                'rnb1kbnr/pppp1pPp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3',
                [],
                True,
                False,
            ),
            (
                '4R1k1/p4ppp/8/8/8/5B2/PP1r1PPP/R5K1 b - - 0 1',
                [],
                True,
                False,
            ),
            (
                '7k/p4p2/P4P2/1P6/6R1/3B4/6PP/R5K1 b - - 0 1',
                [],
                False,
                True,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (start_fen, uci_moves, checkmate, stalemate) = test_case

                expected_actions: list[chessai.core.action.Action] = []
                for uci_move in uci_moves:
                    expected_actions.append(chessai.core.action.Action.from_uci(uci_move))

                state = chessai.chess.gamestate.GameState(fen = start_fen)

                self.assertEqual(state.is_checkmate(), checkmate)
                self.assertEqual(state.is_stalemate(), stalemate)

                actual_actions = state.get_legal_actions()
                self.assertEqual(len(actual_actions), len(expected_actions))

                for expected_action in expected_actions:
                    self.assertIn(expected_action, actual_actions)


    def test_final_action(self):
        """ Test mate in 1 or stalemate in 1. """

        # [(FEN, action, is_checkmate, is_stalemate), ...]
        test_cases: list[tuple[str, chessai.core.action.Action, bool, bool]] = [
            (
                '8/p6k/P7/1P3Pp1/3B4/6R1/3B2PP/R5K1 w - g6 0 1',
                chessai.core.action.Action.from_uci('f5g6'),
                True,
                False,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (start_fen, action, checkmate, stalemate) = test_case

                state = chessai.chess.gamestate.GameState(fen = start_fen)

                # Check that it is not a checkmate or stalemate before the move.
                self.assertEqual(state.is_checkmate(), False)
                self.assertEqual(state.is_stalemate(), False)

                print(state.get_fen())
                state.process_turn(action)
                print(state.get_fen())

                # Check that it is a checkmate or stalemate after the move.
                self.assertEqual(state.is_checkmate(), checkmate)
                self.assertEqual(state.is_stalemate(), stalemate)
