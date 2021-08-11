# Unit tests

## Requirements

- QGIS 3.16+

```bash
python -m pip install -U pip
python -m pip install -U -r requirements/testing.txt
```

## Running tests

### Locally

```bash
# run all tests with PyTest and Coverage report
python -m pytest

# run a specific test module using standard unittest
python -m unittest tests.test_plg_metadata

# run a specific test function using standard unittest
python -m unittest tests.test_plg_metadata.TestPluginMetadata.test_version_semver
```

### Using Docker

Build the image:

```bash
docker build --pull --rm -f "tests/tests_qgis.dockerfile" -t qgis_316:plugin_tester .
```

Run tests:

```bash
docker run -v "$(pwd):/tmp/plugin" qgis_316:plugin_tester python3 -m pytest
```
