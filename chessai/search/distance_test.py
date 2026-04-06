import edq.testing.unittest

import chessai.core.board
import chessai.search.distance
import chessai.search.position

class DistanceTest(edq.testing.unittest.BaseTest):
    """ Test different distance-related functionalities. """

    def test_manhattan_base(self):
        """ Test Manhattan distance and heuristic. """

        test_board = chessai.core.board.load_path('tour-base')
        test_state = chessai.core.gamestate.GameState(seed = 4, board = test_board)

        # [(a, b, expected), ...]
        test_cases = [
            # Identity
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(0, 0), [0.0]),

            # Lateral
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(1, 0), [1.0]),
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(0, 1), [1.0]),
            (chessai.core.square.Square.from_file_rank(1, 0), chessai.core.square.Square.from_file_rank(0, 0), [1.0]),
            (chessai.core.square.Square.from_file_rank(0, 1), chessai.core.square.Square.from_file_rank(0, 0), [1.0]),

            # Diagonal
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(1, 1), [2.0]),
            (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(2, 2), [2.0]),
            (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(0, 0), [2.0]),
        ]

        for (i, test_case) in enumerate(test_cases):
            (a, b, expected_distances) = test_case
            with self.subTest(msg = f"Case {i}: {a} vs {b}"):
                distance = chessai.search.distance.manhattan_distance(a, b)
                for expected_distance in expected_distances:
                    self.assertAlmostEqual(expected_distance, distance)

                node = chessai.search.position.PositionSearchNode(a, test_board)
                problem = chessai.search.position.PositionSearchProblem(
                        test_state,
                        start_position = a,
                        goal_positions = [b])

                heuristic_distances = chessai.search.distance.manhattan_heuristic(node, problem)
                for (expected_distance, heuristic_distance) in zip(expected_distances, heuristic_distances):
                    self.assertAlmostEqual(expected_distance, heuristic_distance)

    def test_euclidean_base(self):
        """ Test Euclidean distance and heuristic. """

        test_board = chessai.core.board.load_path('tour-base')
        test_state = chessai.core.gamestate.GameState(seed = 4, board = test_board)

        # [(a, b, expected), ...]
        test_cases = [
            # Identity
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(0, 0), [0.0]),

            # Lateral
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(1, 0), [1.0]),
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(0, 1), [1.0]),
            (chessai.core.square.Square.from_file_rank(1, 0), chessai.core.square.Square.from_file_rank(0, 0), [1.0]),
            (chessai.core.square.Square.from_file_rank(0, 1), chessai.core.square.Square.from_file_rank(0, 0), [1.0]),

            # Diagonal
            (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(1, 1), [2.0 ** 0.5]),
            (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(2, 2), [2.0 ** 0.5]),
            (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(0, 0), [2.0 ** 0.5]),
        ]

        for (i, test_case) in enumerate(test_cases):
            (a, b, expected_distances) = test_case
            with self.subTest(msg = f"Case {i}: {a} vs {b}"):
                distance = chessai.search.distance.euclidean_distance(a, b)
                for expected_distance in expected_distances:
                    self.assertAlmostEqual(expected_distance, distance)

                node = chessai.search.position.PositionSearchNode(a, test_board)
                problem = chessai.search.position.PositionSearchProblem(
                        test_state,
                        start_position = a,
                        goal_positions = [b])

                heuristic_distances = chessai.search.distance.euclidean_heuristic(node, problem)
                for (expected_distance, heuristic_distance) in zip(expected_distances, heuristic_distances):
                    self.assertAlmostEqual(expected_distance, heuristic_distance)

    # def test_maze_base(self):
    #     """ Test maze distance. """

    #     test_board = chessai.core.board.load_path('tour-base')
    #     test_state = chessai.core.gamestate.GameState(seed = 4, board = test_board)

    #     # Note that the distances will be random because we are using random search.

    #     # [(a, b, expected), ...]
    #     test_cases = [
    #         # Identity
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(1, 1), 0.0),

    #         # Lateral
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(2, 1), 5.0),
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(1, 2), 1.0),
    #         (chessai.core.square.Square.from_file_rank(2, 1), chessai.core.square.Square.from_file_rank(1, 1), 1.0),
    #         (chessai.core.square.Square.from_file_rank(1, 2), chessai.core.square.Square.from_file_rank(1, 1), 5.0),

    #         # Diagonal
    #         (chessai.core.square.Square.from_file_rank(2, 1), chessai.core.square.Square.from_file_rank(3, 2), 44.0),
    #         (chessai.core.square.Square.from_file_rank(3, 5), chessai.core.square.Square.from_file_rank(4, 4), 78.0),
    #     ]

    #     for (i, test_case) in enumerate(test_cases):
    #         (a, b, expected) = test_case
    #         with self.subTest(msg = f"Case {i}: {a} vs {b}"):
    #             distance = chessai.search.distance.maze_distance(a, b, state = test_state)
    #             self.assertAlmostEqual(expected, distance)

    # def test_distanceprecomputer_base(self):
    #     """ Test precomputing distances. """

    #     test_board = chessai.core.board.load_path('tour-base')
    #     precomputer = chessai.search.distance.DistancePreComputer()
    #     precomputer.compute(test_board)

    #     # [(a, b, expected), ...]
    #     test_cases = [
    #         (chessai.core.square.Square.from_file_rank(-1, -1), chessai.core.square.Square.from_file_rank(-2, -2), None),
    #         (chessai.core.square.Square.from_file_rank(0, 0), chessai.core.square.Square.from_file_rank(0, 0), None),

    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(1, 2), 1.0),
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(3, 5), 6.0),
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(3, 4), 7.0),
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(4, 4), 6.0),
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(5, 2), 5.0),
    #         (chessai.core.square.Square.from_file_rank(1, 1), chessai.core.square.Square.from_file_rank(5, 1), 6.0),

    #         (chessai.core.square.Square.from_file_rank(3, 5), chessai.core.square.Square.from_file_rank(4, 4), 2.0),
    #     ]

    #     for (i, test_case) in enumerate(test_cases):
    #         (a, b, expected) = test_case
    #         with self.subTest(msg = f"Case {i}: {a} vs {b}"):
    #             distance_forward = precomputer.get_distance(a, b)
    #             self.assertAlmostEqual(expected, distance_forward)

    #             distance_backwards = precomputer.get_distance(b, a)  # pylint: disable=arguments-out-of-order
    #             self.assertAlmostEqual(distance_forward, distance_backwards)
