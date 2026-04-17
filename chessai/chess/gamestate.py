import random
import typing

import chessai.chess.piece
import chessai.core.action
import chessai.core.gamestate

class GameState(chessai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

    def process_turn(self,
            action: chessai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

        self.push(action)

    def game_complete(self) -> tuple[list[chessai.core.types.Color], float]:
        winners = self.get_winners()

        # Score is based on white's perspective using standard chess scoring.
        if (chessai.core.types.Color.WHITE in winners):
            score = 1.0
        elif (chessai.core.types.Color.BLACK in winners):
            score = 0.0
        else:
            score = 0.5

        return (winners, score)

    def _should_reset_halfmove_clock(self, action: chessai.core.action.Action, piece: chessai.core.piece.Piece) -> bool:
        return (piece == chessai.chess.piece.Pawn)

    def _get_pseudo_legal_moves(self) -> list[chessai.core.action.Action]:
        # Get the base movement from all pieces.
        actions = self._expand_movement_vectors()

        # Add any castling moves.
        actions = self._get_castling_moves()

        # Add any pawn double pushes.
        actions.extend(self._get_pawn_double_pushes())

        # Add any en-passant captures.
        actions.extend(self._get_en_passant_captures())

        return actions

    # # TODO(Lucas): Debatably move this to piece functionality.
    def _expand_movement_vectors(self) -> list[chessai.core.action.Action]:
        """ Expand the movement vectors into the pseudo-legal moves. """

        actions: list[chessai.core.action.Action] = []

        # Determine the rank for pawn promotions.
        if (self.turn == chessai.core.types.Color.WHITE):
            promotion_rank = self.board.num_ranks - 1
        else:
            promotion_rank = 0

        for (coordinate, piece) in self.board.pieces.items():
            if (piece.color != self.turn):
                continue

            movement_vectors = piece.move_vectors(coordinate)
            for movement_vector in movement_vectors:
                current_coordinate = coordinate

                num_repetitions = movement_vector.num_repetitions
                while ((num_repetitions == -1) or (num_repetitions > 0)):
                    current_coordinate = current_coordinate.offset(movement_vector.file_delta, movement_vector.rank_delta)
                    if (not self.board._is_within_bounds(current_coordinate)):
                        break

                    occupant = self.board.get(current_coordinate)

                    is_occupied = occupant is not None
                    is_enemy    = (occupant is not None) and (occupant.color != piece.color)
                    is_ally     = (occupant is not None) and (occupant.color == piece.color)

                    # No movement type can move on top of an ally.
                    if (is_ally):
                        break

                    # Push movement types cannot capture.
                    if ((movement_vector.kind == chessai.core.piece.MoveKind.PUSH) and is_occupied):
                        break

                    # Capture movement types must target an enemy.
                    if ((movement_vector.kind == chessai.core.piece.MoveKind.CAPTURE) and (not is_enemy)):
                        break

                    # Check if this action would lead to a pawn promotion.
                    if ((piece == chessai.chess.piece.Pawn) and (current_coordinate.rank == promotion_rank)):
                        actions.extend(self._get_promotion_actions(coordinate, current_coordinate))
                    else:
                        actions.append(chessai.core.action.Action(coordinate, current_coordinate))

                    if (is_occupied):
                        break

                    num_repetitions -= 1

        return actions

    def _process_special_move(self, action: chessai.core.action.Action, piece: chessai.core.piece.Piece) -> bool:
        # Handle promoting pieces.
        if (action.promotion is not None):
            self._handle_promotion(action, piece)

        # Detect castling by seeing if the king moved more than two files.
        if ((piece == chessai.chess.piece.King)
                and (action.start_coordinate.file_distance(action.end_coordinate) > 1)):
            self._handle_castling(action, piece)
            return False

        # Detect En-passant by checking if a pawn moves diagonally to an empty square.
        if ((piece == chessai.chess.piece.Pawn)
                and (action.start_coordinate.file_distance(action.end_coordinate) == 1)
                and (self.board.get(action.end_coordinate) is None)):
            self._handle_en_passant(action, piece)
            return True

        return False

    def _handle_castling(self, action: chessai.core.action.Action, piece: chessai.core.piece.Piece) -> None:
        # Build the rook action for castling.
        rook_action: chessai.core.action.Action | None = None
        back_rank = action.start_coordinate.rank

        if (action.end_coordinate.file > action.start_coordinate.file):
            # Kingside: rook moves from the h-file to just right of the king's destination.
            rook_start = chessai.core.coordinate.Coordinate(self.board.num_files - 1, back_rank)
            rook_end   = chessai.core.coordinate.Coordinate(action.end_coordinate.file - 1, back_rank)
        else:
            # Queenside: rook moves from the a-file to just left of the king's destination.
            rook_start = chessai.core.coordinate.Coordinate(0, back_rank)
            rook_end   = chessai.core.coordinate.Coordinate(action.end_coordinate.file + 1, back_rank)

        rook_action = chessai.core.action.Action(rook_start, rook_end)

        # Move the rook for castling.
        self.board.push(rook_action)

        # Update castling rights, based on the action.
        self._update_castling_rights(action, piece)

    def _handle_en_passant(self, action: chessai.core.action.Action, piece: chessai.core.piece.Piece) -> None:
        # The captured pawn is on the same rank as the moving pawn, on the destination file.
        captured_piece_coordinate = chessai.core.coordinate.Coordinate(
            action.end_coordinate.file,
            action.start_coordinate.rank,
        )

        # Remove the en-passant captured pawn from its actual square.
        self.board.remove(captured_piece_coordinate)

        # Update the en-passant target square, based on the action.
        self.en_passant_coordinate = self._compute_en_passant(action, piece)

    def _handle_promotion(self, action: chessai.core.action.Action, piece: chessai.core.piece.Piece) -> None:
        # Handle promotion by replacing the pawn with the promoted piece.
        if (action.promotion is not None):
            self.board.set(action.promotion, action.end_coordinate)

    def _get_castling_moves(self) -> list[chessai.core.action.Action]:
        """ Get all pseudo-legal castling moves for the current player. """

        # Determine the back rank and castling rights for the current player.
        if (self.turn == chessai.core.types.Color.WHITE):
            back_rank           = 0
            kingside_rights     = self.castling_rights.white_kingside
            queenside_rights    = self.castling_rights.white_queenside
        else:
            back_rank           = self.board.num_ranks - 1
            kingside_rights     = self.castling_rights.black_kingside
            queenside_rights    = self.castling_rights.black_queenside

        if ((not kingside_rights) and (not queenside_rights)):
            return []

        # Find the king.
        king_coord: chessai.core.coordinate.Coordinate | None = None
        for (coordinate, piece) in self.board.pieces.items():
            if (piece != chessai.chess.piece.King):
                continue

            if (piece.color != self.turn):
                continue

            king_coord = coordinate

        if ((king_coord is None) or (king_coord.rank != back_rank)):
            return []

        actions: list[chessai.core.action.Action] = []

        # Add Kingside castling.
        if (kingside_rights):
            rook_coord = chessai.core.coordinate.Coordinate((self.board.num_files - 1), back_rank)
            rook_piece = self.board.get(rook_coord)

            # Check that the files to the right of the king and left of the rook are empty.
            all_empty = True
            file = king_coord.file + 1
            while (file < rook_coord.file):
                empty_coord = chessai.core.coordinate.Coordinate(file, back_rank)

                if (self.board.has_piece(empty_coord)):
                    all_empty = False
                    break

                file = file + 1

            if ((rook_piece is not None)
                    and (rook_piece == chessai.chess.piece.Rook)
                    and (rook_piece.color == self.turn)
                    and (all_empty)):
                king_dest = chessai.core.coordinate.Coordinate((self.board.num_files - 2), back_rank)
                actions.append(chessai.core.action.Action(king_coord, king_dest))

        # Add Queenside castling.
        if (queenside_rights):
            rook_coord = chessai.core.coordinate.Coordinate(0, back_rank)
            rook_piece = self.board.get(rook_coord)

            # Check that the files to the right of the king and left of the rook are empty.
            all_empty = True
            file = king_coord.file - 1
            while (file > 0):
                empty_coord = chessai.core.coordinate.Coordinate(file, back_rank)

                if (self.board.has_piece(empty_coord)):
                    all_empty = False
                    break

                file = file - 1

            if ((rook_piece is not None)
                    and (rook_piece == chessai.chess.piece.Rook)
                    and (rook_piece.color == self.turn)
                    and (all_empty)):
                king_dest = chessai.core.coordinate.Coordinate(2, back_rank)
                actions.append(chessai.core.action.Action(king_coord, king_dest))

        return actions

    def _get_pawn_double_pushes(self) -> list[chessai.core.action.Action]:
        """ Get all pseudo-legal pawn double push moves for the current player. """

        if (self.turn == chessai.core.types.Color.WHITE):
            start_rank = 1
            direction  = 1
        else:
            start_rank = self.board.num_ranks - 2
            direction  = -1

        actions: list[chessai.core.action.Action] = []

        for (coordinate, piece) in self.board.pieces.items():
            if (piece != chessai.chess.piece.Pawn):
                continue

            if (piece.color != self.turn):
                continue

            if (coordinate.rank != start_rank):
                continue

            # Both the single and double push squares must be empty.
            single_push_coord = coordinate.offset(0, direction)
            if (self.board.has_piece(single_push_coord)):
                continue

            double_push_coord = coordinate.offset(0, direction * 2)
            if (self.board.has_piece(double_push_coord)):
                continue

            actions.append(chessai.core.action.Action(coordinate, double_push_coord))

        return actions

    def _get_en_passant_captures(self) -> list[chessai.core.action.Action]:
        """ Get all pseudo-legal en-passant captures for the current player. """

        actions: list[chessai.core.action.Action] = []

        if (self.en_passant_coordinate is None):
            return actions

        if (self.turn == chessai.core.types.Color.WHITE):
            # The en-passant square encodes the square that must be taken.
            # So, the pawn that can attack it will be one rank below for white.
            capturing_rank = self.en_passant_coordinate.rank - 1
        else:
            capturing_rank = self.en_passant_coordinate.rank + 1

        # The pawn will have to be on an adjacent file.
        for file_delta in [-1, 1]:
            candidate_capture_coord = chessai.core.coordinate.Coordinate(
                self.en_passant_coordinate.file + file_delta,
                capturing_rank,
            )

            if (not self.board._is_within_bounds(candidate_capture_coord)):
                continue

            piece = self.board.get(candidate_capture_coord)
            if (piece is None):
                continue

            if (piece != chessai.chess.piece.Pawn):
                continue

            if (piece.color != self.turn):
                continue

            actions.append(chessai.core.action.Action(candidate_capture_coord, self.en_passant_coordinate))

        return actions

    def _get_promotion_actions(self,
            start_coordinate: chessai.core.coordinate.Coordinate,
            end_coordinate: chessai.core.coordinate.Coordinate) -> list[chessai.core.action.Action]:
        """
        Expand a pawn move that reaches the back rank into one action per promotable piece type.

        Called when a pawn reaches the back rank of the opposing side.
        Always returns exactly four actions (queen, rook, bishop, knight).
        """

        return [
            chessai.core.action.Action(start_coordinate, end_coordinate, chessai.chess.piece.Queen(self.turn)),
            chessai.core.action.Action(start_coordinate, end_coordinate, chessai.chess.piece.Rook(self.turn)),
            chessai.core.action.Action(start_coordinate, end_coordinate, chessai.chess.piece.Bishop(self.turn)),
            chessai.core.action.Action(start_coordinate, end_coordinate, chessai.chess.piece.Knight(self.turn)),
        ]

    def _update_castling_rights(self,
            action: chessai.core.action.Action,
            piece: chessai.core.piece.Piece) -> None:
        """ Revoke castling rights that are no longer valid after the given move. """

        white_kingside_rook  = chessai.core.coordinate.Coordinate(self.board.num_files - 1, 0)
        white_queenside_rook = chessai.core.coordinate.Coordinate(0, 0)
        black_kingside_rook  = chessai.core.coordinate.Coordinate(self.board.num_files - 1, self.board.num_ranks - 1)
        black_queenside_rook = chessai.core.coordinate.Coordinate(0, self.board.num_ranks - 1)

        # King moves, which forfeits both rights for that color.
        if (piece == chessai.chess.piece.King):
            if (piece.color == chessai.core.types.Color.WHITE):
                self.castling_rights.white_kingside  = False
                self.castling_rights.white_queenside = False
            else:
                self.castling_rights.black_kingside  = False
                self.castling_rights.black_queenside = False

        # Rook moves from its starting square.
        if (action.start_coordinate == white_kingside_rook):
            self.castling_rights.white_kingside = False

        if (action.start_coordinate == white_queenside_rook):
            self.castling_rights.white_queenside = False

        if (action.start_coordinate == black_kingside_rook):
            self.castling_rights.black_kingside = False

        if (action.start_coordinate == black_queenside_rook):
            self.castling_rights.black_queenside = False

        # Rook captured on its starting square.
        if (action.end_coordinate == white_kingside_rook):
            self.castling_rights.white_kingside = False

        if (action.end_coordinate == white_queenside_rook):
            self.castling_rights.white_queenside = False

        if (action.end_coordinate == black_kingside_rook):
            self.castling_rights.black_kingside = False

        if (action.end_coordinate == black_queenside_rook):
            self.castling_rights.black_queenside = False

    def _compute_en_passant(self,
            action: chessai.core.action.Action,
            piece: chessai.core.piece.Piece) -> chessai.core.coordinate.Coordinate | None:
        """
        Return the new en-passant target square after this move, or None.

        A target square is set only when a pawn advances two ranks.
        The target is the square the pawn passed through (i.e. one rank behind the destination), which is standard FEN notation.
        """

        if (piece != chessai.chess.piece.Pawn):
            return None

        if (action.start_coordinate.rank_distance(action.end_coordinate) != 2):
            return None

        # The en-passant target is the square the pawn skipped over.
        passed_rank = (action.start_coordinate.rank + action.end_coordinate.rank) // 2
        return chessai.core.coordinate.Coordinate(action.start_coordinate.file, passed_rank)

def base_eval(
        state: GameState,
        action: chessai.core.action.Action | None = None,
        agent: typing.Any | None = None,
        **kwargs: typing.Any) -> float:
    """
    The most basic evaluation function, which just uses the difference in piece value on the board.
    """

    # TODO(Lucas): Fix typing info and move alias.
    piece_values: dict[chessai.core.piece.Piece, int] = {
        chessai.chess.piece.Pawn: 1,
        chessai.chess.piece.Knight: 3,
        chessai.chess.piece.Bishop: 3,
        chessai.chess.piece.Rook: 5,
        chessai.chess.piece.Queen: 9,
        chessai.chess.piece.King: 9999,
    }

    # The difference in pieces from white's perspective.
    board_value = 0
    for (_, piece) in state.board.pieces.items():
        piece_value = piece_values.get(piece, 0)
        if (piece.color == chessai.core.types.Color.WHITE):
            board_value += piece_value
        else:
            board_value -= piece_value

    if (state.turn == chessai.core.types.Color.WHITE):
        return board_value

    # The piece difference is the opposite for black.
    return -1 * board_value
