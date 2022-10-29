"""
    Form to let the end-user pick its options.
"""
import logging

from pg_background_tasks.core.utilities.db_tools import get_db_connections
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import QDialog

ico_postgis = QIcon(":/images/themes/default/mIconPostgis.svg")
ico_spatialite = QIcon(":/images/themes/default/mIconSpatialite.svg")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DatabasePickerForm(QDialog):
    """Form to select the database connection to use."""

    closingPlugin = pyqtSignal()

    def __init__(
        self, parent=None, db_connections: list = [], ui_filepath: str = "db_form.ui"
    ):
        """Constructor

        :param dbname: path to db
        :type dbname: string
        :param parent: Qt parent
        :type parent: QtWidget
        """
        super(DatabasePickerForm, self).__init__(parent)
        uic.loadUi(uifile=ui_filepath.resolve(), baseinstance=self)

        # tuning
        self.rad_db_type_postgis.setIcon(ico_postgis)
        self.rad_db_type_spatialite.setIcon(ico_spatialite)

        # fill combobox
        self.rad_db_type_postgis.toggled.connect(lambda: self._cbb_fill_connections())
        self.rad_db_type_spatialite.toggled.connect(
            lambda: self._cbb_fill_connections()
        )

        # by default, trigger postgis
        self._cbb_fill_connections()

    def _cbb_fill_connections(self):
        self.cbb_db_connections.clear()
        if self.rad_db_type_postgis.isChecked():
            for k, v in get_db_connections(db_type="postgres").items():
                logger.error(type(v))
                self.cbb_db_connections.addItem(k, v)
        if self.rad_db_type_spatialite.isChecked():
            for k, v in get_db_connections(db_type="spatialite").items():
                self.cbb_db_connections.addItem(k, v)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
