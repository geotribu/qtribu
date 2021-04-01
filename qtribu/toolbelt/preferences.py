#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
import logging

# PyQGIS
from qgis.core import QgsSettings
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QHBoxLayout

# package
from qtribu.__about__ import DIR_PLUGIN_ROOT, __title__
from qtribu.resources.gui.dlg_settings import DlgSettings

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
PLG_PREFERENCES: dict = {
    "browser": "default",  # 1 = QGIS, 2 = system
    "sources": {
        "geotribu-rss-feed-created": "https://static.geotribu.fr/feed_rss_created.xml",
        "geotribu-rss-feed-updated": "https://static.geotribu.fr/feed_rss_updated.xml",
    },
}

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> dict:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: dict
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        options_dict = {
            "browser": settings.value(
                key="browser", defaultValue=1, type=int
            ),  # 1 = QGIS, 2 = system
        }

        settings.endGroup()

        return options_dict


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_geotribu.png"))

    def createWidget(self, parent):
        return ConfigOptionsPage(parent)

    def title(self):
        return __title__


class ConfigOptionsPage(QgsOptionsPageWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dlg_settings = DlgSettings(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.dlg_settings.setLayout(layout)
        self.setLayout(layout)
        self.setObjectName("mOptionsPage{}".format(__title__))

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        self.dlg_settings.save()
