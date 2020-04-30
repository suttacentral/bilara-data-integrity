import argparse
import logging
from pathlib import Path

log = logging.getLogger(__name__)

FILE_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
STREAM_LOG_FORMAT = "[%(asctime)s]: %(message)s"


def setup_logging(debug_dir, debug_filename="app.log"):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(fmt=STREAM_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    )
    stream_handler.setLevel(logging.INFO)
    log_handlers = [stream_handler]
    if debug_dir:
        debug_dir = Path(debug_dir).resolve().expanduser()
        debug_dir.mkdir(exist_ok=True, parents=True)
        filepath = debug_dir / debug_filename
        file_log_handler = logging.FileHandler(filepath)
        file_log_handler.setFormatter(logging.Formatter(fmt=FILE_LOG_FORMAT))
        file_log_handler.setLevel(logging.DEBUG)
        log_handlers.append(file_log_handler)
    # noinspection PyArgumentList
    logging.basicConfig(
        level=logging.DEBUG, handlers=log_handlers,
    )


def configure_argparse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tool to help with suttas texts", add_help=False
    )
    parser.add_argument(
        "-c", "--config", help="Path to config file", metavar="CONFIG_PATH", type=str
    )
    parser.add_argument(
        "--debug_dir",
        default="",
        help="Path for debug assets, logs and files.",
        metavar="PATH",
        type=str,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Print this help text and exit",
    )

    return parser.parse_args()
