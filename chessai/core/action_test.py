import edq.testing.unittest

import chessai.core.action
import chessai.core.coordinate
import chessai.core.types

class ActionTest(edq.testing.unittest.BaseTest):
    """ Test Action functionality. """

    def test_uci(self):
        """ Test Action.uci(). """

        # [(start_coordinate, end_coordinate, promotion, uci), ...]
        test_cases: list[tuple[
            chessai.core.coordinate.Coordinate,
            chessai.core.coordinate.Coordinate,
            chessai.core.types.PieceType | None,
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
                chessai.core.types.PieceType.QUEEN,
                'e7e8q',
            ),
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.core.types.PieceType.ROOK,
                'e7e8r',
            ),
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.core.types.PieceType.BISHOP,
                'e7e8b',
            ),
            (
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.core.types.PieceType.KNIGHT,
                'e7e8n',
            ),
        ]

        for (i, (start_coordinate, end_coordinate, promotion, expected)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
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
            chessai.core.types.PieceType | None,
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
                chessai.core.types.PieceType.QUEEN,
            ),
            (
                'e7e8r',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.core.types.PieceType.ROOK,
            ),
            (
                'e7e8b',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.core.types.PieceType.BISHOP,
            ),
            (
                'e7e8n',
                None,
                chessai.core.coordinate.Coordinate(4, 6),
                chessai.core.coordinate.Coordinate(4, 7),
                chessai.core.types.PieceType.KNIGHT,
            ),

            # Promotion on large board (file > 'z').
            (
                'aa1ab2q',
                None,
                chessai.core.coordinate.Coordinate(26, 0),
                chessai.core.coordinate.Coordinate(27, 1),
                chessai.core.types.PieceType.QUEEN,
            ),

            # Errors
            (
                '',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-z]?)$', got: ''.",
                None,
                None,
                None,
            ),
            (
                'a1',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-z]?)$', got: 'a1'.",
                None,
                None,
                None,
            ),
            (
                'a1b2c3',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-z]?)$', got: 'a1b2c3'.",
                None,
                None,
                None,
            ),

            # Multiple trailing characters.
            (
                'e7e8qq',
                r"An action must be a pair of coordinates with an optional promotion piece: '^([a-z]+\d+)([a-z]+\d+)([a-z]?)$', got: 'e7e8qq'.",
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
            with self.subTest(msg=f"Case {i}:"):
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
        ]

        for (i, uci) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
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
