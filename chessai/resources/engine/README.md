# Stockfish Chess Game Analyzer (Docker)
A lightweight, containerized research tool that uses Stockfish and python-chess to provide move-by-move evaluations in a structured JSON format.

### Features
* Zero local dependencies: stockfish, python, etc. are all contained with the image.
* Stockfish is compiled from source during build
* Flexible analysis: supports FEN input, a move sequence, and adjustable search depth

### 1. Installation
Build the image using the provided 'Makefile'. This will take a couple of minutes.

`make build`

### 2. Usage
Run the container by passing a FEN string, an optional comma-separated list of moves, and an optional search depth, the default is 15.

`docker run --rm stockfish-analyzer "<FEN>" "<MOVES>" <DEPTH>`

#### Example:

`docker run --rm stockfish-analyzer "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" "e4, e5, Nf3" 18`

### 3. Understanding Ratings
The `rating` field provides the engine's evaluation of the position:
* Integers (Centipawns): A value of 100 is roughly equivalent to a 1-pawn advantage for White. Positive values favor White; negative values favor Black.
* Mate String (M#): When a forced checkmate is detected, the rating switches to a string format:
  * `M1`: White has a forced checkmate in 1 move.
  * `M-3`: Black has a forced checkmate in 3 moves (White is being mated)
  * `M0`: The current position is checkmate.

### 4. Output Format
The container returns a JSON object to stdout, which can be redirected to a file.

``` 
{
    "initial_fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    "config": { "depth": 15 },
    "initial_rating": 52,
    "analysis_steps": [
        { "move": "Bb5", "rating": 45 }
    ],
    "final_rating": 45
} 
```

#### Example: 

`docker run --rm chess-analyzer "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" "e4, e5, Nf3" 18 > results.json`

### 5. Testing
An initial test suite is provided to verify the Stockfish build, and output are all functioning correctly.  

#### Running the tests:
* 1. Ensure the image is built: `make build`
* 2. Execute the test: `make test`

#### What is being test:
* Verifies the container can process a standard FEN and return numerical centipawn evaluations.
* Ensures the engine correctly identifies forced mates and returns the M# string format.
* confirms that illegal moves or malformed FENs are caught and reported as an error field in the JSON rather than crashing.

### 6. Details
* Base Image: Alpine Linux (Python 3.12 variant)
* Engine: Stockfish (compiled from GitHub)
* Interface: UCI (Universal Chess Interface)
* Default Depth: 15 (if no depth is provided)