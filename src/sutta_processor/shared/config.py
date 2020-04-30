import argparse
import logging
from pathlib import Path
from typing import Union

import attr
from ruamel import yaml

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
SRC_ROOT = HERE.parent

FILE_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
STREAM_LOG_FORMAT = "[%(asctime)s]: %(message)s"
NULL_PTH = Path("/dev/null")


def create_dir(pth: Union[str, Path]) -> Path:
    if not pth or pth == NULL_PTH:
        return NULL_PTH
    pth = Path(pth).expanduser().resolve()
    pth.mkdir(exist_ok=True, parents=True)
    return pth


def touch_file(pth: Union[str, Path]) -> Path:
    pth = Path(pth)
    pth.parent.mkdir(exist_ok=True, parents=True)
    pth.touch()
    if not pth.is_file() and not pth.is_char_device():  # is_char_device for /dev/null
        raise RuntimeError(f"Path should be a file: '{pth}'")
    return pth


@attr.s(frozen=True, auto_attribs=True)
class Config:

    root_pli_ms_path: Path = attr.ib(converter=create_dir)

    debug_dir: Path = attr.ib(converter=create_dir, default=NULL_PTH)

    @classmethod
    def from_yaml(cls, f_pth: Union[str, Path] = None) -> "Config":
        """
        Keys in the yaml file will override corresponding settings if found.
        """
        kwargs = cls._get_yaml_kwargs(f_pth=f_pth)
        return cls(**kwargs)

    @classmethod
    def _get_yaml_kwargs(cls, f_pth: Union[str, Path] = None) -> dict:
        log.info("Loading config: '%s'", f_pth)
        with open(f_pth) as f:
            file_setts = yaml.safe_load(stream=f) or {}
        setup_logging(debug_dir=file_setts.get("debug_dir"))

        setts_names = [field.name for field in attr.fields(cls)]
        log.debug("Loaded setts from file: %s, values: %s", f_pth, file_setts)
        kwargs = {k: v for k, v in file_setts.items() if k in setts_names}
        return kwargs


def setup_logging(debug_dir, debug_filename="app.log"):
    # Reset logging
    logging.getLogger("").handlers = []

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter(fmt=STREAM_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    )
    log_level = logging.DEBUG if debug_dir else logging.INFO
    stream_handler.setLevel(log_level)
    log_handlers = [stream_handler]
    if debug_dir:
        debug_dir = Path(debug_dir).expanduser().resolve()
        debug_dir.mkdir(exist_ok=True, parents=True)
        filepath = debug_dir / debug_filename
        file_log_handler = logging.FileHandler(filepath)
        file_log_handler.setFormatter(logging.Formatter(fmt=FILE_LOG_FORMAT))
        file_log_handler.setLevel(log_level)
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
        "-c",
        "--config",
        help="Path to config file",
        metavar="CONFIG_PATH",
        required=True,
        type=str,
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
