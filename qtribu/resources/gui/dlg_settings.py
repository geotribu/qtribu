#! python3  # noqa: E265

"""
    Plugin settings dialog.
"""

# standard
import logging
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)

# ############################################################################
# ########## Classes ###############
# ##################################


class DlgSettings(QWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(DlgSettings, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
