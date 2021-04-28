# sutta_processor

Process, check, and validate text from bilara-data and original ms_yuttadhammo source.

# Setting up

This package requires Python. It was tested using Python 3.7, so please make sure that version (or a newer one ) is available on your machine. If is isn't, please download it from https://www.python.org/downloads/.

1. Clone the repository to your machine.

```bash
git clone https://github.com/suttacentral/sc-renumber-segments.git
```

2. Clone bilara-data repository to your machine inside the sc-renumber-segments directory.

```bash
git clone https://github.com/suttacentral/bilara-data.git
```

You should now have a directory structure like `path/to/sc-renumber-segments/bilara-data/`.

3. Create new virtual environment in the same directory as the cloned sc-renumber-segments.

```bash
python3 -m venv ./sc-renumber-segments/
```

4. Activate your virtual environment.

```bash
source ./sc-renumber-segments/bin/activate
```

5. Install requirements.

```bash
pip install -r requirements.txt
```

6. Install application in developer mode. Note the "." at the end of the command.

```bash
pip install -e .
```

7. Copy the config file to the current directory. Note the "." at the end of the command.

```bash
cp sc-renumber-segments/src/example_config.yaml .
```

8. Try running the sutta-processor app.

```bash
sutta-processor -c example_config.yaml
```

If everything was set up correctly, you should see the following output:

```bash
Loading config: 'example_config.yaml'
Script is working!
```
# Running the application

Whenever you want to run a particular script from the app just change `exec_module` in the `example_config.yaml`. For example:

```bash
exec_module: 'run_all_checks'
```

`sutta-processor` operates in two different scopes:
1. all files found in the relevant directories, like `html ` or `root`
2. a list of files supplied to the application as arguments

Scope 2 is meant to run on a list of changed files from a git commit.

List of available scripts (unless otherwise noted, all scripts run in Scope 1):

- **check_all_changes** - run checks on supplied list of files (Scope 2)
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

There are several false positives generated by `sutta-processor`.  These have been listed in the file `false_positives.yaml`, which is required by `sutta-processor` to run without raising errors for those false positives. 
