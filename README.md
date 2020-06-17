# sutta_processor

Process, check and validate text from bilara-data and original ms_yuttadhammo source.

# Setting up

This package require Python distribution (it was tested using Python 3.7), thus please make sure that such a version (or newer) is available at your machine. If not, please download it from https://www.python.org/downloads/.

1. Clone the repository to your machine

```bash
git clone https://github.com/suttacentral/sc-renumber-segments.git
```

2. Clone bilara-data repository to your machine

```bash
git clone https://github.com/suttacentral/bilara-data.git
```

3. Create new virtual environment in the same directory as cloned sc-renumber-segments

```bash
python3 -m venv ./sc-renumber-segments/
```

4. Activate your virtual environment

```bash
source ./sc-renumber-segments/bin/activate
```

5. Install requirements

```bash
pip install -r requirements.txt
```

6. Install application in developer mode

```bash
pip install -e .
```

7. Copy config file to the current directory

```bash
cp sc-renumber-segments/src/example_config.yaml .
```

8. Try running sutta-processor app

```bash
sutta-processor -c example_config.yaml
```

If everything was set up correctly, you should see such a notification:

```bash
Loading config: 'example_config.yaml'
Script is working!
```
# Running the application

Whenever you want to run a particular script from the app just change  `exec_module` of the `example_config.yaml` file to whatever you choose - for instance:

```bash
exec_module: 'check_migration'
```


List of available scripts:

- **run_all_checks** - run all available checks
- **check_migration** - cross-validate bilara-data text against original ms_yuttadhammo source files
- **bilara_check_comment** - check if path to comments is set up properly
- **bilara_check_html** - check if path to html files is set up properly
- **bilara_check_root** - check if path to root files is set up properly
- **bilara_check_translation** - check if path to translation files is set up properly
- **bilara_check_variant** - check if path to variant files is set up properly
- **bilara_load** - load bilara-data
- **ms_yuttadhammo_convert_to_html** - extract html files directly from original xml files
- **ms_yuttadhammo_load** - load ms_yuttadhammo
- **ms_yuttadhammo_match_root_text**** - match root text of ms_yuttadhammo
- **noop** - no operation, available just for checking purposes
- **reference_data_check** - validate references




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
