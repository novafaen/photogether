#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sort.py, sort files by date.

Sort files by:
 - File name timestamps (filename).
 - Create timestamps.
 - Modified timestamps.
"""

from logging import Formatter, Logger, getLogger, StreamHandler, DEBUG, INFO
from argparse import ArgumentParser, Namespace
from pathlib import Path
from sys import exit

import .database

log = getLogger(__name__)

def init_logging(level: int) -> Logger:
    """Initiate logging.

    :param int level: Level accoding to logging module.
    """
    global log

    log.setLevel(level)

    formatter: Formatter = Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

    if len(log.handlers) == 0:
        sh = StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(formatter)
        log.addHandler(sh)

def main() -> int:
    """Parse arguments and run appropriate command.

    :return: exit code.
    :rtype: int
    """
    parser: ArgumentParser = ArgumentParser(description='Sort files from one folder to another.')
    parser.add_argument('sort', type=str, help='Source folder (relative or full path)')
    parser.add_argument('to', type=str, help='Destination folder (relative or full path)')
    parser.add_argument('--dryrun', action='store_true', help='Perform a dry run without making changes')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args: Namespace = parser.parse_args()

    init_logging(DEBUG if args.debug else INFO)

    from_path: Path = Path(args.sort).resolve()
    to_path: Path = Path(args.to).resolve()

    log.debug('Debug enabled, enjoy additional information.')

    if args.dryrun:
        log.info('Dry run is enabled, no changes will be made.')

    if not from_path.exists() or not from_path.is_dir():
        log.error(f'Error: Source folder "{from_path}" does not exist or is not a directory.')
        return 100

    if not to_path.exists() or not to_path.is_dir():
        log.error(f'Error: Destination folder "{to_path}" does not exist or is not a directory.')
        return 101

    db_path: Path = to_path / 'sorted.db'

    log.info(f'Source folder: "{from_path}".')
    log.info(f'Destination folder: "{to_path}".')
    log.info(f'Using database: "{db_path}".')

    database.initialize_database()

    # execute here

    return 0

if __name__ == '__main__':
    exit(main())
