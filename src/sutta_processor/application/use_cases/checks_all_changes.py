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
    cfg.repo: FileRepository
    cfg.check: CheckService

    if all_files['comment']:
        bilara_check_comment_from_files(cfg=cfg, comment_file_paths=all_files['comment'],
                                        root_file_paths=all_files['root'])
    elif all_files['html']:
        bilara_check_html_from_files(cfg=cfg, html_file_paths=all_files['html'], root_file_paths=all_files['root'])
    elif all_files['reference']:
        bilara_check_references_from_files(cfg=cfg, ref_file_paths=all_files['reference'])
    elif all_files['root']:
        bilara_check_root_from_files(cfg=cfg, root_file_paths=all_files['root'])
    elif all_files['translation']:
        bilara_check_translation_from_files(cfg=cfg, html_file_paths=all_files['html'],
                                            trans_file_paths=all_files['translation'])
    elif all_files['variant']:
        bilara_check_variant_from_files(cfg=cfg, root_file_paths=all_files['root'], var_file_paths=all_files['variant'])
    elif all_files['reference']:
        bilara_check_duplicated_indexes_from_files(cfg=cfg, ref_file_paths=all_files['reference'])
