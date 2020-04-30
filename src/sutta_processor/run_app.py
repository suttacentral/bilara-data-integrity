import logging
import sys

from sutta_processor.shared.config import Config, configure_argparse, setup_logging

log = logging.getLogger(__name__)


def main():
    args = configure_argparse()
    setup_logging(debug_dir=args.debug_dir)
    cfg = Config.from_yaml(f_pth=args.config)
    log.info("test")
    log.info("cfg: %s, cfg.debugdir: %s", cfg, cfg.debug_dir)


def run():
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    run()
