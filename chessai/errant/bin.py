"""
The main executable for running a game of tour.
"""

import argparse
import logging
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
    Set tour-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--white', dest = 'white',
            action = 'store', type = str, default = chessai.util.alias.AGENT_RANDOM.short,
            help = ('Select the agent type that the white agent will use (default: %(default)s).'
                    + f' Builtin agents: {chessai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--target-squares', dest = 'target_squares',
            action = 'store', type = str, default = None,
            help = ('The target squares for the search problem (default: %(default)s).'
                    + ' Separate multiple targets with commas (e.g., \'0,42,63\').'))

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[bool, chessai.core.agentinfo.AgentInfo], list[bool], dict[str, typing.Any]]:
    """
    Setup agents based on Knight's Errant rules.
    """

    base_agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo] = {
        bool(chessai.core.types.Color.WHITE): chessai.core.agentinfo.AgentInfo(name = args.white),
        bool(chessai.core.types.Color.BLACK): chessai.core.agentinfo.AgentInfo(name = chessai.util.alias.AGENT_DUMMY.short),
    }

    board_kwargs: dict[str, typing.Any] = {}

    if (args.target_squares is not None):
        board_kwargs[chessai.core.square.SQUARES_KEY] = args.target_squares

    return base_agent_infos, [], board_kwargs

def log_tour_results(results: list[chessai.core.game.GameResult], winning_agent_indexes: set[bool], prefix: str = '') -> None:
    """
    Log the result of running several tour games.
    """

    move_counts: list[int] = [len(result.history) for result in results]

    record: list[str] = []
    scores: list[float] = []
    for result in results:
        if ((result.outcome is None) or (result.outcome.winner is None)):
            record.append('Tie')
            scores.append(0.5)
        elif (result.outcome.winner == chessai.core.types.Color.WHITE):
            record.append('Win')
            scores.append(1)
        else:
            record.append('Loss')
            scores.append(0)

    average_score: float = (sum(scores)) / len(scores)
    logging.info('Average Score: %0.2f', average_score)

    # Avoid logging long lists (which can be a bit slow in Python's logging module).
    log_lists_to_info: bool = (len(results) < chessai.util.bin.SCORE_LIST_MAX_INFO_LENGTH)
    log_lists_to_debug: bool = (logging.getLogger().getEffectiveLevel() <= logging.DEBUG)

    joined_scores: str = ''
    joined_record: str = ''
    joined_move_counts: str = ''

    if (log_lists_to_info or log_lists_to_debug):
        joined_scores = ', '.join([str(score) for score in scores])
        joined_record = ', '.join(record)
        joined_move_counts = ', '.join([str(move_count) for move_count in move_counts])

    if (log_lists_to_info):
        logging.info('%sScores:        %s', prefix, joined_scores)
    elif (log_lists_to_debug):
        logging.debug('%sScores:        %s', prefix, joined_scores)

    if (log_lists_to_info):
        logging.info('%sRecord:        %s', prefix, joined_record)
    elif (log_lists_to_debug):
        logging.debug('%sRecord:        %s', prefix, joined_record)

    logging.info('%sAverage Moves: %s', prefix, sum(move_counts) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sMove Counts:   %s', prefix, joined_move_counts)
    elif (log_lists_to_debug):
        logging.debug('%sMove Counts:   %s', prefix, joined_move_counts)

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
        log_results = log_tour_results,
        argv = argv,
    )

if (__name__ == '__main__'):
    main()
