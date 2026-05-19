"""
A script to run the provided agent against a set of puzzles, outputting
the puzzles it fails and the pass/fail rate.
"""
import argparse
import subprocess
import re
import json
import pathlib

def play_game(puzzle_path: pathlib.Path, agent:str) -> float:
    """
    Output to terminal the result of an agent playing a single chess puzzle.
    """
    try:
        with open(puzzle_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        print(f"Skipping {puzzle_path}: Unable to read file. {e}")
        return 0.0

    # Split the file: the header is JSON, the footer is the FEN
    try:
        # Getting the movelines
        header_part, fen_part = content.strip().split('---')
        clean_json = re.sub(r',\s*([\]}])', r'\1', header_part)
        puzzle_data = json.loads(clean_json)

        # separating the fen, starting board
        fen = fen_part.strip()
        move_lines = puzzle_data.get("move_lines")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Skipping {puzzle_path}: Failed to parse file format. {e}")
        return 0.0

    print(f"\n--- Solving Puzzle: {puzzle_path.name} ---")
    print(f"FEN: {fen}")

    # Construct the command
    command = [
        "python3", "-m", "chessai.puzzle",
        "--board", fen,
        "--move-lines", move_lines,
        "--agent", agent
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    score_match = re.search(r"Average Score:\s+([\d.]+)", result.stdout)
    score = float(score_match.group(1)) if score_match else 0.0

    if score == 0.0:
        print(f"Puzzle failed. Expected moves were: {move_lines}")

    return score

def play_all_games(folder: str, agent: str) -> None:
    """
    Iterate the agent through a list of chess puzzles
    """
    puzzle_folder = pathlib.Path(folder)

    if not puzzle_folder.is_dir():
        print(f"Error: {puzzle_folder} is not a directory.")
        return None

    # Iterate through all .puzzle files
    puzzle_files = list(puzzle_folder.glob("*.puzzle"))

    if not puzzle_files:
        print("No .puzzle files found in the directory.")
        return None

    count = 0.0
    score = 0.0

    # play each puzzle
    for puzzle_file in puzzle_files:

        score = play_game(puzzle_file, agent)
        count += 1
        score += score

    fails = count - score
    pass_rate = (score / count) * 100 if count > 0 else 0

    # Summary Output
    print("\n" + "="*40)
    print(f"FINAL SUMMARY - Agent: {agent}")
    print("-" * 40)
    print(f"Total Puzzles: {count}")
    print(f"Pass:          {score:.2f}")
    print(f"Fail:         {fails:.2f}")
    print(f"Pass Rate:     {pass_rate:.2f}%")

    return None

def main() -> None:
    """
    Entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="Run a specific agent against a set of chess puzzles."
    )

    parser.add_argument(
        "--folder", 
        required=True,
        help="Path to folder containing .puzzle files"
    )

    parser.add_argument(
        "--agent", 
        default="agent-random",
        help="Agent to play puzzles (default: agent-random)"
    )

    args = parser.parse_args()

    # Execution flow
    play_all_games(args.folder, args.agent)


if __name__ == "__main__":
    main()
