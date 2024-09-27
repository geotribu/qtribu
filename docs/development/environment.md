# Environnement de développement

Sur Ubuntu :

```sh
# create virtual environment linking to system packages (for pyqgis)
python3 -m venv .venv --system-site-packages
source .venv/bin/activate

# bump dependencies inside venv
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements/development.txt

# install git hooks (pre-commit)
pre-commit install
```
