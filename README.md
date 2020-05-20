# sutta_processor

Process and check suttas.

# Installation

```bash
# Tested under python3.7
# Create your virtual environment

# Install requrements
pip install -r requirements.txt
# Install this package in develop mode
pip install -e .

# For makefile to work overwrite the path to virtual env
VENV_PATH=/pth/to/venv make test
```

# Run
```bash
# (activate your virtual env)
# Run package
sutta-processor -c ./src/example_config.yaml

# You might want to copy the configuration file somewhere and modify it to
# suit your local paths
```

# Available checks
## Validate SuttaCentral reference data
Load 1) Pali, 2) SC root data and 3) SC reference data. Checks:
* All PapliMsIds are referenced in reference data
* Reference data contain only valid MsIds
* Reference data contain only valid SC UIDs

*How to run*
* In your configuration file set `exec_module: "check_reference_data"`
* Make sure `pali_canon_path`, `bilara_root_path` and `reference_root_path` are valid


## Read data from ms_yuttadhammo source
First we need to convert xml data to html. Actual data is loaded via parsing those html.

*How to run*
* In your configuration file set `exec_module: "ms_yuttadhammo_convert_to_html"` and run the script
* In your configuration file set `exec_module: "ms_yuttadhammo_load"` and run the script

## Check bilary data segments id
Run various tests against the segments. Check `sutta_processor.application.services.bilara_data_check.BDataCheckService.check_uid_sequence_in_file`.

*How to run*
* In your configuration file set `exec_module: "bilara_check_root"` and run the script

---
*TODO*
* Check comments if they got any references to segments/MsId/other id
* `bilara_check_root` - check any and all references are incrementing
* Sort references alphabetically
* In MN, SC segments are referenced from `nya*` - check for consistency
* if two adjacent segments have identical text, then check the original root text
  [link](https://github.com/suttacentral/bilara-data/commit/8eb4cc80f2457de28d1ffef1ed17529b8ed8e85f)
* if reference data appears on any segment not found in root,
  then change reference data to the immediate next segment that appears in the root
  [link](https://github.com/suttacentral/bilara-data/commit/1aa2bc0d5a362f54b7d93568dc9a33dde42b682b)
