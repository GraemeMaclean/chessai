import dataclasses
import json
import os
import typing

import chessai.core.action
import chessai.core.parser

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
PUZZLES_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'puzzles')

PUZZLE_FILE_EXTENSION = '.json'

MOVE_LINES_KEY: str = 'move_lines'

@dataclasses.dataclass
class PuzzleInfo:
    """ A simple dataclass to unpack puzzle data from JSON. """

    fen: str
    """ The starting FEN for the puzzle. """

    move_lines: list[list[chessai.core.action.Action]]
    """ The expected move lines to solve the puzzle. """

def parse_puzzle_from_string(text: str, **kwargs: typing.Any) -> chessai.core.parser.ParsedGameState:
    """ Load a puzzle from a string, which is expected to be JSON data. """

    # Extract the JSON data into the puzzle info.
    data_dict = json.loads(text)
    puzzle_info = PuzzleInfo(**data_dict)

    # Use the default fen parsing.
    parsed_gamestate = chessai.core.parser.load_fen_from_string(text = puzzle_info.fen, **kwargs)

    print(f"Parser found: {type(puzzle_info.move_lines)} {puzzle_info.move_lines}")

    # Add the move line information.
    parsed_gamestate.options[MOVE_LINES_KEY] = puzzle_info.move_lines

    return parsed_gamestate

def parse_puzzle(data: str,
                 default_dir: str = PUZZLES_DIR,
                 default_extension: str = PUZZLE_FILE_EXTENSION,
                 string_parser: chessai.core.parser.GameStateStringParser = parse_puzzle_from_string,
                 accepts_raw_string: bool = False,
                 options: dict[str, typing.Any] | None = None,
                 **kwargs: typing.Any) -> chessai.core.parser.ParsedGameState:
    """
    Parse a Puzzle GameState from a file path.

    If the filepath does not exist, the default directory and file extension are added.
    """

    return chessai.core.parser.load_from_path(data,
                                              default_dir = default_dir,
                                              default_extension = default_extension,
                                              string_parser = string_parser,
                                              **kwargs)
