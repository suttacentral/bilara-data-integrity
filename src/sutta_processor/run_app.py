import logging

from sutta_processor.shared.config import configure_argparse, setup_logging

log = logging.getLogger(__name__)


def main():
    args = configure_argparse()
    setup_logging(debug_dir=args.debug_dir)
    log.info("test")


def run():
    try:
        main()
    except Exception as e:
        log.exception(e)
        raise


if __name__ == "__main__":
    run()
