"""
The main executable for running a game of Knight's Errant.
"""

import argparse
import typing

import chessai.core.agentinfo
import chessai.core.board
import chessai.errant.game
import chessai.errant.gamestate
import chessai.util.bin
import chessai.util.alias

DEFAULT_BOARD: str = 'knights-errant-base'

def set_cli_args(parser: argparse.ArgumentParser, **kwargs: typing.Any) -> argparse.ArgumentParser:
    """
    Set Knight's-Errant-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--knight', dest = 'knight',
            action = 'store', type = str, default = chessai.util.alias.AGENT_RANDOM.short,
            help = ('Select the agent type that the Knight will use (default: %(default)s).'
                    + f' Builtin agents: {chessai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--target-square', dest = 'target_square',
            action = 'store', type = int, default = 0,
            help = ('The target square for the knight (default: %(default)s).'))

    # parser.add_argument('--start-square', dest = 'start_square',
    #         action = 'store', type = int, default = None,
    #         help = ('The starting square for the knight (default: %(default)s).'
    #                 + ' Overrides the board given by `--board` and places a single white knight at this position.'))

    return parser

# TODO(Lucas): Keep working on parsing the args and defining a game of knight's errant. Then, we can add tests.
def init_from_args(args: argparse.Namespace) -> tuple[dict[bool, chessai.core.agentinfo.AgentInfo], list[bool], dict[str, typing.Any]]:
    """
    Setup agents based on Knight's Errant rules.
    """

    base_agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo] = {
        bool(chessai.core.types.Color.WHITE): chessai.core.agentinfo.AgentInfo(name = args.knight),
        bool(chessai.core.types.Color.BLACK): chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_DUMMY.short),
    }

    search_target = chessai.core.square.Square(args.target_square)

    board_kwargs: dict[str, typing.Any] = {
        'search_target': search_target.to_dict(),
    }

    # If a start square was provided, override the board's knight position.
    # if args.start_square is not None:
    #     start_square = chessai.core.square.Square(args.start_square)
    #     board_kwargs['_start_square'] = start_square.to_dict()

    return base_agent_infos, [], board_kwargs

# TODO(Lucas): Figure out how to use this to parse the above info.
# def _get_fen_from_knight_position(
#         square: chessai.core.square.Square,
#         row_size: int = chessai.core.types.DEFAULT_BOARD_SIZE
#     ) -> str:
#     """
#     Returns a FEN board string placing a single white knight at the given square.

#     The FEN covers only the piece placement portion (8 ranks, '/' separated).
#     Ranks are ordered from rank 8 (top) down to rank 1 (bottom), as per FEN spec.
#     """

#     rank = square.rank
#     file = square.file

#     ranks = []
#     for r in range(row_size - 1, -1, -1):
#         if r != rank:
#             ranks.append(str(row_size))
#         else:
#             parts = []
#             if file > 0:
#                 parts.append(str(file))

#             parts.append('N')

#             if file < row_size - 1:
#                 parts.append(str(row_size - file - 1))

#             ranks.append(''.join(parts))

#     return '/'.join(ranks)

def main(argv: list[str] | None = None,
         ) -> list[chessai.core.game.GameResult]:
    """
    Invoke a game of Knight's Errant.

    Will return the results of any training games followed by the results of any non-training games.
    """

    return chessai.util.bin.run_main(
        description = "Play a game of Knight's Errant.",
        default_board = DEFAULT_BOARD,
        game_class = chessai.errant.game.Game,
        custom_set_cli_args = set_cli_args,
        custom_init_from_args = init_from_args,
        # TODO(Lucas): Does white always win?
        winning_agent_indexes = {bool(chessai.core.types.Color.WHITE)},
        argv = argv,
    )

if (__name__ == '__main__'):
    main()
