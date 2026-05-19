"""
Entrypoint script for a docker container utilizing the stockfish engine
to rate a board and moveline for the board
"""

import sys
import json

# python-chess is imported into the docker container image
# pylint: disable=import-error
import chess.engine     # type: ignore

def get_rating_value(engine, board, depth_limit):
    """Fetches evaluation and returns a simplified string or integer."""
    info = engine.analyse(board, chess.engine.Limit(depth=depth_limit))
    score = info["score"].white()

    if score.is_mate():
        return f"M{score.mate()}"
    return score.score()

def main():
    """Take an input board and moveline and return the rating for each stage."""
    # Check if at least FEN is provided
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: docker run <image> <FEN> [MOVES] [DEPTH]"}))
        return

    fen = sys.argv[1]
    moves_raw = sys.argv[2] if len(sys.argv) > 2 else ""

    # DEFAULT LIMIT: If 3rd argument is missing, use depth 15
    try:
        depth_limit = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    except ValueError:
        print(json.dumps({"error": "Depth must be an integer"}))
        return

    output = {
        "initial_fen": fen,
        "config": {"depth": depth_limit},
        "analysis_steps": []
    }

    board = chess.Board(fen)
    engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")

    try:
        # Initial Rating
        output["initial_rating"] = get_rating_value(engine, board, depth_limit)

        # Process Moves
        if moves_raw:
            move_list = [m.strip() for m in moves_raw.split(",") if m.strip()]

            for move_san in move_list:
                try:
                    move = board.parse_san(move_san)
                    board.push(move)

                    output["analysis_steps"].append({
                        "move": move_san,
                        "rating": get_rating_value(engine, board, depth_limit)
                    })
                except ValueError:
                    output["analysis_steps"].append({"move": move_san, "error": "Invalid move"})
                    break

            # Final Rating
            output["final_rating"] = get_rating_value(engine, board, depth_limit)
        else:
            # no moves provided, so initial and final rating is equal
            output["final_rating"] = output["initial_rating"]

    except (chess.engine.EngineError, chess.engine.EngineTerminatedError) as e:
        output["error"] = str(e)
    finally:
        engine.quit()

    # Final JSON output to stdout
    print(json.dumps(output, indent=4))

if __name__ == "__main__":
    main()
