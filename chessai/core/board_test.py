import edq.testing.unittest

import chessai.chess.piece
import chessai.core.board
import chessai.core.action
import chessai.core.coordinate
import chessai.core.types

class BoardTest(edq.testing.unittest.BaseTest):
    """ Test Board functionality. """

    def test_push_no_capture(self):
        """ Test push with no capture. """

        start_coordinate = chessai.core.coordinate.Coordinate(1, 1)
        end_coordinate = chessai.core.coordinate.Coordinate(1, 2)
        piece = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)

        board = chessai.core.board.Board(pieces = {
            start_coordinate: piece
        })

        action = chessai.core.action.MoveAction(start_coordinate, end_coordinate)
        was_capture = board.push(action)

        # Not a capture
        self.assertFalse(was_capture)

        # Piece moved correctly
        self.assertIsNone(board.get(start_coordinate.file, start_coordinate.rank))
        self.assertEqual(piece, board.get(end_coordinate.file, end_coordinate.rank))

    def test_push_with_capture(self):
        """ Test push with capture. """

        start_coordinate = chessai.core.coordinate.Coordinate(1, 1)
        end_coordinate = chessai.core.coordinate.Coordinate(2, 2)

        attacker_piece = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)
        victim_piece = chessai.chess.piece.Knight(chessai.core.types.Color.BLACK)

        board = chessai.core.board.Board(pieces = {
            start_coordinate: attacker_piece,
            end_coordinate: victim_piece,
        })

        action = chessai.core.action.MoveAction(start_coordinate, end_coordinate)
        was_capture = board.push(action)

        # Was a capture
        self.assertTrue(was_capture)

        # Capture happened
        self.assertIsNone(board.get(start_coordinate.file, start_coordinate.rank))
        self.assertEqual(attacker_piece, board.get(end_coordinate.file, end_coordinate.rank))

    def test_push_with_promotion(self):
        """ Test push with pawn promotion. """

        start_coordinate = chessai.core.coordinate.Coordinate(0, 6)
        end_coordinate = chessai.core.coordinate.Coordinate(0, 7)

        pawn = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)
        promotion_piece = chessai.chess.piece.Queen(chessai.core.types.Color.WHITE)

        board = chessai.core.board.Board(pieces = {
            start_coordinate: pawn
        })

        action = chessai.core.action.PromotionAction(start_coordinate, end_coordinate, promotion_piece)
        was_capture = board.push(action)

        # Not a capture
        self.assertFalse(was_capture)

        # Promoted piece is on the board
        self.assertIsNone(board.get(start_coordinate.file, start_coordinate.rank))
        promoted = board.get(end_coordinate.file, end_coordinate.rank)
        self.assertIsInstance(promoted, chessai.chess.piece.Queen)
        self.assertEqual(chessai.core.types.Color.WHITE, promoted.color)

    def test_is_valid(self):
        """ Test board validity constraints. """

        out_of_bounds = chessai.core.coordinate.Coordinate(-1, -1)
        piece = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)

        with self.assertRaises(ValueError):
            chessai.core.board.Board(pieces = {
                out_of_bounds: piece
            })

    def test_has_piece(self):
        """ Test has_piece helper. """

        coord = chessai.core.coordinate.Coordinate(0, 0)
        piece = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)

        # Empty board
        board = chessai.core.board.Board(pieces={})
        self.assertFalse(board.has_piece(coord))

        # Board with piece
        board = chessai.core.board.Board(pieces={coord: piece})
        self.assertTrue(board.has_piece(coord))

    def test_is_capture(self):
        """ Test is_capture helper. """

        start = chessai.core.coordinate.Coordinate(0, 0)
        end_empty = chessai.core.coordinate.Coordinate(1, 1)
        end_occupied = chessai.core.coordinate.Coordinate(2, 2)

        attacker = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)
        victim = chessai.chess.piece.Knight(chessai.core.types.Color.BLACK)

        board = chessai.core.board.Board(pieces={
            start: attacker,
            end_occupied: victim,
        })

        # Not a capture
        action_no_capture = chessai.core.action.MoveAction(start, end_empty)
        self.assertFalse(board.is_capture(action_no_capture))

        # Is a capture
        action_capture = chessai.core.action.MoveAction(start, end_occupied)
        self.assertTrue(board.is_capture(action_capture))

    def test_copy_is_deep(self):
        """ Test deep copy independence. """

        start = chessai.core.coordinate.Coordinate(0, 0)
        end = chessai.core.coordinate.Coordinate(1, 1)
        piece = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)

        board = chessai.core.board.Board(pieces={start: piece})
        board_copy = board.copy()

        # Modify the copy
        action = chessai.core.action.MoveAction(start, end)
        board_copy.push(action)

        # Original unchanged
        self.assertIsNotNone(board.get(start.file, start.rank))
        self.assertIsNone(board.get(end.file, end.rank))

        # Copy changed
        self.assertIsNone(board_copy.get(start.file, start.rank))
        self.assertIsNotNone(board_copy.get(end.file, end.rank))

    def test_all_pieces_and_coordinates(self):
        """ Test iteration helpers. """

        coord1 = chessai.core.coordinate.Coordinate(0, 0)
        coord2 = chessai.core.coordinate.Coordinate(1, 1)

        piece1 = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)
        piece2 = chessai.chess.piece.Knight(chessai.core.types.Color.BLACK)

        board = chessai.core.board.Board(pieces={
            coord1: piece1,
            coord2: piece2
        })

        pieces = board.all_pieces()
        coords = board.all_coordinates()

        self.assertEqual(2, len(pieces))
        self.assertEqual(2, len(coords))
        self.assertIn(piece1, pieces)
        self.assertIn(piece2, pieces)
        self.assertIn(coord1, coords)
        self.assertIn(coord2, coords)

    def test_set_and_remove(self):
        """ Test set and remove operations. """

        coord = chessai.core.coordinate.Coordinate(3, 3)
        piece = chessai.chess.piece.Rook(chessai.core.types.Color.WHITE)

        board = chessai.core.board.Board()

        # Set a piece
        board.set(piece, coord)
        self.assertEqual(piece, board.get(coord.file, coord.rank))

        # Remove the piece
        board.remove(coord)
        self.assertIsNone(board.get(coord.file, coord.rank))

        # Remove from empty coordinate (should not raise)
        board.remove(coord)
        self.assertIsNone(board.get(coord.file, coord.rank))

    def test_set_out_of_bounds_raises(self):
        """ Test that setting a piece out of bounds raises an error. """

        board = chessai.core.board.Board()
        piece = chessai.chess.piece.Pawn(chessai.core.types.Color.WHITE)
        out_of_bounds = chessai.core.coordinate.Coordinate(10, 10)

        with self.assertRaises(ValueError):
            board.set(piece, out_of_bounds)
