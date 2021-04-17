import logging
import sys
from pathlib import Path
from typing import Dict, List

from sutta_processor.application import use_cases
from sutta_processor.shared.config import Config, Logging, configure_argparse

log = logging.getLogger(__name__)


def get_exit_status(cfg: Config):
    """Status is based on the length of report/error log."""
    with open(cfg.debug_dir / Logging.REPORT_LOG_FILENAME) as f:
        return len(f.read(10))

def _sort_files(file_paths: List[Path]) -> Dict[str, List[Path]]:
    sorted_files: Dict[str: List[Path]] = {}
    comment_files = []
    html_files = []
    ref_files = []
    root_files = []
    trans_files = []
    var_files = []
    for file in file_paths:
        if file.parts[0] == 'comment':
            comment_files.append(file)
        elif file.parts[0] == 'html':
            html_files.append(file)
        elif file.parts[0] == 'reference':
            ref_files.append(file)
        elif file.parts[0] == 'root':
            root_files.append(file)
        elif file.parts[0] == 'translation':
            trans_files.append(file)
        else:
            var_files.append(file)

    sorted_files['comment'] = comment_files
    sorted_files['html'] = html_files
    sorted_files['reference'] = ref_files
    sorted_files['root'] = root_files
    sorted_files['translation'] = trans_files
    sorted_files['variant'] = var_files

    return sorted_files

def main() -> int:
    args = configure_argparse()
    Logging.setup()
    cfg = Config.from_yaml(f_pth=args.config)
    all_files = _sort_files(file_paths=args.files)
    log.debug("cfg.debug_dir: %s", cfg.debug_dir)
    exec_module = getattr(use_cases, cfg.exec_module)
    exec_module(cfg=cfg, all_files=all_files)
    return get_exit_status(cfg=cfg)


def run():
    try:
        sys.exit(main())
    except Exception as e:
        log.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    run()
