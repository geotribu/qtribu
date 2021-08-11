# Unit tests

## Requirements

- QGIS 3.16+

```bash
python -m pip install -U pip
python -m pip install -U -r requirements/testing.txt
```

## Run unit tests

```bash
# run all tests with PyTest and Coverage report
python -m pytest

# run a specific test module using standard unittest
python -m unittest tests.test_plg_metadata

# run a specific test function using standard unittest
python -m unittest tests.test_plg_metadata.TestPluginMetadata.test_version_semver
```
