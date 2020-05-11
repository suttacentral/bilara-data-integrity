import logging
import sys

from sutta_processor.application import use_cases
from sutta_processor.shared.config import Config, Logging, configure_argparse

log = logging.getLogger(__name__)


def main():
    args = configure_argparse()
    Logging.setup()
    cfg = Config.from_yaml(f_pth=args.config)
    log.debug("cfg.debug_dir: %s", cfg.debug_dir)
    exec_module = getattr(use_cases, cfg.exec_module)
    exec_module(cfg=cfg)


def run():
    try:
        main()
    except Exception as e:
        log.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    run()
