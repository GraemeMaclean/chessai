import edq.testing.unittest

import chessai.core.board
import chessai.core.action
import chessai.core.coordinate
import chessai.core.piece
import chessai.core.types

class BoardTest(edq.testing.unittest.BaseTest):
    """ Test Board functionality. """

    def test_push_and_pop_no_capture(self):
        """ Test push + pop with no capture. """

        # [(start_coordinate, end_coordinate, piece), ...]
        test_cases: list[tuple[
            chessai.core.coordinate.Coordinate,
            chessai.core.coordinate.Coordinate,
            chessai.core.piece.Piece,
        ]] = [
            (
                chessai.core.coordinate.Coordinate(1, 1),
                chessai.core.coordinate.Coordinate(1, 2),
                chessai.core.piece.Piece(
                    chessai.core.types.PieceType.PAWN,
                    chessai.core.types.Color.WHITE,
                ),
            ),
            (
                chessai.core.coordinate.Coordinate(3, 3),
                chessai.core.coordinate.Coordinate(4, 5),
                chessai.core.piece.Piece(
                    chessai.core.types.PieceType.KNIGHT,
                    chessai.core.types.Color.BLACK,
                ),
            ),
        ]

        for (i, (start_coordinate, end_coordinate, piece)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}"):
                board = chessai.core.board.Board(pieces = {
                    start_coordinate: piece
                })

                action = chessai.core.action.Action(start_coordinate, end_coordinate)

                record = board.push(action)

                # Pushed correctly
                self.assertIsNone(board.get(start_coordinate))
                self.assertEqual(piece, board.get(end_coordinate))

                # Pop restores
                board.pop(record)

                self.assertIsNone(board.get(end_coordinate))
                self.assertEqual(piece, board.get(start_coordinate))

    def test_push_and_pop_with_capture(self):
        """ Test push + pop with capture restoration. """

        # [(attacker_piece, victim_piece), ...]
        test_cases: list[tuple[
            chessai.core.piece.Piece,
            chessai.core.piece.Piece,
        ]] = [
            (
                chessai.core.piece.Piece(
                    chessai.core.types.PieceType.PAWN,
                    chessai.core.types.Color.WHITE,
                ),
                chessai.core.piece.Piece(
                    chessai.core.types.PieceType.KNIGHT,
                    chessai.core.types.Color.BLACK,
                ),
            ),
        ]

        for (i, (attacker_piece, victim_piece)) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}"):

                start_coordinate = chessai.core.coordinate.Coordinate(1, 1)
                end_coordinate = chessai.core.coordinate.Coordinate(2, 2)

                board = chessai.core.board.Board(pieces = {
                    start_coordinate: attacker_piece,
                    end_coordinate: victim_piece,
                })

                action = chessai.core.action.Action(start_coordinate, end_coordinate)

                record = board.push(action)

                # Capture happened
                self.assertIsNone(board.get(start_coordinate))
                self.assertEqual(attacker_piece, board.get(end_coordinate))

                # Pop restores capture
                board.pop(record)

                self.assertEqual(attacker_piece, board.get(start_coordinate))
                self.assertEqual(victim_piece, board.get(end_coordinate))

    def test_is_valid(self):
        """ Test board validity constraints. """

        start = chessai.core.coordinate.Coordinate(-1, -1)
        piece = chessai.core.piece.Piece(
            chessai.core.types.PieceType.PAWN,
            chessai.core.types.Color.WHITE
        )

        with self.assertRaises(ValueError):
            chessai.core.board.Board(pieces = {
                start: piece
            })

    def test_has_piece(self):
        """ Test has_piece helper. """

        # [bool, ...]
        test_cases: list[bool] = [
            True,
            False,
        ]

        for (i, exists) in enumerate(test_cases):
            with self.subTest(msg=f"Case {i}"):

                coord = chessai.core.coordinate.Coordinate(0, 0)

                pieces = {}
                if exists:
                    pieces[coord] = chessai.core.piece.Piece(
                        chessai.core.types.PieceType.PAWN,
                        chessai.core.types.Color.WHITE
                    )

                board = chessai.core.board.Board(pieces = pieces)

                self.assertEqual(exists, board.has_piece(coord))

    def test_copy_is_deep(self):
        """ Test deep copy independence. """

        start = chessai.core.coordinate.Coordinate(0, 0)
        end = chessai.core.coordinate.Coordinate(1, 1)

        piece = chessai.core.piece.Piece(
            chessai.core.types.PieceType.PAWN,
            chessai.core.types.Color.WHITE
        )

        board = chessai.core.board.Board(pieces={start: piece})
        board_copy = board.copy()

        self.assertIsNot(board, board_copy)

        action = chessai.core.action.Action(start, end)
        _ = board_copy.push(action)

        # Original unchanged
        self.assertIsNotNone(board.get(start))
        self.assertIsNone(board.get(end))

        # Copy changed
        self.assertIsNone(board_copy.get(start))
        self.assertIsNotNone(board_copy.get(end))

    def test_all_pieces_and_coordinates(self):
        """ Test iteration helpers. """

        coord1 = chessai.core.coordinate.Coordinate(0, 0)
        coord2 = chessai.core.coordinate.Coordinate(1, 1)

        piece1 = chessai.core.piece.Piece(
            chessai.core.types.PieceType.PAWN,
            chessai.core.types.Color.WHITE
        )

        piece2 = chessai.core.piece.Piece(
            chessai.core.types.PieceType.KNIGHT,
            chessai.core.types.Color.BLACK
        )

        board = chessai.core.board.Board(pieces={
            coord1: piece1,
            coord2: piece2
        })

        pieces = list(board.all_pieces())
        coords = list(board.all_coordinates())

        self.assertEqual(2, len(pieces))
        self.assertEqual(2, len(coords))
        self.assertIn(coord1, coords)
        self.assertIn(coord2, coords)
