#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
import logging

# PyQGIS
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QHBoxLayout

# package
from qtribu.__about__ import DIR_PLUGIN_ROOT

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


PLG_PREFERENCES: dict = {
    "browser": "default",  # default or qgis
    "sources": {
        "geotribu-rss-feed-created": "https://static.geotribu.fr/feed_rss_created.xml",
        "geotribu-rss-feed-updated": "https://static.geotribu.fr/feed_rss_updated.xml",
    },
}


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_geotribu.png"))

    def createWidget(self, parent):
        return ConfigOptionsPage(parent)


class ConfigOptionsPage(QgsOptionsPageWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
