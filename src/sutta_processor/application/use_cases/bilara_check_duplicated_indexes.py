import collections
import json
import logging
import ntpath
import os
from fnmatch import fnmatch

from sutta_processor.shared.config import Config

log = logging.getLogger(__name__)


def get_reference_paths(directory):
    reference_file_pattern = "*_reference.json"
    reference_files = []

    for path, _, files in os.walk(directory):
        for file in files:
            if fnmatch(file, reference_file_pattern):
                reference_files.append(os.path.join(path, file))

    return reference_files


def get_file_content(file_path):
    with open(file_path, "r") as file:
        file_content = json.load(file)

    return {reference: indexes.split(", ") for reference, indexes in file_content.items()}


def get_duplicated_indexes(file_content):
    all_indexes = []

    for indexes in file_content.values():
        all_indexes += indexes

    return [index for index, count in collections.Counter(all_indexes).items() if count > 1]


def remove_duplicated_index(file_content, duplicated_index):
    """ Removing the first apperance of duplicated index """
    for reference, indexes in file_content.items():
        if duplicated_index in indexes:
            indexes.remove(duplicated_index)
            if not indexes: del file_content[reference]
            break


def save_file_content(file_path, file_content):
    file_content = {reference: ", ".join(indexes) for reference, indexes in file_content.items()}

    with open(file_path, "w") as file:
        json.dump(file_content, file, indent=2)


def bilara_check_duplicated_indexes(cfg: Config):
    reference_paths = get_reference_paths(directory=cfg.reference_root_path)

    for reference_path in reference_paths:
        file_content = get_file_content(reference_path)
        duplicated_indexes = get_duplicated_indexes(file_content)

        for duplicated_index in duplicated_indexes:
            log.error(f"Found duplicated index {duplicated_index} in the {reference_path}")
            # Uncomment to remove duplicated indexes from files.
            # remove_duplicated_index(file_content, duplicated_index)
            # save_file_content(reference_path, file_content)
