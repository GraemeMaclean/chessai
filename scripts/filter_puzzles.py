#!/usr/bin/env python3
"""
A script to extract a specific number of puzzles of a certain theme from the Lichess database. 
Outputs individual .board files for each match.
"""

import argparse
import csv
import os
import sys
import typing

import edq.util.dirent
import edq.util.json

DEFAULT_COUNT: typing.Optional[int] = None
DEFAULT_THEME: str = 'mateIn1'
DEFAULT_OUTPUT_DIR: str = os.path.join('chessai', 'resources', 'puzzles')

def generate_puzzle_files(
        input_csv: str,
        output_folder: str = DEFAULT_OUTPUT_DIR,
        target_theme: str = DEFAULT_THEME,
        limit: typing.Optional[int] = DEFAULT_COUNT
        ) -> None:
    """ Filters Lichess CSV for a specific theme and outputs a set number of files. """

    edq.util.dirent.mkdir(output_folder)

    count = 0
    limit_reached = False
    with open(input_csv, mode = 'r', encoding = 'utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            if (limit is not None and count >= limit):
                limit_reached = True
                break

            # Lichess themes are space-separated in the 'Themes' column.
            themes = str(row.get('Themes', '')).split()

            if (target_theme in themes):
                puzzle_id = str(row.get('PuzzleId', ''))
                fen = str(row.get('FEN', ''))
                raw_moves = str(row.get('Moves', ''))

                if (not puzzle_id or not fen):
                    continue

                moves_list: typing.List[str] = raw_moves.split()

                puzzle_data = {
                    "class": "chessai.puzzle.board.Board",
                    "move_lines": edq.util.json.dumps([moves_list])
                }

                puzzle_path = os.path.join(output_folder, f"{puzzle_id}.puzzle")

                with open(puzzle_path, 'w', encoding='utf-8') as out_file:
                    edq.util.json.dump(puzzle_data, out_file, indent=4)
                    out_file.write(f"\n---\n{fen}")

                count += 1

    if (limit_reached):
        print(f"Reached requested limit of {limit} puzzles for theme '{target_theme}'. Stopping search.")
    elif (limit is not None):
        print(f"Ran out of puzzles, only found {count} puzzles out of the requested {limit} for theme '{target_theme}'.")
    else:
        print(f"Successfully processed entire file. Generated {count} total puzzles for theme '{target_theme}'.")

def main(args) -> int:
    """ Handles command line argument parsing and script execution. """

    generate_puzzle_files(args.input, args.output, args.theme, args.limit)

    return 0

def _load_args():
    parser = argparse.ArgumentParser(
            description = 'Extract specific themes from Lichess puzzle CSV.')

    parser.add_argument('input', metavar = 'INPUT_CSV', type = str,
            help = 'Path to the Lichess CSV file.')

    parser.add_argument('--output', dest = 'output',
            action = 'store', type = str, default = DEFAULT_OUTPUT_DIR,
            help = 'Directory to save .board files (default: %(default)s).')

    parser.add_argument('--theme', dest = 'theme',
            action = 'store', type = str, default = DEFAULT_THEME,
            help = "Puzzle theme to filter by (default: %(default)s)," \
            "refer to https://github.com/lichess-org/lila/blob/master/modules/puzzle/src/main/PuzzleTheme.scala for puzzle themes.")

    parser.add_argument('--limit', dest = 'limit',
            action = 'store', type = int, default = DEFAULT_COUNT,
            help = 'Limit the number of puzzles to extract (default: %(default)s).')

    return parser.parse_args()

if (__name__ == "__main__"):
    sys.exit(main(_load_args()))
