import argparse
import sys
import logging

from sutta_processor import __version__

from sutta_processor.shared.config import parse_args, setup_logging

log = logging.getLogger(__name__)


def main():
    # args = parse_args()
    # setup_logging()
    print('asd')


def run():
    try:
        main()
    except Exception as e:
        log.exception(e)
        raise


if __name__ == "__main__":
    run()
