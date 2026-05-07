import edq.testing.unittest

import chessai.chess.game
import chessai.core.game
import chessai.core.agentinfo
import chessai.core.gamestate
import chessai.core.types
import chessai.util.alias

AGENT_INFOS: dict[chessai.core.types.Color, chessai.core.agentinfo.AgentInfo] = {
    chessai.core.types.Color.WHITE: chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
    chessai.core.types.Color.BLACK: chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_RANDOM.long),
}
DEFAULT_SEED: int = 1

class GameFromPGNTest(edq.testing.unittest.BaseTest):
    """ Test Game.from_pgn() construction from ParsedPGN. """

    def test_from_pgn(self):
        """ Test Game.from_pgn() with various PGN inputs. """

        # [(pgn_string, expected_game), ...]
        test_cases: list[tuple[str, chessai.chess.game.Game]] = [
            # Basic game with default starting position.
            (
                '[Event "Test Tournament"]\n[Site "Test City"]\n[Date "2024.01.01"]\n'
                + '[Round "1"]\n[White "Alice"]\n[Black "Bob"]\n[Result "1-0"]\n\n'
                + '1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0',
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = chessai.core.gamestate.DEFAULT_FEN,
                        event = "Test Tournament",
                        site = "Test City",
                        date = "2024.01.01",
                        game_round = "1",
                        white_player = "Alice",
                        black_player = "Bob",
                    ),
                    fen = chessai.core.gamestate.DEFAULT_FEN,
                    san_moves = ["e4", "e5", "Nf3", "Nc6", "Bb5"],
                    expected_result = chessai.core.parser.PGNResult("1-0"),
                ),
            ),

            # Game with custom starting position (FEN header).
            (
                '[Event "Puzzle"]\n[Site "Online"]\n[Date "2024.01.15"]\n'
                '[Round "-"]\n[White "White"]\n[Black "Black"]\n[Result "*"]\n'
                '[FEN "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"]\n\n'
                '3. Bb5 a6 *',
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
                        event = "Puzzle",
                        site = "Online",
                        date = "2024.01.15",
                        game_round = "-",
                        white_player = "White",
                        black_player = "Black",
                    ),
                    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
                    san_moves = ["Bb5", "a6"],
                    expected_result = chessai.core.parser.PGNResult("*"),
                ),
            ),

            # Draw result.
            (
                '[Event "Draw Game"]\n[Site "Test"]\n[Date "2024.02.01"]\n'
                '[Round "5"]\n[White "Player1"]\n[Black "Player2"]\n[Result "1/2-1/2"]\n\n'
                '1. e4 e5 2. Nf3 Nc6 1/2-1/2',
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = chessai.core.gamestate.DEFAULT_FEN,
                        event = "Draw Game",
                        site = "Test",
                        date = "2024.02.01",
                        game_round = "5",
                        white_player = "Player1",
                        black_player = "Player2",
                    ),
                    fen = chessai.core.gamestate.DEFAULT_FEN,
                    san_moves = ["e4", "e5", "Nf3", "Nc6"],
                    expected_result = chessai.core.parser.PGNResult("1/2-1/2"),
                ),
            ),
        ]

        for i, test_case in enumerate(test_cases):
            (pgn_string, expected_game) = test_case

            with self.subTest(msg = f"Case {i}:"):
                # Parse the PGN.
                parsed_pgn = chessai.core.parser.parse_pgn_game(pgn_string)
                self.assertIsNotNone(parsed_pgn)

                # Create Game from ParsedPGN.
                game = chessai.chess.game.Game.from_pgn(
                    parsed_pgn,
                    agent_infos = AGENT_INFOS,
                    seed = DEFAULT_SEED,
                )

                # Set the seed to the default seed to compare game info's directly.
                expected_game.game_info.seed = DEFAULT_SEED

                # Verify the game info is as expected.
                self.assertEqual(game.game_info, expected_game.game_info)

                # Verify the fen, san_moves, and expected_result of the Game.
                self.assertEqual(game.fen, expected_game.fen)
                self.assertEqual(game.san_moves, expected_game.san_moves)
                self.assertEqual(game.expected_result, expected_game.expected_result)
