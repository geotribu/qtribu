#! python3  # noqa: E265

# standard library
import logging
from pathlib import Path
from string import Template

# PyQGIS
from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QLocale, QTranslator
from qgis.PyQt.QtWidgets import QApplication

# project package
from qtribu.__about__ import DIR_PLUGIN_ROOT, __email__, __title__
from qtribu.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes ###############
# ##################################


class PlgTranslator:

    AVAILABLE_TRANSLATIONS: tuple = None

    def __init__(
        self,
        qm_search_start_path: Path = DIR_PLUGIN_ROOT,
        tpl_filename: str = Template(f"{__title__.lower()}_$locale.qm"),
    ):
        """Helper module to manage plugin translations."""
        self.log = PlgLogger().log

        # list .qm files
        qm_files = tuple(qm_search_start_path.glob("**/*.qm"))
        self.AVAILABLE_TRANSLATIONS = tuple(q.name for q in qm_files)

        # get locale and identify the compiled translation file (*.qm) to use
        locale = QgsSettings().value("locale/userLocale", QLocale().name())[0:2]
        locale_filename = tpl_filename.substitute(locale=locale)

        self.qm_filepath = None
        for qm in qm_files:
            if qm.name == locale_filename:
                self.qm_filepath = qm
                break

        if not self.qm_filepath:
            info_msg = self.tr(
                "Your selected locale ({}) is not available. "
                "Please consider to contribute with your own translation :). "
                "Contact the plugin maintener(s): {}".format(locale, __email__)
            )
            self.log(message=str(info_msg), log_level=1, push=1)
            logger.info(info_msg)

    def get_translator(self) -> QTranslator:
        if self.AVAILABLE_TRANSLATIONS is None:
            warn_msg = self.tr(
                text="No translation found among plugin files and folders.",
                context="PlgTranslator",
            )
            logger.warning(warn_msg)
            self.log(message=warn_msg, log_level=1)
            return None

        if not self.qm_filepath:
            return None

        # load translation
        translator = QTranslator()
        translator.load(str(self.qm_filepath.resolve()))
        return translator

    def tr(self, text: str = None, context: str = "@default"):
        return QApplication.translate(context, text)
