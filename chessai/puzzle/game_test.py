import pathlib

import edq.testing.unittest
import edq.util.dirent

import chessai.core.parser
import chessai.puzzle.bin

class GameTest(edq.testing.unittest.BaseTest):
    """ Test specifics for puzzle games. """

    def test_puzzles(self):
        """ Test every puzzle board in the resources directory. """

        expected_score = 1.0

        board_paths = []
        boards_dir = pathlib.Path(chessai.core.parser.PUZZLES_DIR)
        for path in boards_dir.iterdir():
            if (not path.is_file()):
                continue

            board_paths.append(str(path))

        board_paths.sort()

        # Ensure we find at least one puzzle.
        self.assertNotEqual(len(board_paths), 0)

        for (i, board_path) in enumerate(board_paths):
            with self.subTest(msg = f"Case {i}, path: {board_path}"):
                gamestate = chessai.puzzle.gamestate.GameState(fen = board_path)

                # Puzzle boards must include the move lines, which will be parsed by the gamestate.
                move_lines = gamestate.options.get('move_lines', None)
                agent_arg = f"{gamestate.turn.symbol()}::move_lines={move_lines}"

                argv = [
                    '--log-level', 'CRITICAL',
                    '--board', str(board_path),
                    '--agent', 'agent-multi-scripted',
                    '--agent-arg', agent_arg,
                    '--max-moves', '80',
                ]
                results = chessai.puzzle.bin.main(argv = argv)

                self.assertEqual(expected_score, results[0].score)
