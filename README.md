# 🎲 Dice Chess (Python Implementation)

**Author:** *Azzorini*  
**License:** [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html)  
**Language:** Python 3.x  

---

## ♟️ Overview

This is an **open-source Python implementation** of the *Dice Chess* variant, built on top of the [python-chess](https://python-chess.readthedocs.io/) library.  
Each turn, a player rolls three dice that determine which pieces they may move.  
Unlike standard chess, **check and checkmate do not exist** — the game ends only when a king is captured.  

This project is **not affiliated with or endorsed by [dicechess.com](https://www.dicechess.com)**.  
It is an independent educational and hobby implementation of similar gameplay mechanics.

---

## ⚙️ Features

- Implements the main *Dice Chess* mechanics:
  - Random dice rolls determine allowed piece types per turn.  
  - Multi-move turns (up to three moves per roll).  
  - Castling requires both King + Rook dice and consumes both. 
  - Custom en passant system.  
  - A king capture ends the game.
- Fully playable from the command line. A notebook is included for a better experience. Even though I will consider creating a GUI. 
- Written in idiomatic Python 3 with type hints. 
- Uses `python-chess` for move generation and SAN notation.  
- License: GPL v3 (you are free to use, modify, and redistribute under the same license).

---

## 📖 Rules Summary

1. At the start of each turn, roll **three dice** — each die shows one of the six piece types.
2. The current player may make **up to three moves**, each move corresponding to one of the rolled pieces.
3. The player is forced to **maximize** the number of **moves** that can be made on the turn. This engine automatically compute the moves that lead to a maximum number of moves on the turn.
4. A player’s turn ends when:
   - All three dice are used, or  
   - The player has no legal moves remaining.  
5. **Castling** is allowed if it is legal in standard chess (ignoring checks) *and* both King + Rook appear in the dice. The move consumes both dice.  
6. **En passant** is available only until the opponent’s next full turn and only if a pawn capable of capturing en passant is adjacent.  
7. **Check, checkmate, and stalemate do not apply.**  
   The game continues until a king is captured.  
8. If a player cannot move any of their rolled pieces, the turn passes to the opponent.  

---

## 🧩 Requirements

- Python ≥ 3.9  
- [python-chess](https://pypi.org/project/python-chess/)  
  ```bash
  pip install python-chess
  ```

---

## 🧠 Class & Method Overview

### `DiceBoard(chess.Board)`
Extends `python-chess.Board` with Dice Chess–specific logic.

| Method | Description |
|---------|--------------|
| `roll_dices()` | Rolls three dice and stores the resulting piece types available for the current player. |
| `get_moves()` | Returns the set of moves available based on the current dice roll (supports 1–3 dice remaining and only allows for moves that maximize the total number of moves in the turn). |
| `push(move, make_changes=False)` | Executes a move, handling dice consumption, en passant captures, and castling logic. If `make_changes` is `True` the dice roll and the en passant data will be modified. |
| `pseudo_legal_moves_dice` | Property returning all pseudo-legal moves plus custom en passant moves. |
| `is_check()` / `is_checkmate()` / `is_stalemate()` / `_attacked_for_king()` | Overridden to always return `False`, since Dice Chess ignores check and checkmate. |
| `san(move)` | Returns a SAN (Standard Algebraic Notation) string for a move, supporting Dice Chess’s custom en passant behavior. |
| `is_game_over(move)` | Returns `True` if the move captures a king. |
| `next_player()` | Clears temporary state (e.g., en passant squares) and switches to the next player. |

---

## ▶️ Usage

### Run from terminal

To play from the command line, simply run:

```bash
python DiceChess.py
```

The basic loop of the game is given by the following code:

```python
import chess
from DiceChess import DiceBoard, pieces_name_list

board: DiceBoard = DiceBoard() # Create board
while True:
    board.roll_dices() # Roll dices for current player

    print("Roll: ", [pieces_name_list[p-1] for p in board.dice_roll])
    move_list: List[chess.Move] = board.get_moves() # Get possible moves
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
        board.push(move_list[choice-1], make_changes = True) # Push move
        if is_game_over:
            print(board)
            print(("White" if board.turn == chess.WHITE else "Black") + " wins.")
            return
        move_list = board.get_moves()
        nMoves = len(move_list)

    print(board)
    print("Next player (current player out of moves)")
    board.next_player() # Change the player
```

---

## ⚖️ License

This project is licensed under the **GNU General Public License v3.0**.  
You are free to use, modify, and distribute this code provided that:

- Any derivative works remain under the GPL v3 license.  
- Proper attribution is given to the original author.  

You can find the full license text in the [`LICENSE`](./LICENSE) file or at  
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html).

---

## 🧩 Disclaimer

This project is an **independent, open-source implementation** of a dice-based chess variant inspired by publicly known gameplay concepts.  
It is **not affiliated with, endorsed by, or derived from** any proprietary code, design, or intellectual property belonging to  
[*dicechess.com*](https://www.dicechess.com) or its creators.  

All source code in this repository was written entirely from scratch using publicly available chess mechanics via the  
[`python-chess`](https://python-chess.readthedocs.io/) library.
