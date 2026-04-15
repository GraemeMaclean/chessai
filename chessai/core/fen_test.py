import edq.testing.unittest

import chessai.core.castling
import chessai.core.coordinate
import chessai.core.fen
import chessai.core.piece
import chessai.core.types

# The standard starting position FEN, used across multiple tests.
STARTING_FEN: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class ParseDimensionsTest(edq.testing.unittest.BaseTest):
    """ Test chessai.core.fen._parse_dimensions(). """

    def test_parse_dimensions(self):
        """ Test valid dimension strings. """

        # [(dimensions_field, expected_num_files, expected_num_ranks), ...]
        test_cases: list[tuple[str, int, int]] = [
            ('8x8',   8,  8),
            ('10x10', 10, 10),
            ('4x6',   4,  6),
            ('1x1',   1,  1),
            ('16x4',  16, 4),
        ]

        for (i, (dimensions_field, expected_files, expected_ranks)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                (num_files, num_ranks) = chessai.core.fen._parse_dimensions(dimensions_field)
                self.assertEqual(expected_files, num_files)
                self.assertEqual(expected_ranks, num_ranks)

    def test_parse_dimensions_errors(self):
        """ Test that malformed dimension strings raise ValueError. """

        # [(dimensions_field, error_substring), ...]
        test_cases: list[tuple[str, str]] = [
            (
                '8',
                "FEN dimensions field must be '<files>x<ranks>' (e.g. '8x8'), got: '8'.",
            ),
            (
                '8x',
                "FEN dimensions field must be '<files>x<ranks>' (e.g. '8x8'), got: '8x'.",
            ),
            (
                'x8',
                "FEN dimensions field must be '<files>x<ranks>' (e.g. '8x8'), got: 'x8'.",
            ),
            (
                '8x8x8',
                "FEN dimensions field must be '<files>x<ranks>' (e.g. '8x8'), got: '8x8x8'.",
            ),
            (
                'axb',
                "FEN dimensions field must be '<files>x<ranks>' (e.g. '8x8'), got: 'axb'.",
            ),
            (
                '0x8',
                "FEN dimensions num_files must be >= 1, got: 0.",
            ),
            (
                '8x0',
                "FEN dimensions num_ranks must be >= 1, got: 0.",
            ),
        ]

        for (i, (dimensions_field, error_substring)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                try:
                    chessai.core.fen._parse_dimensions(dimensions_field)
                except ValueError as ex:
                    self.assertIn(error_substring, str(ex))
                    continue

                self.fail(f"Did not get expected error: '{error_substring}'.")


class ParseFENTest(edq.testing.unittest.BaseTest):
    """ Test chessai.core.fen.parse(). """

    def test_parse_standard_starting_position(self):
        """ Test parsing the standard chess starting position. """

        result = chessai.core.fen.parse(STARTING_FEN)

        self.assertEqual(chessai.core.types.Color.WHITE, result.turn)
        self.assertEqual(0, result.halfmove_clock)
        self.assertEqual(1, result.fullmove_number)
        self.assertIsNone(result.en_passant_coordinate)
        self.assertEqual(8, result.num_files)
        self.assertEqual(8, result.num_ranks)

        # Castling rights.
        self.assertTrue(result.castling_rights.white_kingside)
        self.assertTrue(result.castling_rights.white_queenside)
        self.assertTrue(result.castling_rights.black_kingside)
        self.assertTrue(result.castling_rights.black_queenside)

        # Spot-check a few well-known piece positions.
        white_king_coords = [
            coord for (coord, piece) in result.pieces.items()
            if (piece.piece_type == chessai.core.types.PieceType.KING
                    and piece.color == chessai.core.types.Color.WHITE)
        ]
        self.assertEqual(1, len(white_king_coords))
        self.assertEqual(chessai.core.coordinate.Coordinate(4, 0), white_king_coords[0])

        black_king_coords = [
            coord for (coord, piece) in result.pieces.items()
            if (piece.piece_type == chessai.core.types.PieceType.KING
                    and piece.color == chessai.core.types.Color.BLACK)
        ]
        self.assertEqual(1, len(black_king_coords))
        self.assertEqual(chessai.core.coordinate.Coordinate(4, 7), black_king_coords[0])

        # 32 pieces total on the starting board.
        self.assertEqual(32, len(result.pieces))

    def test_parse_turn(self):
        """ Test that the turn field is parsed correctly. """

        # [(fen, expected_turn), ...]
        test_cases: list[tuple[str, chessai.core.types.Color]] = [
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                chessai.core.types.Color.WHITE,
            ),
            (
                'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
                chessai.core.types.Color.BLACK,
            ),
        ]

        for (i, (fen, expected_turn)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = chessai.core.fen.parse(fen)
                self.assertEqual(expected_turn, result.turn)

    def test_parse_castling_rights(self):
        """ Test that castling rights are parsed correctly. """

        # [(fen, expected_castling_rights), ...]
        test_cases: list[tuple[str, chessai.core.castling.CastlingRights]] = [
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                chessai.core.castling.CastlingRights(True, True, True, True),
            ),
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w Kq - 0 1',
                chessai.core.castling.CastlingRights(True, False, False, True),
            ),
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1',
                chessai.core.castling.CastlingRights(False, False, False, False),
            ),
        ]

        for (i, (fen, expected_rights)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = chessai.core.fen.parse(fen)
                self.assertEqual(expected_rights, result.castling_rights)

    def test_parse_en_passant(self):
        """ Test that the en passant coordinate is parsed correctly. """

        # [(fen, expected_en_passant_coordinate), ...]
        test_cases: list[tuple[str, chessai.core.coordinate.Coordinate | None]] = [
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                None,
            ),
            (
                'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
                chessai.core.coordinate.Coordinate(4, 2),
            ),
        ]

        for (i, (fen, expected_ep)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = chessai.core.fen.parse(fen)
                self.assertEqual(expected_ep, result.en_passant_coordinate)

    def test_parse_clocks(self):
        """ Test that the halfmove clock and fullmove number are parsed correctly. """

        # [(fen, expected_halfmove_clock, expected_fullmove_number), ...]
        test_cases: list[tuple[str, int, int]] = [
            ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',  0,  1),
            ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 5 42', 5, 42),
        ]

        for (i, (fen, expected_half, expected_full)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = chessai.core.fen.parse(fen)
                self.assertEqual(expected_half, result.halfmove_clock)
                self.assertEqual(expected_full, result.fullmove_number)

    def test_parse_dimensions_field(self):
        """ Test that the optional dimensions field is parsed and defaults correctly. """

        # [(fen, expected_num_files, expected_num_ranks), ...]
        test_cases: list[tuple[str, int, int]] = [
            # Standard FEN — dimensions default to 8x8.
            ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 8, 8),

            # Explicit 8x8 — same result as omitting the field.
            ('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 8x8', 8, 8),

            # Non-standard board.
            ('ppppkpppp/9/9/9/9/9/9/9/PPPPKPPPP w - - 0 1 9x9', 9, 9),
        ]

        for (i, (fen, expected_files, expected_ranks)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = chessai.core.fen.parse(fen)
                self.assertEqual(expected_files, result.num_files)
                self.assertEqual(expected_ranks, result.num_ranks)

    def test_parse_errors(self):
        """ Test that malformed FEN strings raise ValueError. """

        # [(fen, error_substring), ...]
        test_cases: list[tuple[str, str]] = [
            # Wrong field count.
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -',
                "FEN must have 6 or 7 fields, found 4:",
            ),
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 8x8 extra',
                "FEN must have 6 or 7 fields, found 8:",
            ),

            # Bad turn field.
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR x KQkq - 0 1',
                "FEN turn field must be 'w' or 'b', found: 'x'.",
            ),

            # Bad halfmove clock.
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - -1 1',
                "FEN halfmove clock must be >= 0, found: -1.",
            ),

            # Bad fullmove number.
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0',
                "FEN fullmove number must be >= 1, found: 0.",
            ),

            # Wrong rank count.
            (
                'rnbqkbnr/pppppppp/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                "FEN piece field must have 8 ranks separated by '/', found 7:",
            ),

            # Too many files on a rank.
            (
                'rnbqkbnrr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                "Too many pieces on rank 8 in FEN:",
            ),

            # Too few files on a rank.
            (
                'rnbqkbn/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                "Rank 8 has 7 files, expected 8:",
            ),

            # Bad dimensions field.
            (
                'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 8',
                "FEN dimensions field must be '<files>x<ranks>' (e.g. '8x8'), got: '8'.",
            ),
        ]

        for (i, (fen, error_substring)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                try:
                    chessai.core.fen.parse(fen)
                except ValueError as ex:
                    self.assertIn(error_substring, str(ex))
                    continue

                self.fail(f"Did not get expected error: '{error_substring}'.")


class SerializeFENTest(edq.testing.unittest.BaseTest):
    """ Test chessai.core.fen.serialize(). """

    def test_serialize_standard_size_omits_dimensions(self):
        """
        Serializing a standard 8x8 board should produce a spec-compliant
        6-field FEN with no dimensions extension.
        """

        result = chessai.core.fen.parse(STARTING_FEN)
        serialized = chessai.core.fen.serialize(
            pieces                = result.pieces,
            turn                  = result.turn,
            castling_rights       = result.castling_rights,
            en_passant_coordinate = result.en_passant_coordinate,
            halfmove_clock        = result.halfmove_clock,
            fullmove_number       = result.fullmove_number,
            num_files             = result.num_files,
            num_ranks             = result.num_ranks,
        )

        self.assertEqual(STARTING_FEN, serialized)
        self.assertEqual(6, len(serialized.split()))

    def test_serialize_non_standard_size_includes_dimensions(self):
        """
        Serializing a non-standard board should append the dimensions field.
        """

        fen_with_dimensions = 'ppppkpppp/9/9/9/9/9/9/9/PPPPKPPPP w - - 0 1 9x9'
        result = chessai.core.fen.parse(fen_with_dimensions)
        serialized = chessai.core.fen.serialize(
            pieces                = result.pieces,
            turn                  = result.turn,
            castling_rights       = result.castling_rights,
            en_passant_coordinate = result.en_passant_coordinate,
            halfmove_clock        = result.halfmove_clock,
            fullmove_number       = result.fullmove_number,
            num_files             = result.num_files,
            num_ranks             = result.num_ranks,
        )

        self.assertEqual(fen_with_dimensions, serialized)
        self.assertEqual(7, len(serialized.split()))

    def test_serialize_default_dimensions_omits_field(self):
        """
        Calling serialize() without explicit dimensions should default to 8x8
        and omit the dimensions field.
        """

        result = chessai.core.fen.parse(STARTING_FEN)
        serialized = chessai.core.fen.serialize(
            pieces                = result.pieces,
            turn                  = result.turn,
            castling_rights       = result.castling_rights,
            en_passant_coordinate = result.en_passant_coordinate,
            halfmove_clock        = result.halfmove_clock,
            fullmove_number       = result.fullmove_number,
        )

        self.assertEqual(STARTING_FEN, serialized)


class RoundTripFENTest(edq.testing.unittest.BaseTest):
    """ Test that parse -> serialize produces the original FEN string. """

    def test_round_trip(self):
        """ Test FEN round-trip conversion (string -> ParsedFEN -> string). """

        test_cases: list[str] = [
            # Standard starting position.
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',

            # Mid-game position with en passant.
            'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',

            # No castling rights.
            'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 10 5',

            # Non-standard board size.
            'ppppkpppp/9/9/9/9/9/9/9/PPPPKPPPP w - - 0 1 9x9',
        ]

        for (i, fen) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = chessai.core.fen.parse(fen)
                serialized = chessai.core.fen.serialize(
                    pieces                = result.pieces,
                    turn                  = result.turn,
                    castling_rights       = result.castling_rights,
                    en_passant_coordinate = result.en_passant_coordinate,
                    halfmove_clock        = result.halfmove_clock,
                    fullmove_number       = result.fullmove_number,
                    num_files             = result.num_files,
                    num_ranks             = result.num_ranks,
                )

                self.assertEqual(fen, serialized)
