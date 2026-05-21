"""
A script to run the provided agent against a set of puzzles, outputting
the puzzles it fails and the pass/fail rate.
"""

import argparse
import glob
import os
import sys

import chessai.puzzle.bin

def play_puzzle(puzzle_path: str, agent: str, agent_args: str) -> float:
    """ Output to terminal the result of an agent playing a single chess puzzle. """

    print(f"\n--- Solving Puzzle: {puzzle_path} ---")
    print(puzzle_path, agent, agent_args)

    argv = [
        "--board", puzzle_path,
        "--agent", agent
    ]

    if (agent_args):
        for arg in agent_args:
            argv.extend(["--agent-arg", arg])

    print(argv)

    try:
        results = chessai.puzzle.bin.main(argv = argv)
    except ValueError as e:
        print(f"Skipping puzzle due to an illegal move: {e}", file=sys.stderr)
        return 0.0

    return results[0].score

def play_all_puzzles(folder: str, agent: str, agent_arg: str) -> None:
    """ Iterate the agent through a folder with chess puzzles. """

    if (not os.path.isdir(folder)):
        print(f"Error: {folder} is not a directory.")
        return None

    # Find all .puzzle files.
    search_pattern = os.path.join(folder, "*.puzzle")
    puzzle_files = glob.glob(search_pattern)

    if (not puzzle_files):
        print("No .puzzle files found in the directory.")
        return None

    puzzle_count = 0.0
    total_score = 0.0

    # Iterate through each puzzle.
    for puzzle_file in puzzle_files:

        puzzle_score = play_puzzle(puzzle_file, agent, agent_arg)
        puzzle_count += 1
        total_score += puzzle_score

    fails = puzzle_count - total_score
    pass_rate = (total_score / puzzle_count) * 100

    # Summary Output
    print("\n" + "="*40)
    print(f"FINAL SUMMARY - Agent: {agent}")
    print("-" * 40)
    print(f"Total Puzzles: {puzzle_count}")
    print(f"Pass:          {total_score:.2f}")
    print(f"Fail:         {fails:.2f}")
    print(f"Pass Rate:     {pass_rate:.2f}%")

    return None

def main() -> None:
    """ Handles command line argument parsing and script execution. """

    parser = argparse.ArgumentParser(
            description = "Run a specific agent against a set of chess puzzles.")

    parser.add_argument('--folder', dest = 'folder',
            action = 'store', type = str, default = 'chessai/resources/puzzles',
            help = ('Path to folder containing .puzzle files (default: %(default)s).'
                    + ' If just a filename, than the `chessai/resources/puzzles` directory will be checked'
                    + ' (using a ".puzzle" extension).'))

    parser.add_argument('--agent', dest = 'agent',
            action = 'store', type = str, default = 'agent-random',
            help = 'Agent to play puzzles (default: %(default)s).')

    parser.add_argument('--agent-arg', dest = 'agent_arg',
            action = 'append', type = str, default = None,
            help = 'Specify arguments directly to agents (may be used multiple times).')

    args = parser.parse_args()

    play_all_puzzles(args.folder, args.agent, args.agent_arg)

if __name__ == "__main__":
    main()
