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
