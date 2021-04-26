import logging
import sys

from sutta_processor.application import use_cases
from sutta_processor.shared.config import Config, Logging, configure_argparse

log = logging.getLogger(__name__)


def get_exit_status(cfg: Config):
    """Status is based on the length of report/error log."""
    with open(cfg.debug_dir / Logging.REPORT_LOG_FILENAME) as f:
        return len(f.read(10))


def main() -> int:
    args = configure_argparse()
    Logging.setup()
    cfg = Config.from_yaml(f_pth=args.config)
    log.debug("cfg.debug_dir: %s", cfg.debug_dir)
    exec_module = getattr(use_cases, cfg.exec_module)
    exec_module(cfg=cfg)
    return get_exit_status(cfg=cfg)


def run():
    try:
        sys.exit(main())
    except Exception as e:
        log.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    run()
