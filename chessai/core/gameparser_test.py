import edq.testing.unittest

import chessai.chess.piece
import chessai.core.castling
import chessai.core.coordinate
import chessai.core.gameparser
import chessai.core.piece
import chessai.core.types

# The standard starting position FEN, used across multiple tests.
STARTING_FEN: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class ParseSinglePGNTest(edq.testing.unittest.BaseTest):
    """ Test the parsing of a single raw PGN into a ParsedPGN. """

    def test_parse_single_pgn(self):
        """ Test the parsing of a single raw PGN into a ParsedPGN. """

        # [(raw PGN, error substring, expected ParsedPGN), ...]
        test_cases: list[tuple[str, str | None, chessai.core.gameparser.ParsedPGN]] = [
            # Default headers and move SANs.
            (
                '[Event "Test"]\n[Site "Here"]\n[Date "2024.01.01"]\n'
                '[Round "1"]\n[White "A"]\n[Black "B"]\n[Result "1/2-1/2"]\n\n'
                '1. e4 e5 2. Nf3 Nc6 1/2-1/2',
                None,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeadersDict({
                        chessai.core.gameparser.StandardPGNHeaders.EVENT: "Test",
                        chessai.core.gameparser.StandardPGNHeaders.SITE: "Here",
                        chessai.core.gameparser.StandardPGNHeaders.DATE: "2024.01.01",
                        chessai.core.gameparser.StandardPGNHeaders.ROUND: "1",
                        chessai.core.gameparser.StandardPGNHeaders.WHITE: "A",
                        chessai.core.gameparser.StandardPGNHeaders.BLACK: "B",
                        chessai.core.gameparser.StandardPGNHeaders.RESULT: "1/2-1/2",
                    }),
                    initial_actions = ["e4", "e5", "Nf3", "Nc6"],
                    result = chessai.core.gameparser.PGNResult('1/2-1/2'),
                )
            ),

            # Ignore RAVs.
            (
                '[Event "Test"]\n[Site "Here"]\n[Date "2024.01.01"]\n'
                '[Round "1"]\n[White "A"]\n[Black "B"]\n[Result "0-1"]\n\n'
                '1. e4 (1. d4 d5) e5 2. Nf3 Nc6 0-1',
                None,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeadersDict({
                        chessai.core.gameparser.StandardPGNHeaders.EVENT: "Test",
                        chessai.core.gameparser.StandardPGNHeaders.SITE: "Here",
                        chessai.core.gameparser.StandardPGNHeaders.DATE: "2024.01.01",
                        chessai.core.gameparser.StandardPGNHeaders.ROUND: "1",
                        chessai.core.gameparser.StandardPGNHeaders.WHITE: "A",
                        chessai.core.gameparser.StandardPGNHeaders.BLACK: "B",
                        chessai.core.gameparser.StandardPGNHeaders.RESULT: "0-1",
                    }),
                    initial_actions = ["e4", "e5", "Nf3", "Nc6"],
                    result = chessai.core.gameparser.PGNResult('0-1'),
                )
            ),

            # Ignore nested RAVs.
            (
                '[Event "Test"]\n[Site "Here"]\n[Date "2024.01.01"]\n'
                '[Round "1"]\n[White "A"]\n[Black "B"]\n[Result "1-0"]\n\n'
                '1. e4 (1. d4 (1... d5) d5) e5 2. Nf3 Nc6 1-0',
                None,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeadersDict({
                        chessai.core.gameparser.StandardPGNHeaders.EVENT: "Test",
                        chessai.core.gameparser.StandardPGNHeaders.SITE: "Here",
                        chessai.core.gameparser.StandardPGNHeaders.DATE: "2024.01.01",
                        chessai.core.gameparser.StandardPGNHeaders.ROUND: "1",
                        chessai.core.gameparser.StandardPGNHeaders.WHITE: "A",
                        chessai.core.gameparser.StandardPGNHeaders.BLACK: "B",
                        chessai.core.gameparser.StandardPGNHeaders.RESULT: "1-0",
                    }),
                    initial_actions = ["e4", "e5", "Nf3", "Nc6"],
                    result = chessai.core.gameparser.PGNResult('1-0'),
                )
            ),

            # Capture in-line comments.
            (
                '[Event "Test"]\n[Site "Here"]\n[Date "2024.01.01"]\n'
                '[Round "1"]\n[White "A"]\n[Black "B"]\n[Result "*"]\n\n'
                '1. e4 {Very interesting move!} e5 2. Nf3 Nc6 *',
                None,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeadersDict({
                        chessai.core.gameparser.StandardPGNHeaders.EVENT: "Test",
                        chessai.core.gameparser.StandardPGNHeaders.SITE: "Here",
                        chessai.core.gameparser.StandardPGNHeaders.DATE: "2024.01.01",
                        chessai.core.gameparser.StandardPGNHeaders.ROUND: "1",
                        chessai.core.gameparser.StandardPGNHeaders.WHITE: "A",
                        chessai.core.gameparser.StandardPGNHeaders.BLACK: "B",
                        chessai.core.gameparser.StandardPGNHeaders.RESULT: "*",
                    }),
                    initial_actions = ["e4", "e5", "Nf3", "Nc6"],
                    comments = ["Very interesting move!"],
                    result = chessai.core.gameparser.PGNResult('*'),
                )
            ),

            # Capture multi-line comments.
            (
                '[Event "Test"]\n[Site "Here"]\n[Date "2024.01.01"]\n'
                '[Round "1"]\n[White "A"]\n[Black "B"]\n[Result "1-0"]\n\n'
                '1. e4 {This is a\nmulti-line\ncomment!} e5 2. Nf3 Nc6 1-0',
                None,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeadersDict({
                        chessai.core.gameparser.StandardPGNHeaders.EVENT: "Test",
                        chessai.core.gameparser.StandardPGNHeaders.SITE: "Here",
                        chessai.core.gameparser.StandardPGNHeaders.DATE: "2024.01.01",
                        chessai.core.gameparser.StandardPGNHeaders.ROUND: "1",
                        chessai.core.gameparser.StandardPGNHeaders.WHITE: "A",
                        chessai.core.gameparser.StandardPGNHeaders.BLACK: "B",
                        chessai.core.gameparser.StandardPGNHeaders.RESULT: "1-0",
                    }),
                    initial_actions = ["e4", "e5", "Nf3", "Nc6"],
                    comments = ["This is a\nmulti-line\ncomment!"],
                    result = chessai.core.gameparser.PGNResult('1-0'),
                )
            ),

            # Custom starting position with FEN header.
            (
                '[Event "Test"]\n[Site "Here"]\n[Date "2024.01.01"]\n'
                '[Round "1"]\n[White "A"]\n[Black "B"]\n[Result "1-0"]\n'
                '[FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"]\n\n'
                '1... Nc6 2. Nf3 Nf6 1-0',
                None,
                chessai.core.gameparser.ParsedPGN(
                    headers = chessai.core.gameparser.StandardHeadersDict({
                        chessai.core.gameparser.StandardPGNHeaders.EVENT: "Test",
                        chessai.core.gameparser.StandardPGNHeaders.SITE: "Here",
                        chessai.core.gameparser.StandardPGNHeaders.DATE: "2024.01.01",
                        chessai.core.gameparser.StandardPGNHeaders.ROUND: "1",
                        chessai.core.gameparser.StandardPGNHeaders.WHITE: "A",
                        chessai.core.gameparser.StandardPGNHeaders.BLACK: "B",
                        chessai.core.gameparser.StandardPGNHeaders.RESULT: "1-0",
                    }),
                    optional_headers = {"Fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"},
                    initial_actions = ["Nc6", "Nf3", "Nf6"],
                    result = "1-0",
                )
            ),

            # Error: missing required headers.
            (
                '[Event "Test"]\n\n1. e4 e5',
                "Did not find all required headers",
                None,
            ),
        ]

        for i, test_case in enumerate(test_cases):
            (raw_pgn, error_substring, expected_pgn) = test_case

            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual_pgn = chessai.core.gameparser.parse_pgn_game(raw_pgn, chessai.core.gamestate.GameState)

                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex))
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertTrue(actual_pgn.headers.is_complete())

                self.assertEqual(expected_pgn, actual_pgn)
