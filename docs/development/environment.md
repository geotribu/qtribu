# Environnement de développement

Sur Ubuntu :

```bash
# create virtual environment linking to system packages (for pyqgis)
python3.8 -m venv .venv --system-site-packages
source .venv/bin/activate

# bump dependencies inside venv
python -m pip install -U pip setuptools wheel
python -m pip install -U -r requirements/development.txt

# install project as editable
python -m pip install -e .
```

## Gestion des traductions

```bash
sudo apt install qttools5-dev-tools
```

Mise à jour des textes à traduire :

```bash
pylupdate5 -noobsolete -verbose qtribu/resources/i18n/plugin_translation.pro
```

Une fois les traductions effectuées (dans Qlinguist par exemple), les compiler :

```bash
lrelease qtribu/resources/i18n/*.ts
```
