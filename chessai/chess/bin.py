"""
The main executable for running a game of Chess.
"""

import argparse
import logging
import typing

import chessai.chess.game
import chessai.util.alias
import chessai.util.bin

def set_cli_args(parser: argparse.ArgumentParser, **kwargs: typing.Any) -> argparse.ArgumentParser:
    """
    Set Chess-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--white-team', dest = 'white_team', metavar = 'TEAM_CREATION_FUNC',
            action = 'store', type = str, default = chessai.util.alias.AGENT_RANDOM.short,
            help = ('Select the chess team that will play on the white team (default: %(default)s).'
                    + f' Builtin teams: {chessai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--black-team', dest = 'black_team', metavar = 'TEAM_CREATION_FUNC',
            action = 'store', type = str, default = chessai.util.alias.AGENT_RANDOM.short,
            help = ('Select the chess team that will play on the black team (default: %(default)s).'
                    + f' Builtin teams: {chessai.util.alias.AGENT_SHORT_NAMES}.'))

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[bool, chessai.core.agentinfo.AgentInfo], list[bool], dict[str, typing.Any]]:
    """
    Setup agents based on Chess rules.

    Agent infos are supplied via the --white-team and --black-team arguments.
    Missing agents will be filled in with random agents.
    """

    base_agent_infos: dict[bool, chessai.core.agentinfo.AgentInfo] = {
        bool(chessai.core.types.Color.WHITE): chessai.core.agentinfo.AgentInfo(name = args.white_team),
        bool(chessai.core.types.Color.BLACK): chessai.core.agentinfo.AgentInfo(name = args.black_team),
    }

    # TODO(Lucas): Expand the board offerings.
    # Check for random boards.
    # args.board = chessai.chess.game.Game.check_for_random_board(args.board)

    return base_agent_infos, [], {}

def log_chess_results(results: list[chessai.core.game.GameResult], winning_agent_indexes: set[bool], prefix: str = '') -> None:
    """
    Log the result of running several games.
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
    Invoke a game of chess.

    Will return the results of the games.
    """

    return chessai.util.bin.run_main(
        description = "Play a game of chess.",
        game_class = chessai.chess.game.Game,
        default_board = None,
        custom_set_cli_args = set_cli_args,
        custom_init_from_args = init_from_args,
        log_results = log_chess_results,
        argv = argv,
    )

if (__name__ == '__main__'):
    main()
