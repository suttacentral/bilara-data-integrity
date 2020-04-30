import logging
import sys

from sutta_processor.application.use_cases.checking_uid import checking_uid
from sutta_processor.shared.config import Config, configure_argparse, setup_logging

log = logging.getLogger(__name__)


def main():
    args = configure_argparse()
    setup_logging(debug_dir=args.debug_dir)
    cfg = Config.from_yaml(f_pth=args.config)
    log.debug("cfg.debug_dir: %s", cfg.debug_dir)
    checking_uid(cfg=cfg)


def run():
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    run()
