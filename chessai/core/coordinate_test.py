import typing

import edq.testing.unittest

import chessai.core.coordinate

class CoordinateTest(edq.testing.unittest.BaseTest):
    """ Test Coordinate functionality. """

    def test_from_uci(self):
        """ Test creating coordinates from UCI strings. """

        # [(uci, error_substring, expected_file, expected_rank), ...]
        test_cases: list[tuple[str, str | None, int, int]] = [
            # Base
            ('a1', None, 0, 0),
            ('h8', None, 7, 7),
            ('d5', None, 3, 4),

            # Extended UCI
            ('aa1', None, 26, 0),
            ('ab10', None, 27, 9),
            ('z26', None, 25, 25),

            # Case insensitivity
            ('A1', None, 0, 0),
            ('Aa1', None, 26, 0),

            # Errors
            ('', 'Improper Coordinate name', None, None),
            ('1a', 'Improper Coordinate name', None, None),
            ('a', 'Improper Coordinate name', None, None),
            ('11', 'Improper Coordinate name', None, None),
        ]

        for (i, test_case) in enumerate(test_cases):
            (uci, error_substring, expected_file, expected_rank) = test_case
            with self.subTest(msg=f"Case {i}:"):
                try:
                    coord = chessai.core.coordinate.Coordinate.from_uci(uci)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex))
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(expected_file, coord.file)
                self.assertEqual(expected_rank, coord.rank)

    def test_uci_round_trip(self):
        """ Test conversion to/from UCI strings. """

        # [(file, rank, uci), ...]
        test_cases: list[tuple[int, int, str]] = [
            (0, 0, 'a1'),
            (7, 7, 'h8'),
            (3, 4, 'd5'),
            (26, 0, 'aa1'),
            (27, 9, 'ab10'),
        ]

        for (i, (file, rank, expected_uci)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                coord = chessai.core.coordinate.Coordinate(file, rank)
                self.assertEqual(expected_uci, coord.uci())

                round_trip = chessai.core.coordinate.Coordinate.from_uci(coord.uci())
                self.assertEqual(coord, round_trip)

    def test_offset(self):
        """ Test coordinate offsets. """

        # [(coordinate, (file_delta, rank_delta), (expected_file, expected_rank)), ...]
        test_cases: list[tuple[chessai.core.coordinate.Coordinate, tuple[int, int], tuple[int, int]]]= [
            (chessai.core.coordinate.Coordinate(0, 0), (1, 1), (1, 1)),
            (chessai.core.coordinate.Coordinate(3, 3), (-1, 2), (2, 5)),
            (chessai.core.coordinate.Coordinate(5, 5), (0, -3), (5, 2)),
        ]

        for (i, (coordinate, (delta_file, delta_rank), (expected_file, expected_rank))) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                result = coordinate.offset(delta_file, delta_rank)

                expected_coordinate = chessai.core.coordinate.Coordinate(expected_file, expected_rank)
                self.assertEqual(result, expected_coordinate)

    def test_distances(self):
        """ Test distance calculations. """

        # [(coordinate_1, coordinate_2, file_dist, rank_dist, cheb, manhattan), ...]
        test_cases: list[tuple[chessai.core.coordinate.Coordinate, chessai.core.coordinate.Coordinate, int, int, int, int]] = [
            (
                chessai.core.coordinate.Coordinate(0, 0),
                chessai.core.coordinate.Coordinate(0, 0),
                0,
                0,
                0,
                0,
            ),
            (
                chessai.core.coordinate.Coordinate(0, 0),
                chessai.core.coordinate.Coordinate(3, 4),
                3,
                4,
                4,
                7,
            ),
            (
                chessai.core.coordinate.Coordinate(5, 5),
                chessai.core.coordinate.Coordinate(2, 1),
                3,
                4,
                4,
                7,
            ),
            (
                chessai.core.coordinate.Coordinate(7, 7),
                chessai.core.coordinate.Coordinate(0, 0),
                7,
                7,
                7,
                14,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (coordinate_1, coordinate_2, file_dist, rank_dist, cheb_dist, man_dist) = test_case
            with self.subTest(msg=f"Case {i}:"):
                self.assertEqual(file_dist, coordinate_1.file_distance(coordinate_2))
                self.assertEqual(rank_dist, coordinate_1.rank_distance(coordinate_2))
                self.assertEqual(cheb_dist, coordinate_1.chebyshev_distance(coordinate_2))
                self.assertEqual(man_dist, coordinate_1.manhattan_distance(coordinate_2))

    def test_dict_conversion(self):
        """ Test to_dict and from_dict. """

        test_cases = [
            (0, 0),
            (3, 4),
            (26, 10),
        ]

        for (i, (file, rank)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                coord = chessai.core.coordinate.Coordinate(file, rank)
                data = coord.to_dict()

                self.assertEqual(file, data['file'])
                self.assertEqual(rank, data['rank'])

                restored = chessai.core.coordinate.Coordinate.from_dict(data)
                self.assertEqual(file, restored.file)
                self.assertEqual(rank, restored.rank)

    def test_coordinates_from_dict(self):
        """ Test parsing coordinate lists from dicts. """

        # [(input_dict, expected_len, expected_uci_list), ...]
        test_cases: list[tuple[dict[str, typing.Any], int, list[str]]] = [
            (
                {},
                0,
                [],
            ),
            (
                {'coordinates': ['a1', 'b2', 'c3']},
                3,
                ['a1', 'b2', 'c3'],
            ),
            (
                {'coordinates': 'a1,b2,c3'},
                3,
                ['a1', 'b2', 'c3'],
            ),
            (
                {'coordinates': [{'file': 0, 'rank': 0}, {'file': 1, 'rank': 1}]},
                2,
                ['a1', 'b2'],
            ),
            (
                {'coordinates': ['a1', {'file': 1, 'rank': 1}, None, 123]},
                2,
                ['a1', 'b2'],
            ),
        ]

        for (i, (input_dict, expected_len, expected_uci)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}:"):
                coords = chessai.core.coordinate.coordinates_from_dict(input_dict)

                self.assertEqual(expected_len, len(coords))
                self.assertEqual(expected_uci, [c.uci() for c in coords])

    def test_null_coordinate(self):
        """ Test NULL_COORDINATE constant. """

        self.assertEqual(-1, chessai.core.coordinate.NULL_COORDINATE.file)
        self.assertEqual(-1, chessai.core.coordinate.NULL_COORDINATE.rank)
        self.assertEqual(chessai.core.coordinate.Coordinate(-1, -1), chessai.core.coordinate.NULL_COORDINATE)
