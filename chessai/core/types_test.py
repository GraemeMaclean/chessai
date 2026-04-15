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

    def test_piece_type_basic(self):
        """ Test basic PieceType behavior. """

        # [(piece, symbol, name_str, str_val, repr_val), ...]
        test_cases: list[tuple[chessai.core.types.PieceType, str, str, str, str]] = [
            (chessai.core.types.PieceType.KING, 'k', 'king', 'k', 'PieceType.KING'),
            (chessai.core.types.PieceType.QUEEN, 'q', 'queen', 'q', 'PieceType.QUEEN'),
            (chessai.core.types.PieceType.KNIGHT, 'n', 'knight', 'n', 'PieceType.KNIGHT'),
            (chessai.core.types.PieceType.BISHOP, 'b', 'bishop', 'b', 'PieceType.BISHOP'),
            (chessai.core.types.PieceType.ROOK, 'r', 'rook', 'r', 'PieceType.ROOK'),
            (chessai.core.types.PieceType.PAWN, 'p', 'pawn', 'p', 'PieceType.PAWN'),
        ]

        for (i, (piece, symbol, name_str, str_val, repr_val)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                self.assertEqual(symbol, piece.symbol)
                self.assertEqual(name_str, piece.name_str)
                self.assertEqual(str_val, str(piece))
                self.assertEqual(repr_val, repr(piece))

    def test_piece_type_unicode(self):
        """ Test unicode symbols for PieceType. """

        # [(piece, white_symbol, black_symbol), ...]
        test_cases: list[tuple[chessai.core.types.PieceType, str, str]] = [
            (chessai.core.types.PieceType.KING, '♔', '♚'),
            (chessai.core.types.PieceType.QUEEN, '♕', '♛'),
            (chessai.core.types.PieceType.ROOK, '♖', '♜'),
            (chessai.core.types.PieceType.BISHOP, '♗', '♝'),
            (chessai.core.types.PieceType.KNIGHT, '♘', '♞'),
            (chessai.core.types.PieceType.PAWN, '♙', '♟'),
        ]

        for (i, (piece, white_sym, black_sym)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                self.assertEqual(white_sym, piece.unicode_symbol(chessai.core.types.Color.WHITE))
                self.assertEqual(black_sym, piece.unicode_symbol(chessai.core.types.Color.BLACK))

    def test_piece_symbols_mapping(self):
        """ Test PIECE_SYMBOLS mapping. """

        for (i, piece) in enumerate(chessai.core.types.PieceType):
            with self.subTest(msg=f"Case {i}:"):
                symbol = piece.value
                self.assertIn(symbol, chessai.core.types.PIECE_SYMBOLS)
                self.assertEqual(piece, chessai.core.types.PIECE_SYMBOLS[symbol])

    def test_unicode_piece_symbols_mapping(self):
        """ Test UNICODE_PIECE_SYMBOLS completeness. """

        expected_keys: list[str] = ['R', 'r', 'N', 'n', 'B', 'b', 'Q', 'q', 'K', 'k', 'P', 'p']

        for (i, key) in enumerate(expected_keys):
            with self.subTest(msg=f"Case {i}:"):
                self.assertIn(key, chessai.core.types.UNICODE_PIECE_SYMBOLS)
                self.assertIsInstance(chessai.core.types.UNICODE_PIECE_SYMBOLS[key], str)

    def test_termination_reason_enum(self):
        """ Test TerminationReason enum basics. """

        # Ensure values exist and are distinct.
        reasons = list(chessai.core.types.TerminationReason)

        self.assertGreater(len(reasons), 0)

        for (i, reason) in enumerate(reasons):
            with self.subTest(msg=f"Case {i}:"):
                self.assertIsInstance(reason.name, str)
                self.assertIsInstance(reason.value, int)
