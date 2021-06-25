import logging
from pathlib import Path
from typing import Dict, List

from sutta_processor.application.check_service import CheckService
from sutta_processor.infrastructure.repository.repo import FileRepository
from sutta_processor.shared.config import Config

from .bilara_check_comment import bilara_check_comment_from_files
from .bilara_check_html import bilara_check_html_from_files
from .bilara_check_references import bilara_check_references_from_files
from .bilara_check_root import bilara_check_root_from_files
from .bilara_check_translation import bilara_check_translation_from_files
from .bilara_check_variant import bilara_check_variant_from_files
from .bilara_check_duplicated_indexes import bilara_check_duplicated_indexes_from_files

log = logging.getLogger(__name__)


# noinspection PyDataclass
def check_all_changes(cfg: Config, all_files: Dict[str, List[Path]]):
    """This wrapper function is used when running tests only on changed files that are part of a commit, rather than on
    all files (changed and unchanged) that are part of a commit."""
    cfg.repo: FileRepository
    cfg.check: CheckService

    # Only run tests if there are changed files.
    if all_files['comment']:
        bilara_check_comment_from_files(cfg=cfg, comment_file_paths=all_files['comment'],
                                        root_file_paths=all_files['root'])
    if all_files['html'] and all_files['root']:
        print('Running check_html on:')
        print(f"html files: {all_files['html']}")
        print(f"root files: {all_files['root']}")
        bilara_check_html_from_files(cfg=cfg, html_file_paths=all_files['html'], root_file_paths=all_files['root'])

    if all_files['reference']:
        bilara_check_references_from_files(cfg=cfg, ref_file_paths=all_files['reference'])

    if all_files['root']:
        print('Running check_root on:')
        print(f"root files: {all_files['root']}")
        bilara_check_root_from_files(cfg=cfg, root_file_paths=all_files['root'])

    if all_files['html'] and all_files['translation']:
        print('Running check_translation on:')
        print(f"html files: {all_files['html']}")
        print(f"translation files: {all_files['translation']}")
        bilara_check_translation_from_files(cfg=cfg, html_file_paths=all_files['html'],
                                            trans_file_paths=all_files['translation'])
    if all_files['variant'] and all_files['root']:
        print('Running check_variant on:')
        print(f"variant files: {all_files['variant']}")
        print(f"root files: {all_files['root']}")
        bilara_check_variant_from_files(cfg=cfg, root_file_paths=all_files['root'], var_file_paths=all_files['variant'])

    if all_files['reference']:
        bilara_check_duplicated_indexes_from_files(cfg=cfg, ref_file_paths=all_files['reference'])
