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
exec_module: 'run_all_checks'
```


List of available scripts:

- **run_all_checks** - run all available checks
- **check_migration** - cross-validate bilara-data text against original ms_yuttadhammo source files; the result will be saved to the path specified in `example_config.yaml` file, by default: `./bilara-data/migration_differences`
- **bilara_check_comment** - check if path to comments is set up properly
- **bilara_check_html** - check if path to html files is set up properly
- **bilara_check_root** - check if path to root files is set up properly
- **bilara_check_translation** - check if path to translation files is set up properly
- **bilara_check_variant** - check if path to variant files is set up properly
- **bilara_load** - load bilara-data
- **ms_yuttadhammo_convert_to_html** - extract html files directly from original xml files
- **ms_yuttadhammo_load** - load ms_yuttadhammo
- **ms_yuttadhammo_match_root_text** - match root text of ms_yuttadhammo
- **noop** - no operation, available just for checking purposes
- **reference_data_check** - validate references

List of available scripts:

- **run_all_checks** - run all available checks
- **check_migration** - cross-validate bilara-data text against original ms_yuttadhammo source files; the result will be saved to the path specified in `example_config.yaml` file, by default: `./bilara-data/migration_differences`
- **bilara_check_comment** - check if path to comments is set up properly
- **bilara_check_html** - check if path to html files is set up properly
- **bilara_check_root** - check if path to root files is set up properly
- **bilara_check_translation** - check if path to translation files is set up properly
- **bilara_check_variant** - check if path to variant files is set up properly
- **bilara_load** - load bilara-data
- **ms_yuttadhammo_convert_to_html** - extract html files directly from original xml files
- **ms_yuttadhammo_load** - load ms_yuttadhammo
- **ms_yuttadhammo_match_root_text** - match root text of ms_yuttadhammo
- **noop** - no operation, available just for checking purposes
- **reference_data_check** - validate references

## Notes on exceptions

The scripts try to return as many possibly wrong entries as possible, and hence generate some false positives. Further refinement might eliminate these, but for now, here is a general guide to the exceptions you are likely to find. Following describes the state as of 23/6/2020.

### check_migration

Saves files to /migration_differences. Works by diffing text based on ms IDs, stripping punctuation, ṃ/ṅ differences, markup, handles some quote mark cases.

`File with the key: 'sn48.147-158' is missing in the root or reference directory`
4 false positives of this error.

Message of contains many or does not contain ms references is for information, it is not an error.

Currently shows many errors due to not aliasing ṃ and ṁ.

### bilara_check_comment

0 errors

### bilara_check_html

0 errors

### bilara_check_root

Returns 11 duplicated segments errors. These are false positives, the text repeats.

### bilara_check_translation

Currently shows false positives for not recognizing Russian texts, and German blurbs.

### bilara_check_variant

`get_wrong_uid_with_arrow`
The script checks whether the first words in the variant entry are in fact found in the associated root text. Errors are generated in several contexts. Currently 41 are returned.

- variant abbreviates with …
- English used in variant
- change in quote marks
- capitalization
- variant note is descriptive (eg. ayaṁ pāṭho si potthake natthi)
- variant is split over several segments

`get_unknown_variants] Not valid keys`
These are variants that do not use the expected arrow notation, currently counted at 298. These are not errors, but it would be good to either standardize the notation further or refine the script.

`[get_unordered_segments]`
There are '7' unordered segment errors, however these are due to script not parsing sequence properly, they are in fact in sequence.

### reference_data_check

0 errors.
