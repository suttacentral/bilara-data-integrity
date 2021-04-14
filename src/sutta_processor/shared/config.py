import argparse
import logging
from logging.config import dictConfig
from os.path import expandvars
from pathlib import Path
from typing import List, Union

import attr
from ruamel import yaml

log = logging.getLogger(__name__)

HERE = Path(__file__).parent
SRC_ROOT = HERE.parent


NULL_PTH = Path("/dev/null")


def create_dir(pth: Union[str, Path]) -> Path:
    if not pth or pth == NULL_PTH:
        return NULL_PTH
    pth = Path(expandvars(pth)).expanduser().resolve()
    pth.mkdir(exist_ok=True, parents=True)
    return pth


def touch_file(pth: Union[str, Path]) -> Path:
    pth = Path(expandvars(pth))
    pth.parent.mkdir(exist_ok=True, parents=True)
    pth.touch()
    if not pth.is_file() and not pth.is_char_device():  # is_char_device for /dev/null
        raise RuntimeError(f"Path should be a file: '{pth}'")
    return pth


def use_case_present(_inst, _attr, uc_name: str):
    from sutta_processor.application import use_cases

    if not getattr(use_cases, uc_name, None):
        choices = use_cases.__all__
        raise NameError(
            f"Module {uc_name} was not found, choices: {choices}. "
            "Check `exec_module` config key."
        )


@attr.s(frozen=True, auto_attribs=True)
class ExcludeRepo:
    headers_without_0: set = attr.ib(default=set())
    get_comment_surplus_segments: set = attr.ib(default=set())
    get_missing_segments: set = attr.ib(default=set())
    get_unordered_segments: set = attr.ib(default=set())
    check_uid_sequence_in_file: set = attr.ib(default=set())
    get_unknown_variants: set = attr.ib(default=set())
    get_wrong_uid_with_arrow: set = attr.ib(default=set())
    get_duplicated_verses_next_to_each_other: set = attr.ib(default=set())

    @classmethod
    def from_dict(cls, data: dict) -> "ExcludeRepo":
        fields = [field.name for field in attr.fields(cls)]
        kwargs = {k: set(v) for k, v in data.items() if k in fields}
        return cls(**kwargs)

    @classmethod
    def from_yaml(cls, f_pth: Union[str, Path] = None) -> "ExcludeRepo":
        """
        Structure of yaml file:
        ```
        headers_without_0:
          - dhp416:5
          - pli-tv-bi-pm:107.2
          ...
          - pli-tv-bi-pm:158.4
        ```
        """
        with open(expandvars(f_pth)) as f:
            data = yaml.safe_load(stream=f) or {}
        return cls.from_dict(data=data)


@attr.s(frozen=True, auto_attribs=True)
class Config:
    # Not setting default so that exclude_dirs must be included
    exclude_dirs: List[str] = attr.ib()
    # Not setting default so that exclude_filepath must be included.  We need this to remove false positives.
    exclude_filepath: Path = attr.ib()
    # A list of folder names, where each folder has files in a certain language
    bilara_root_langs: List[str] = attr.ib()

    exec_module: str = attr.ib(validator=use_case_present)

    bilara_root_path: Path = attr.ib(converter=create_dir)
    pali_canon_path: Path = attr.ib(converter=create_dir)
    ms_yuttadhammo_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    bilara_html_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    bilara_comment_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    bilara_variant_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    bilara_translation_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    pali_concordance_filepath: Path = attr.ib(default=NULL_PTH)
    reference_root_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    migration_differences_path: Path = attr.ib(converter=create_dir, default=NULL_PTH)

    debug_dir: Path = attr.ib(converter=create_dir, default=NULL_PTH)
    log_level: int = attr.ib(default=logging.INFO)

    repo: "FileRepository" = attr.ib(init=False)
    check: "CheckService" = attr.ib(init=False)
    exclude: ExcludeRepo = attr.ib(init=False)

    def __attrs_post_init__(self):
        from sutta_processor.infrastructure.repository.repo import FileRepository

        from sutta_processor.application.check_service import CheckService

        object.__setattr__(self, "check", CheckService(cfg=self))
        object.__setattr__(self, "repo", FileRepository(cfg=self))
        object.__setattr__(
            self, "exclude", ExcludeRepo.from_yaml(f_pth=self.exclude_filepath)
        )

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
        with open(expandvars(f_pth)) as f:
            file_setts = yaml.safe_load(stream=f) or {}
        Logging.setup(
            debug_dir=file_setts.get("debug_dir"),
            log_level=file_setts.get("log_level"),
        )

        setts_names = [field.name for field in attr.fields(cls)]
        log.debug("Loaded setts from file: %s, values: %s", f_pth, file_setts)
        kwargs = {k: v for k, v in file_setts.items() if k in setts_names}
        return kwargs


class Logging:
    APP_LOG_FILENAME = "app.log"
    REPORT_LOG_FILENAME = "report.log"

    FORMATTERS = {
        "verbose": {
            "format": (
                "%(asctime)s [%(levelname)7s] %(funcName)20s:%(lineno)d: %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(message)s",},
    }

    @classmethod
    def setup(cls, debug_dir: str = "", log_level=None):
        """
        WARNING: Information about the discrepancy in the data, should be fixed when
                 errors are corrected.
        ERROR: Error found in the processed data. Should give some ids to check and fix.
        """
        log_level = log_level or logging.INFO
        cls.add_trace_level()
        handlers = {
            **cls.get_console_conf(log_level=log_level),
            **cls.get_file_handlers(debug_dir=debug_dir, log_level=log_level),
        }

        root_handler = ["console", "file", "file_report"] if debug_dir else ["console"]

        log_conf = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": cls.FORMATTERS,
            "handlers": handlers,
            "loggers": {
                "": {
                    "level": logging._levelToName.get(log_level, "INFO"),
                    "handlers": root_handler,
                },
                "root": {
                    "level": logging._levelToName.get(log_level, "INFO"),
                    "handlers": root_handler,
                },
            },
        }
        dictConfig(log_conf)

    @classmethod
    def get_file_handlers(cls, debug_dir: str, log_level: int) -> dict:
        if not debug_dir:
            return {}

        debug_dir = Path(expandvars(debug_dir)).expanduser().resolve()
        debug_dir.mkdir(exist_ok=True, parents=True)
        handlers = {
            "file": {
                "class": "logging.FileHandler",
                "filename": str(debug_dir / cls.APP_LOG_FILENAME),
                "formatter": "verbose",
                "level": logging._levelToName.get(log_level, "TRACE"),
                "mode": "w",
            },
            "file_report": {
                "class": "logging.FileHandler",
                "filename": str(debug_dir / cls.REPORT_LOG_FILENAME),
                "formatter": "simple",
                "level": "ERROR",
                "mode": "w",
            },
        }
        return handlers

    @classmethod
    def get_console_conf(cls, log_level) -> dict:
        console = {
            "level": logging._levelToName.get(log_level, "DEBUG"),
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
        return {"console": console}

    @classmethod
    def add_trace_level(cls, trace_lvl=9):
        logging.addLevelName(trace_lvl, "TRACE")

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(trace_lvl):
                self._log(trace_lvl, message, args, **kws)

        logging.Logger.trace = trace


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
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Print this help text and exit",
    )

    return parser.parse_args()
