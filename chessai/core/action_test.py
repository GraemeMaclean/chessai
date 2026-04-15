import edq.testing.unittest

import chessai.core.action
import chessai.core.coordinate


class ActionTest(edq.testing.unittest.BaseTest):
    """ Test Action functionality. """

    def test_uci(self):
        """ Test Action.uci(). """

        # [(start_coordinate, end_coordinate, uci), ...]
        test_cases: list[tuple[
            chessai.core.coordinate.Coordinate,
            chessai.core.coordinate.Coordinate,
            str
        ]] = [
            (
                chessai.core.coordinate.Coordinate(0, 0),
                chessai.core.coordinate.Coordinate(1, 1),
                'a1b2',
            ),
            (
                chessai.core.coordinate.Coordinate(3, 4),
                chessai.core.coordinate.Coordinate(5, 6),
                'd5f7',
            ),
            (
                chessai.core.coordinate.Coordinate(26, 0),
                chessai.core.coordinate.Coordinate(27, 9),
                'aa1ab10',
            ),
        ]

        for (i, (start_coordinate, end_coordinate, expected)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                action = chessai.core.action.Action(start_coordinate, end_coordinate)
                self.assertEqual(expected, action.uci())

    def test_from_uci(self):
        """ Test Action.from_uci(). """

        # [(uci, error_substring, start_coordinate, end_coordinate), ...]
        test_cases: list[tuple[
            str,
            str | None,
            chessai.core.coordinate.Coordinate | None,
            chessai.core.coordinate.Coordinate | None,
        ]] = [
            # Base
            (
                'a1b2',
                None,
                chessai.core.coordinate.Coordinate(0, 0),
                chessai.core.coordinate.Coordinate(1, 1),
            ),
            (
                'd5f7',
                None,
                chessai.core.coordinate.Coordinate(3, 4),
                chessai.core.coordinate.Coordinate(5, 6),
            ),
            (
                'aa1ab10',
                None,
                chessai.core.coordinate.Coordinate(26, 0),
                chessai.core.coordinate.Coordinate(27, 9),
            ),

            # Errors
            (
                '',
                "An action must be a pair of coordinates '([a-z]+)(\\d+)([a-z]+)(\\d+)', got: ''.",
                None,
                None,
            ),
            (
                'a1',
                "An action must be a pair of coordinates '([a-z]+)(\\d+)([a-z]+)(\\d+)', got: 'a1'.",
                None,
                None,
            ),
            (
                'a1b2c3',
                "An action must be a pair of coordinates '([a-z]+)(\\d+)([a-z]+)(\\d+)', got: 'a1b2c3'.",
                None,
                None,
            ),
        ]

        for (i, (uci, error_substring, expected_start, expected_end)) in enumerate(test_cases):
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

    def test_round_trip(self):
        """ Test Action round-trip conversion (uci -> object -> uci). """

        test_cases: list[str] = [
            'a1b2',
            'd5f7',
            'aa1ab10',
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

        self.assertEqual(chessai.core.action.Action(), chessai.core.action.NULL_ACTION)
