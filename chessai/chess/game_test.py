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
                """
                [Event "Test Tournament"]
                [Site "Test City"]
                [Date "2024.01.01"]
                [Round "1"]
                [White "Alice"]
                [Black "Bob"]
                [Result "1-0"]

                1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0
                """,
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
                    initial_actions = [
                        chessai.core.action.Action.from_uci("e2e4"),
                        chessai.core.action.Action.from_uci("e7e5"),
                        chessai.core.action.Action.from_uci("g1f3"),
                        chessai.core.action.Action.from_uci("b8c6"),
                        chessai.core.action.Action.from_uci("f1b5"),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("1-0"),
                ),
            ),

            # Game with custom starting position (FEN header).
            (
                """
                [Event "Puzzle"]
                [Site "Online"]
                [Date "2024.01.15"]
                [Round "-"]
                [White "White"]
                [Black "Black"]
                [Result "*"]
                [FEN "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"]

                3. Bb5 a6 *
                """,
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
                    initial_actions = [
                        chessai.core.action.Action.from_uci("f1b5"),
                        chessai.core.action.Action.from_uci("a7a6"),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("*"),
                ),
            ),

            # Draw result.
            (
                """
                [Event "Draw Game"]
                [Site "Test"]
                [Date "2024.02.01"]
                [Round "5"]
                [White "Player1"]
                [Black "Player2"]
                [Result "1/2-1/2"]

                1. e4 e5 2. Nf3 Nc6 1/2-1/2
                """,
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
                    initial_actions = [
                        chessai.core.action.Action.from_uci("e2e4"),
                        chessai.core.action.Action.from_uci("e7e5"),
                        chessai.core.action.Action.from_uci("g1f3"),
                        chessai.core.action.Action.from_uci("b8c6"),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("1/2-1/2"),
                ),
            ),

            # Proposed draw.
            (
                """
                [Event "casual correspondence game"]
                [Site "https://lichess.org/s7o9V5ny"]
                [Date "2026.05.07"]
                [Round "-"]
                [White "ScrimScram"]
                [Black "Anonymous"]
                [Result "1/2-1/2"]
                [GameId "s7o9V5ny"]
                [UTCDate "2026.05.07"]
                [UTCTime "21:09:09"]
                [WhiteElo "1500"]
                [BlackElo "?"]
                [Variant "Standard"]
                [TimeControl "-"]
                [ECO "C00"]
                [Opening "French Defense"]
                [Termination "Normal"]
                [Annotator "lichess.org"]

                1. e4 e6 { C00 French Defense } { The game is a draw. } 1/2-1/2
                """,
                chessai.chess.game.Game(
                    game_info = chessai.core.game.GameInfo(
                        agent_infos = AGENT_INFOS,
                        start_fen = chessai.core.gamestate.DEFAULT_FEN,
                        event = "casual correspondence game",
                        site = "https://lichess.org/s7o9V5ny",
                        date = "2026.05.07",
                        game_round = "-",
                        white_player = "ScrimScram",
                        black_player = "Anonymous",
                    ),
                    fen = chessai.core.gamestate.DEFAULT_FEN,
                    initial_actions = [
                        chessai.core.action.Action.from_uci("e2e4"),
                        chessai.core.action.Action.from_uci("e7e6"),
                    ],
                    expected_result = chessai.core.gameparser.PGNResult("1/2-1/2"),
                ),
            ),
        ]

        for i, test_case in enumerate(test_cases):
            (pgn_string, expected_game) = test_case

            with self.subTest(msg = f"Case {i}:"):
                # Parse the PGN.
                parsed_pgn = chessai.core.gameparser.parse_pgn_game(pgn_string, chessai.chess.gamestate.GameState)
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

                # Verify the fen, initial_actions, and expected_result of the Game.
                self.assertEqual(game.fen, expected_game.fen)
                self.assertEqual(game.initial_actions, expected_game.initial_actions)
                self.assertEqual(game.expected_result, expected_game.expected_result)
