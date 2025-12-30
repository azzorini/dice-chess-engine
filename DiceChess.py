#!/usr/bin/python

import chess
import random
from copy import deepcopy

from typing import List, Dict, Self

pieces_list: List[chess.PieceType] = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
pieces_name_list: List[str] = ["Pawn", "Knight", "Bishop", "Rook", "Queen", "King"]

class DiceBoard(chess.Board):
    def __init__(self: Self, *args, **kwargs) -> Self:
        """Constructor that gives the arguments to the chess.Board constructor.
        It initializes the dice roll as an empty list and the ep_squares dict as
        a dictionary with empty lists of squares."""
        super().__init__(*args, **kwargs)
        self.ep_squares: Dict[bool, List[chess.Square]] = {chess.WHITE: [], chess.BLACK: []}
        self.dice_roll: List[chess.PieceType] = []

    def roll_dices(self: Self) -> None:
        """Roll the dices for the current player"""
        self.dice_roll = random.choices(pieces_list, k=3)
    
    def copy(self: Self, *, stack: bool | int = True) -> Self:
        "Copies the content of the DiceBoard"
        board_copy: DiceBoard = super().copy(stack=stack)
        board_copy.ep_squares = deepcopy(self.ep_squares)
        board_copy.dice_roll = self.dice_roll.copy()
        return board_copy

    def _get_pseudo_moves(self: Self) -> List[chess.Move]:
        """Get possible moves compatible with the dices.
        If there is only one piece left these are all the possible moves."""
        return [move for move in self.pseudo_legal_moves_dice if
                ((not (castling := self.is_castling(move))) and (piece := self.piece_at(move.from_square))
                 and (piece.piece_type in self.dice_roll)) or (castling and chess.KING in self.dice_roll and chess.ROOK in self.dice_roll)]
    
    def _get_moves_3(self: Self) -> List[chess.Move]:
        """Get possible moves when there are three reamining pieces in the dice."""
        pseudo_moves: List[chess.Move] = self._get_pseudo_moves()
        count_list: List[int] = [1 for _ in pseudo_moves]
        max_count: int = 1
        for i, move in enumerate(pseudo_moves):
            board_p1: DiceBoard = self.copy(stack=False)
            board_p1.push(move, make_changes = True)
            pseudo_moves_p1: List[Move] = board_p1._get_pseudo_moves()
            if self.is_castling(move):
                count_list[i] = 2
                if max_count < 2:
                    max_count = 2
                if len(pseudo_moves_p1) > 0:
                    count_list[i] = 3
                    max_count = 3
            elif len(pseudo_moves_p1) > 0:
                count_list[i] = 2
                if max_count < 2:
                    max_count = 2
                for move_p1 in pseudo_moves_p1:
                    if board_p1.is_castling(move_p1):
                        count_list[i] = 3
                        max_count = 3
                        break
                    
                    board_p2: DiceBoard = board_p1.copy(stack=False)
                    board_p2.push(move_p1, make_changes = True)
                    pseudo_moves_p2: List[Move] = board_p2._get_pseudo_moves()
                    if len(pseudo_moves_p2) > 0:
                        count_list[i] = 3
                        max_count = 3
                        break # If there are three moves already (starting from our original move) we stop checking the other options
        
        return [move for move, count in zip(pseudo_moves, count_list) if count == max_count or ((captured := self.piece_at(move.to_square)) and captured.piece_type == chess.KING)]
    
    def _get_moves_2(self: Self) -> List[chess.Move]:
        """Get possible moves when there are two reamining pieces in the dice."""
        pseudo_moves: List[chess.Move] = self._get_pseudo_moves()
        count_list: List[int] = [1 for _ in pseudo_moves]
        max_count: int = 1
        for i, move in enumerate(pseudo_moves):
            if self.is_castling(move):
                count_list[i] = 2
                max_count = 2
            else:
                board_p1: DiceBoard = self.copy(stack=False)
                board_p1.push(move, make_changes = True)
                pseudo_moves_p1: List[chess.Move] = board_p1._get_pseudo_moves()
                if len(pseudo_moves_p1) > 0:
                    count_list[i] = 2
                    max_count = 2
        
        return [move for move, count in zip(pseudo_moves, count_list) if count == max_count or ((captured := self.piece_at(move.to_square)) and captured.piece_type == chess.KING)]

    def get_moves(self: Self) -> List[chess.Move]:
        """Get possible moves in current position"""
        nDices: int = len(self.dice_roll)
        if nDices == 0:
            return []
        elif nDices == 1:
            return self._get_pseudo_moves()
        elif nDices == 2:
            return self._get_moves_2()
        elif nDices == 3:
            return self._get_moves_3()
        else:
            raise ValueError("This class is not coded for more than three dices.")
    
    def push(self: Self, move: chess.Move, make_changes: bool = False):
        """Push a move, managing extended en passant and multi-move turns."""
        color: bool = self.turn
        opponent: bool = not color

        piece: chess.Piece = self.piece_at(move.from_square)
        is_castling: bool = self.is_castling(move)
        is_pawn: bool = piece and piece.piece_type == chess.PAWN
        ep_capture_square: None | chess.Square = None

        # Detect custom en passant captures
        if (
            make_changes
            and is_pawn
            and move.to_square in self.ep_squares[color]
            and not self.piece_at(move.to_square)  # target is empty
        ):
            # This is an en passant capture
            ep_capture_square = (
                move.to_square + (8 if color == chess.BLACK else -8)
            )  # square of captured pawn

            # Remove captured pawn manually
            self.remove_piece_at(ep_capture_square)

            # Remove ep square
            self.ep_squares[color].remove(move.to_square)

        # Execute the move normally
        super().push(move)
        self.turn = color
        self.ep_square = None

        if make_changes:
            try:
                self.dice_roll.remove(piece.piece_type)
                if is_castling:
                    self.dice_roll.remove(chess.ROOK)
            except ValueError:
                pass

        # Handle new en passant rights
        if is_pawn and make_changes:
            from_rank: int = chess.square_rank(move.from_square)
            to_rank: int = chess.square_rank(move.to_square)
            if abs(to_rank - from_rank) == 2:
                ep_sq = (move.from_square + move.to_square) // 2
        
                # Check for adjacent opponent pawns before granting EP right
                to_file: int = chess.square_file(move.to_square)
                to_rank: int = chess.square_rank(move.to_square)
        
                has_adjacent_opponent_pawn: bool = False
                for side_file in (to_file - 1, to_file + 1):
                    if 0 <= side_file <= 7:  # stay on board
                        neighbor_sq: chess.Square = chess.square(side_file, to_rank)
                        piece: chess.Piece = self.piece_at(neighbor_sq)
                        if piece and piece.piece_type == chess.PAWN and piece.color == opponent:
                            has_adjacent_opponent_pawn = True
                            break
        
                # Only add EP square if opponent pawn adjacent
                if has_adjacent_opponent_pawn and not ep_sq in self.ep_squares[opponent]:
                    self.ep_squares[opponent].append(ep_sq)
    
    @property
    def pseudo_legal_moves_dice(self: Self) -> List[chess.Move]:
        """All standard pseudo-legal moves + custom en passant moves."""
        moves: List[chess.Move] = list(super().pseudo_legal_moves)
        color: bool = self.turn
        opponent: bool = not color

        # Add all custom en passant moves for this side
        for ep_sq in self.ep_squares[color]:
            # Rank of target square (where capturing pawn will land)
            ep_rank: int = chess.square_rank(ep_sq)
            ep_file: int = chess.square_file(ep_sq)

            # Direction depends on side to move
            direction: int = 1 if color == chess.WHITE else -1
            captured_sq: chess.Square = chess.square(ep_file, ep_rank - direction)

            # For each side-adjacent file, check for capturing pawn
            for df in (-1, 1):
                pawn_file: int = ep_file + df
                if 0 <= pawn_file <= 7:
                    pawn_sq: chess.Square = chess.square(pawn_file, ep_rank - direction)
                    piece: chess.Piece = self.piece_at(pawn_sq)
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        # Create en passant move
                        move: chess.Move = chess.Move(pawn_sq, ep_sq)
                        # Double-check that the captured square really contains an opponent pawn
                        captured_piece: chess.Piece = self.piece_at(captured_sq)
                        if captured_piece and captured_piece.piece_type == chess.PAWN and captured_piece.color == opponent:
                            moves.append(move)

        return moves

    def is_check(self: Self) -> bool:
        """In dice chess the checks do not matter, so I will always return False.
        This is made so the castling works fine."""
        return False

    def is_checkmate(self: Self) -> bool:
        """In dice chess the checks do not matter, so I will always return False."""
        return False
    
    def _attacked_for_king(self: Self, king_square: chess.Square, color: bool) -> bool:
        """Dice Chess ignores checks; the king is never considered attacked."""
        return False
    
    def is_stalemate(self: Self) -> bool:
        """Dice Chess ignores checks; as long as you still have your king there are always potential moves."""
        return False
    
    def san(self: Self, move: chess.Move) -> str:
        """Return SAN (standard algebraic notation) for a move, including custom en passant."""
        color: bool = self.turn
    
        # Check if this move is a custom en passant capture
        is_pawn: bool = (piece := self.piece_at(move.from_square)) and piece.piece_type == chess.PAWN
        if (
            is_pawn
            and move.to_square in self.ep_squares[color]
            and not self.piece_at(move.to_square)
        ):
            # Temporarily tell python-chess that this is an en passant move
            self.ep_square = move.to_square
    
        # Get SAN from parent class (now en passant-aware)
        san_str: str = super().san(move)
    
        # Restore ep_square
        self.ep_square = None
        return san_str

    def is_game_over(self: Self, move: chess.Move) -> bool:
        """Check if the move ends the game (king capture)"""
        captured: None | chess.Piece = self.piece_at(move.to_square)
        if captured and captured.piece_type == chess.KING:
            return True
        return False

    def next_player(self: Self) -> None:
        """Change to the next player"""
        color: bool = self.turn
        self.ep_squares[color] = []
        self.turn = not color

def main() -> None:
    """Main function, mainly thought for debugging. If you want to play use the notebook."""
    board: DiceBoard = DiceBoard()
    while True:
        board.roll_dices()

        print("Roll: ", [pieces_name_list[p-1] for p in board.dice_roll])
        move_list: List[chess.Move] = board.get_moves()
        nMoves: int = len(move_list)
        while nMoves > 0:
            print("Remaining pieces: ", [pieces_name_list[p-1] for p in board.dice_roll])
            print(board)
            print("Available moves:")
            for i, move in enumerate(move_list, start=1):
                print('\t', i, board.san(move))
            
            choice: int = 0
            while choice < 1 or choice > nMoves:
                print(f"Choose a move (1-{nMoves}): ")
                try:
                    choice = int(input())
                except ValueError:
                    choice = 0
            
            is_game_over: bool = board.is_game_over(move_list[choice-1])
            board.push(move_list[choice-1], make_changes = True)
            if is_game_over:
                print(board)
                print(("White" if board.turn == chess.WHITE else "Black") + " wins.")
                return
            move_list = board.get_moves()
            nMoves = len(move_list)

        print(board)
        print("Next player (current player out of moves)")
        board.next_player()


if __name__ == "__main__":
    main()