import edq.testing.unittest

import chessai.chess.piece
import chessai.core.action
import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

class ActionTest(edq.testing.unittest.BaseTest):
    """ Test Action functionality. """

    def test_uci(self):
        """ Test Action.uci(). """

        # [(start_coordinate, end_coordinate, promotion, uci), ...]
        test_cases: list[tuple[
            chessai.core.coordinate.Coordinate,
            chessai.core.coordinate.Coordinate,
            chessai.core.piece.Piece | None,
            str
        ]] = [
            # Base
            (
                chessai.core.coordinate.Coordinate(0, 0),
                chessai.core.coordinate.Coordinate(1, 1),
                None,
                'a1b2',
            ),
            (
                chessai.core.coordinate.Coordinate(5, 6),
                chessai.core.coordinate.Coordinate(5, 7),
                None,
                'f7f8',
            ),
            (
                chessai.core.coordinate.Coordinate(3, 4),
                chessai.core.coordinate.Coordinate(5, 6),
                None,
                'd5f7',
            ),
            (
                chessai.core.coordinate.Coordinate(26, 0),
                chessai.core.coordinate.Coordinate(27, 9),
                None,
                'aa1ab10',
            ),

            # UCI Null Actions
            (
                chessai.core.coordinate.NULL_COORDINATE,
                chessai.core.coordinate.NULL_COORDINATE,
                None,
                '0000',
            ),

            # Promotions
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Queen(color = chessai.core.types.Color.BLACK),
                'e7e8q',
            ),
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Rook(color = chessai.core.types.Color.BLACK),
                'e7e8r',
            ),
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Bishop(color = chessai.core.types.Color.BLACK),
                'e7e8b',
            ),
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Knight(color = chessai.core.types.Color.BLACK),
                'e7e8n',
            ),
        ]

        for (i, (start_coordinate, end_coordinate, promotion, expected)) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                action = chessai.core.action.Action(start_coordinate, end_coordinate, promotion)
                self.assertEqual(expected, action.uci())

    def test_from_uci(self):
        """ Test Action.from_uci(). """

        # [(uci, error_substring, start_coordinate, end_coordinate, promotion), ...]
        test_cases: list[tuple[
            str,
            str | None,
            chessai.core.coordinate.Coordinate | None,
            chessai.core.coordinate.Coordinate | None,
            chessai.core.piece.Piece | None,
        ]] = [
            # Base
            (
                'a1b2',
                None,
                chessai.core.coordinate.Coordinate(0, 0),
                chessai.core.coordinate.Coordinate(1, 1),
                None,
            ),
            (
                'f7f8',
                None,
                chessai.core.coordinate.Coordinate(5, 6),
                chessai.core.coordinate.Coordinate(5, 7),
                None,
            ),
            (
                'd5f7',
                None,
                chessai.core.coordinate.Coordinate(3, 4),
                chessai.core.coordinate.Coordinate(5, 6),
                None,
            ),
            (
                'aa1ab10',
                None,
                chessai.core.coordinate.Coordinate(26, 0),
                chessai.core.coordinate.Coordinate(27, 9),
                None,
            ),

            # UCI Null Actions
            (
                '0000',
                None,
                chessai.core.coordinate.NULL_COORDINATE,
                chessai.core.coordinate.NULL_COORDINATE,
                None,
            ),
            (
                chessai.core.action.UCI_NULL_ACTION,
                None,
                chessai.core.coordinate.NULL_COORDINATE,
                chessai.core.coordinate.NULL_COORDINATE,
                None,
            ),

            # Promotions
            (
                'e7e8q',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Queen(color = chessai.core.types.Color.BLACK),
            ),
            (
                'e7e8r',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Rook(color = chessai.core.types.Color.BLACK),
            ),
            (
                'e7e8b',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Bishop(color = chessai.core.types.Color.BLACK),
            ),
            (
                'e7e8n',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.chess.piece.Knight(color = chessai.core.types.Color.BLACK),
            ),

            # Promotion on large board (file > 'z').
            (
                'aa1ab2q',
                None,
                chessai.core.coordinate.Coordinate(26, 0),
                chessai.core.coordinate.Coordinate(27, 1),
                chessai.chess.piece.Queen(color = chessai.core.types.Color.BLACK),
            ),

            # Errors
            (
                '',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-zA-Z]?)$', got: ''.",
                None,
                None,
                None,
            ),
            (
                'a1',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-zA-Z]?)$', got: 'a1'.",
                None,
                None,
                None,
            ),
            (
                'a1b2c3',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-zA-Z]?)$', got: 'a1b2c3'.",
                None,
                None,
                None,
            ),

            # Multiple trailing characters.
            (
                'e7e8qq',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-zA-Z]?)$', got: 'e7e8qq'.",
                None,
                None,
                None,
            ),

            # Unknown promotion symbol.
            (
                'e7e8x',
                "Unknown promotion piece symbol 'x' in UCI string: 'e7e8x'.",
                None,
                None,
                None,
            ),
        ]

        for (i, (uci, error_substring, expected_start, expected_end, expected_promotion)) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                try:
                    action = chessai.core.action.Action.from_uci(uci)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex))
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(expected_start, action.start_coordinate)
                self.assertEqual(expected_end, action.end_coordinate)
                self.assertEqual(expected_promotion, action.promotion)

    def test_round_trip(self):
        """ Test Action round-trip conversion (uci -> object -> uci). """

        test_cases: list[str] = [
            # Base
            'a1b2',
            'd5f7',
            'aa1ab10',
            '0000',

            # Promotions
            'e7e8q',
            'e7e8r',
            'e7e8b',
            'e7e8n',
            'aa1ab2q',

            # Custom Actions
            'Propose Draw',
            'Accept Draw',
            'Reject Draw',
            'Forfeit',
        ]

        for (i, uci) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                action = chessai.core.action.Action.from_uci(uci)
                self.assertEqual(uci, action.uci())

    def test_null_action(self):
        """ Test NULL_ACTION constant. """

        action = chessai.core.action.NULL_ACTION

        self.assertEqual(-1, action.start_coordinate.file)
        self.assertEqual(-1, action.start_coordinate.rank)
        self.assertEqual(-1, action.end_coordinate.file)
        self.assertEqual(-1, action.end_coordinate.rank)
        self.assertIsNone(action.promotion)

        self.assertEqual(chessai.core.action.Action(), chessai.core.action.NULL_ACTION)

    def test_actions_list_from_dict(self):
        """ Test getting a list of list of actions from a dict. """

        # [(input, expected_output), ...]
        test_cases: list[tuple[str, list[list[str]]]] = [
            (
                "[]",
                [],
            ),
            (
                "[[]]",
                [[]],
            ),
            (
                "[[\"a2a3\"]]",
                [['a2a3']],
            ),
            (
                "[[\"a2a3\",\"a3a4\"]]",
                [['a2a3', 'a3a4']],
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (raw_input, raw_expected_actions) = test_case

                expected: list[list[chessai.core.action.Action]] = []
                for raw_expected_action_list in raw_expected_actions:
                    clean_action_list = []
                    for raw_expected_action in raw_expected_action_list:
                        clean_action_list.append(chessai.core.action.Action.from_uci(raw_expected_action))

                    expected.append(clean_action_list)

                actions_input = {
                    chessai.core.action.ACTION_KEY: raw_input,
                }

                actual = chessai.core.action.actions_list_from_dict(actions_input)
                self.assertEqual(actual, expected)

    def test_actions_sorting(self):
        """ Test sorting actions. """

        # [(input, expected_output), ...]
        test_cases: list[tuple[list[chessai.core.action.Action], list[chessai.core.action.Action]]] = [
            # End rank.
            (
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                ],
            ),
            (
                [
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1a1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                ],
            ),

            # Start rank.
            (
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                ],
            ),
            (
                [
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("a1a1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                ],
            ),

            # End file.
            (
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1b1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1b1"),
                ],
            ),
            (
                [
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a1a1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1b1"),
                ],
            ),

            # Start file.
            (
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
            ),
            (
                [
                    chessai.core.action.Action.from_uci("b1a1"),
                    chessai.core.action.Action.from_uci("a1a1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
            ),

            # All normal actions.
            (
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                    chessai.core.action.Action.from_uci("a1b1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
            ),
            (
                [
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                ],
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
            ),

            # Meta actions.
            (
                [
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                ],
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
            ),
            (
                [
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.REJECT_DRAW_ACTION,
                ],
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
            ),

            # All together.
            (
                [
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                    chessai.core.action.Action.from_uci("a1b1"),
                ],
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
            ),
            (
                [
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.Action.from_uci("b1a1"),
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                ],
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (input_list, expected_list) = test_case

                input_list.sort()

                self.assertEqual(input_list, expected_list)

    def test_action_membership(self):
        """ Test sorting actions. """

        # [(input, expected_output), ...]
        test_cases: list[tuple[chessai.core.action.Action, list[chessai.core.action.Action]], bool] = [
            (
                chessai.core.action.REJECT_DRAW_ACTION,
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
                True,
            ),

            (
                chessai.core.action.PROPOSE_DRAW_ACTION,
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                True,
            ),

            (
                chessai.core.action.FORFEIT_ACTION,
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                True,
            ),

            (
                chessai.core.action.ACCEPT_DRAW_ACTION,
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                True,
            ),

            (
                chessai.core.action.NULL_ACTION,
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.NULL_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                True,
            ),

            (
                chessai.core.action.REJECT_DRAW_ACTION,
                [
                    chessai.core.action.Action.from_uci("a1a1"),
                    chessai.core.action.Action.from_uci("a1a2"),
                    chessai.core.action.Action.from_uci("a1b1"),
                    chessai.core.action.Action.from_uci("a2a1"),
                    chessai.core.action.Action.from_uci("b1a1"),
                ],
                False,
            ),

            (
                chessai.core.action.PROPOSE_DRAW_ACTION,
                [],
                False,
            ),

            (
                chessai.core.action.FORFEIT_ACTION,
                [
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                False,
            ),

            (
                chessai.core.action.ACCEPT_DRAW_ACTION,
                [
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                False,
            ),

            (
                chessai.core.action.NULL_ACTION,
                [
                    chessai.core.action.Action.from_uci("b1a1"),
                    chessai.core.action.REJECT_DRAW_ACTION,
                    chessai.core.action.ACCEPT_DRAW_ACTION,
                    chessai.core.action.FORFEIT_ACTION,
                    chessai.core.action.PROPOSE_DRAW_ACTION,
                ],
                False,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            with self.subTest(msg = f"Case {i}:"):
                (action, action_list, expected) = test_case

                actual = action in action_list

                self.assertEqual(actual, expected)
