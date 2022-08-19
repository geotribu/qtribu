# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialog

# plugin
from qtribu.constants import GEORDP_NEWS_CATEGORIES
from qtribu.toolbelt import PlgLogger, PlgOptionsManager


class RdpNewsForm(QDialog):
    def __init__(self, parent=None):
        """QDialog to set user informations.

        :param parent: _description_
        :type parent: QWidget
        """
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "{}.ui".format(Path(__file__).stem), self)

        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # populate combobox of news category
        for rdp_category in GEORDP_NEWS_CATEGORIES:
            self.cbb_category.addItem(rdp_category.name)
            self.cbb_category.setItemData(
                rdp_category.order - 1, rdp_category.description, Qt.ToolTipRole
            )

        # connect help button
        self.btn_box.helpRequested.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl("https://static.geotribu.fr/contribuer/rdp/add_news/"),
            )
        )
