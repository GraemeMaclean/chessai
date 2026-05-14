"""
A script to extract a specific number of puzzles of a certain theme from the 
Lichess database. Outputs individual .board files for each match.
"""
import argparse
import csv
import json
import os
from typing import List

def generate_puzzle_files(
    input_csv: str,
    output_folder: str,
    target_theme: str,
    limit: int
) -> None:
    """
    Filters Lichess CSV for a specific theme and outputs a set number of files.

    Args:
        input_csv: Path to the source Lichess CSV file.
        output_folder: Path to the target output directory.
        target_theme: The theme string to search for (e.g., 'mateIn2').
        limit: The maximum number of puzzles to generate.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    count = 0

    try:
        with open(input_csv, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                if count >= limit:
                    break

                # Lichess themes are space-separated in the 'Themes' column
                themes = str(row.get('Themes', '')).split()

                if target_theme in themes:
                    puzzle_id = str(row.get('PuzzleId', ''))
                    fen = str(row.get('FEN', ''))
                    raw_moves = str(row.get('Moves', ''))

                    if not puzzle_id or not fen:
                        continue

                    moves_list: List[str] = raw_moves.split()

                    puzzle_data = {
                        "class": "chessai.puzzle.board.Board",
                        "move_lines": json.dumps([moves_list])
                    }

                    file_path = os.path.join(output_folder, f"{puzzle_id}.board")

                    with open(file_path, 'w', encoding='utf-8') as out_file:
                        json.dump(puzzle_data, out_file, indent=4)
                        out_file.write(f"\n---\n{fen}")

                    count += 1

        print(f"Successfully generated {count} puzzles for theme '{target_theme}'.")

    except FileNotFoundError:
        print(f"Error: The file {input_csv} was not found.")
    except PermissionError:
        print(f"Error: Permission denied accessing {input_csv} or {output_folder}.")

def main() -> None:
    """
    Handles command line argument parsing and script execution.
    """
    parser = argparse.ArgumentParser(
        description="Extract specific themes from Lichess puzzle CSV."
    )
    parser.add_argument("input", help="Path to the Lichess CSV file")
    parser.add_argument("output", help="Directory to save .board files")
    parser.add_argument("theme", help="Puzzle theme to filter by (e.g. 'fork')")
    parser.add_argument(
        "count", 
        type=int,
        help="Number of puzzles to extract"
    )

    args = parser.parse_args()

    generate_puzzle_files(args.input, args.output, args.theme, args.count)

if __name__ == "__main__":
    main()
