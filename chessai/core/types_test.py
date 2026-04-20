import edq.testing.unittest

import chessai.core.types

class TypesTest(edq.testing.unittest.BaseTest):
    """ Test types module functionality. """

    def test_color_basic(self):
        """ Test basic Color behavior. """

        # [(color, expected_symbol, expected_bool, expected_str, expected_repr), ...]
        test_cases: list[tuple[chessai.core.types, str, bool, str, str]] = [
            (chessai.core.types.Color.WHITE, 'w', True, 'white', 'Color.WHITE'),
            (chessai.core.types.Color.BLACK, 'b', False, 'black', 'Color.BLACK'),
        ]

        for (i, (color, symbol, truth, string, repr_str)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                self.assertEqual(symbol, color.symbol())
                self.assertEqual(truth, bool(color))
                self.assertEqual(string, str(color))
                self.assertEqual(repr_str, repr(color))

    def test_color_opposite(self):
        """ Test Color.opposite(). """

        test_cases: list[tuple[chessai.core.types.Color, chessai.core.types.Color]] = [
            (chessai.core.types.Color.WHITE, chessai.core.types.Color.BLACK),
            (chessai.core.types.Color.BLACK, chessai.core.types.Color.WHITE),
        ]

        for (i, (color, expected)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                self.assertEqual(expected, color.opposite())

    def test_termination_reason_enum(self):
        """ Test TerminationReason enum basics. """

        # Ensure values exist and are distinct.
        reasons = list(chessai.core.types.TerminationReason)

        self.assertGreater(len(reasons), 0)

        for (i, reason) in enumerate(reasons):
            with self.subTest(msg=f"Case {i}:"):
                self.assertIsInstance(reason.name, str)
                self.assertIsInstance(reason.value, str)
