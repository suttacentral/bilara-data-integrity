from sutta_processor.shared.config import Config
import os
import logging
from sutta_processor.application.domain_models import YuttaAggregate
import pickle
from collections import OrderedDict
import json
import re


log = logging.getLogger(__name__)


# Text cleaning global function.


def clean_verse(verse):
    """ Cleans input text from unwanted characters. """
    verse = (
        verse.rstrip()
        .lower()
        .replace("—", " ")
        .replace(":", " ")
        .replace("…", " ")
        .replace(".", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("ṅ", "ṃ")
        .replace("“", " ")
        .replace("”", " ")
        .replace("–", " ")
        .replace("-", " ")
        .replace("?", " ")
        .replace(",", " ")
        .replace(";", " ")
        .replace("0", " ")
        .replace("1", " ")
        .replace("2", " ")
        .replace("3", " ")
        .replace("4", " ")
        .replace("5", " ")
        .replace("6", " ")
        .replace("7", " ")
        .replace("8", " ")
        .replace("9", " ")
        .replace("☑", " ")
        .replace("๐", " ")
        .replace("×", " ")
        .replace("☒", " ")
        .replace("*", "")
        .replace("|", " ")
        .replace("#", " ")
        .replace("[", " ")
        .replace("]", " ")
    )

    return " ".join(verse.split())


#############################################

# CLASSES


class Yutta:
    def __init__(self, yutta_aggregate):
        self.unused_msids_list, self.msids_list = self.generate_msids_lists(yutta_aggregate)
        self.last_msids_list = self.generate_last_msids_list(yutta_aggregate)
        self.yutta_aggregate = yutta_aggregate

    def generate_msids_lists(self, yutta_aggregate):
        """ Generate list of all ms* ids and placed them in the ascending order """
        msids_list = [msid for msid in yutta_aggregate.index.keys()]
        sorted_msids_list = sorted(msids_list, key=lambda index: (index.rsplit("_", 1)[0], int(index.rsplit("_", 1)[1])))
        return sorted_msids_list, sorted_msids_list.copy()

    def generate_last_msids_list(self, yutta_aggregate):
        """ 
        Generates dictionary in which keys are ms* ids. For every item, if ms* id is the last one in the file, it will have the True value.
        Otherwise it will be False as default value.
        """

        last_msids_list = {msid: False for msid in yutta_aggregate.index.keys()}

        for aggregated_file in yutta_aggregate.file_aggregates:
            if aggregated_file.index:
                last_msid = list(aggregated_file.index)[-1]
                last_msids_list[last_msid] = True

        return last_msids_list

    def get_verses(self, headers, start_msid, end_msid):
        """
        Generates full sutra by combining all verses from Yuttadhammo html files.
        It starts from given start_msid and add verses by selecting next ms* ids.
        Adding new verses will stop if end_msid was found. 
        If the end_msid was not the last index in the html file all verses after them till the end of the file also will be added.
        All verses which text is included in header will be ignored.
        """

        full_sutra = ""
        msid_index = self.msids_list.index(start_msid)
        cutted_msids_list = self.msids_list[(msid_index):]
        found_last_msid = False

        for msid in cutted_msids_list:
            if msid == end_msid:
                found_last_msid = True

            if clean_verse(self.yutta_aggregate.index[msid].verse) not in headers:
                full_sutra += " " + self.yutta_aggregate.index[msid].verse
            
            if msid in self.unused_msids_list: self.unused_msids_list.remove(msid)

            if self.last_msids_list[msid] and found_last_msid:
                break

        return full_sutra.lstrip()


class BilaraSutra:
    def __init__(self, bilara_file_path, reference_file_path, yutta):
        self.references = self.get_formatted_references(reference_file_path)
        self.headers = self.get_headers(bilara_file_path)
        self.content = self.get_formatted_content(bilara_file_path)
        self.yutta = yutta

    def remove_headers(self, data):
        """ Removes headers from reference file """
        for index in list(data.keys()):
            if "0" in index.split(":")[1].split("."):
                del data[index]

    def remove_non_ms_indexes(self, references):
        """
        Remove ids which do not start with 'ms' or start with 'msdiv' characters.
        If there is no ms* id in the data, the whole index will be removed.
        """
        ms_regex = "ms(?!div)\w+"

        for index, msids in references.copy().items():
            founded_msids = re.findall(ms_regex, msids)

            if len(founded_msids) > 1:
                log.error(f"This reference contains many ms* ids: {index}: {msids}")
                references.clear()
                break
            elif founded_msids:
                references[index] = founded_msids[0]
            else:
                del references[index]

    def get_formatted_references(self, reference_file_path):
        """
        Load data from reference file, removes headers indexes and non ms* ids.
        By the end it returns the first and last msid in the reference data.
        If there is just one msisd in the references it will be returned as the first and last one twice.
        If there is no msid in the references, the empty list will be returned.
        """
        with open(reference_file_path, "r") as file:
            references = json.load(file)

        self.remove_headers(references)
        self.remove_non_ms_indexes(references)

        msids_list = list(references.values())
        sorted_msids_list = sorted(
            msids_list, key=lambda index: (index.rsplit("_", 1)[0], int(index.rsplit("_", 1)[1]))
        )

        if not msids_list:
            log.error(f"This reference file does not conaint ms* ids: {reference_file_path}")
            return []
        elif msids_list != sorted_msids_list:
            log.error(f"In this file, the ms* ids are not in order: {reference_file_path}")
            return []
        else:
            return [msids_list[0], msids_list[-1]]

    def get_headers(self, bilara_file_path):
        """ Create list with texts of all headers in the sutra. """
        with open(bilara_file_path, "r") as file:
            content = json.load(file)

        headers = []

        for index, text in content.items():
            if "0" in index.split(":")[1].split("."):
                headers.append(clean_verse(text))

        return headers

    def get_formatted_content(self, bilara_file_path):
        """ Load and clean data from bilara file. All headers are removed from the dictionary. """
        with open(bilara_file_path, "r") as file:
            content = json.load(file)

        self.remove_headers(content)
        return content

    def generate_bilara_sutra(self):
        """ Join all verses from bilara content together. Some versers do not have the extra whitespace at the end."""
        sutra = ""

        for text in self.content.values():
            if not text:
                continue
            text = text if text[-1] == " " else text + " "
            sutra += text

        return sutra

    def format_output(self, msids, bilara_sutra, bilara_extra_words, yutthadammo_sutra, yutthadamo_extra_words):
        return {
            "msids": msids,
            "bilara_sutra": bilara_sutra,
            "bilara_extra_words": " ".join(bilara_extra_words),
            "yutthadammo_sutra": yutthadammo_sutra,
            "yutthadamo_extra_words": " ".join(yutthadamo_extra_words),
        }

    def get_differences(self):
        """ Checks if sutras form Bilara-data and Yuttadhammo match together. """

        # Return False if reference file is missing or corrupted.
        if not self.references:
            return None

        bilara_sutra = self.generate_bilara_sutra()
        yutta_sutra = self.yutta.get_verses(self.headers, self.references[0], self.references[1])

        clean_bilara_sutra = clean_verse(bilara_sutra)
        clean_yutta_sutra = clean_verse(yutta_sutra)

        if clean_bilara_sutra != clean_yutta_sutra:

            bilara_difference = clean_bilara_sutra.split()
            for word in clean_yutta_sutra.split():
                if word in bilara_difference:
                    bilara_difference.remove(word)

            yuta_difference = clean_yutta_sutra.split()
            for word in clean_bilara_sutra.split():
                if word in yuta_difference:
                    yuta_difference.remove(word)

            return self.format_output(
                self.references, clean_bilara_sutra, bilara_difference, clean_yutta_sutra, yuta_difference
            )

        return None


## ################## ##

# HELPERS FUNCTIONS

# Getting BilaraSutra objects


def get_file_paths(directory, key_separator):
    """ 
    Returns file key - file path pair for every file in the directory.
    E.g. "an10.48": "/bilara-data/reference/pli/ms/sutta/an/an10/an10.48_reference.json"
         "an10.48": "/bilara-data/root/pli/ms/sutta/an/an10/an10.48_root-pli-ms.json
    """
    file_paths = dict()

    for path, _, files in os.walk(directory):
        for name in files:
            file_key = name.split(key_separator)[0]
            file_paths[file_key] = os.path.join(path, name)

    return file_paths


def get_matched_bilara_files(cfg):
    """ Generates list of matching *root.json and *reference.json files from the Bilary-data directory. """
    matched_files = list()
    bilara_file_paths = get_file_paths(cfg.bilara_root_path, "_root")
    reference_file_paths = get_file_paths(cfg.reference_root_path, "_reference")

    bilara_keys_set = set(bilara_file_paths)
    reference_keys_set = set(reference_file_paths)

    missing_keys = bilara_keys_set.symmetric_difference(reference_keys_set)
    matched_keys = sorted(bilara_keys_set.intersection(reference_keys_set))

    for key in missing_keys:
        log.error("File with the key: '%s' is missing in the root or reference directory.", key)

    for key in matched_keys:
        matched_files.append(
            {"bilara_file_path": bilara_file_paths[key], "reference_file_path": reference_file_paths[key]}
        )

    return matched_files


def get_bilara_sutras(cfg, yutta):
    """ Creates BilaraSutra object for every sutra-reference file pairs in the Bilara-data """
    matched_bilara_files = get_matched_bilara_files(cfg)
    bilara_sutras = list()

    for files in matched_bilara_files:
        bilara_sutras.append(BilaraSutra(**files, yutta=yutta))

    return bilara_sutras


# Getting Yuta object


def get_yutta(cfg):
    """ Generate Yutta class object using data from Yuthaddamo files. """

    # Use this code to save yuthta_agregate data on local disc and speed up loading the Yuthadammo sutras for processing.

    # yutta_aggregate = None

    # if os.path.isfile("./yutta_aggregate.pickle"):
    #     with open("./yutta_aggregate.pickle", "rb") as file:
    #         yutta_aggregate = pickle.load(file)
    # else:
    #     yutta_aggregate = cfg.repo.yutta.get_aggregate()

    #     with open("yutta_aggregate.pickle", "wb") as file:
    #         pickle.dump(yutta_aggregate, file, protocol=pickle.HIGHEST_PROTOCOL)

    yutta_aggregate = cfg.repo.yutta.get_aggregate()

    return Yutta(yutta_aggregate)


# Saving script result


def save_result(directory, sutra_differences):
    bilara_differences_path = os.path.join(directory, "bilara_differences.json")
    yutta_differences_path = os.path.join(directory, "yutta_differences.json")
    extra_words_summary_path = os.path.join(directory, "extra_words_summary.json")
    bilara_differences = dict()
    yutta_differences = dict()
    extra_words_summary = dict()

    for sutra_difference in sutra_differences:
        msids = " - ".join(sutra_difference["msids"])

        bilara_differences[msids] = {
            "text": sutra_difference["bilara_sutra"],
            "extra_words": sutra_difference["bilara_extra_words"],
        }

        yutta_differences[msids] = {
            "text": sutra_difference["yutthadammo_sutra"],
            "extra_words": sutra_difference["yutthadamo_extra_words"],
        }

        extra_words_summary[msids] = {
            "bilara_extra_words": sutra_difference["bilara_extra_words"],
            "yuttadhammo_extra_words": sutra_difference["yutthadamo_extra_words"],
        }

    with open(bilara_differences_path, "w") as file:
        json.dump(bilara_differences, file, indent=2, ensure_ascii=False)

    with open(yutta_differences_path, "w") as file:
        json.dump(yutta_differences, file, indent=2, ensure_ascii=False)

    with open(extra_words_summary_path, "w") as file:
        json.dump(extra_words_summary, file, indent=2, ensure_ascii=False)


## ################## ##

# MAIN SCRIPT


def check_migration(cfg: Config):
    yutta = get_yutta(cfg)
    bilara_sutras = get_bilara_sutras(cfg, yutta)
    sutras_differences = list()

    sutras_count = len(bilara_sutras)
    matched_sutras = 0

    for index, bilara_sutra in enumerate(bilara_sutras):
        if index % 100 == 0:
            print(f"Processed: {sutras_count}/{index}")

        sutra_differences = bilara_sutra.get_differences()
        if sutra_differences is None:
            matched_sutras += 1
        else:
            sutras_differences.append(sutra_differences)

    if sutras_differences:
        save_result(cfg.migration_differences_path, sutras_differences)

    log.info(
        f"""
        Verses from Yuttadhammo which have not been used : 
        
        {[yutta.unused_msids_list]}

        List of duplicated references: 
        Sutras checked: {sutras_count}
        Matched texts: {matched_sutras}
        Bugs: {sutras_count - matched_sutras}
    """
    )

