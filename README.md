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
* Reference data contain only valid PaliMsIds
* Reference data contain only valid SC UIDs
### How to run
* In your configuration file set `exec_module: "check_reference_data"`.
* Make sure `pali_canon_path`, `root_pli_ms_path` and `reference_root_path` are valid.
