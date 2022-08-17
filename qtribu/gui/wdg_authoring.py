# standard
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget


class AuthoringWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        """QWidget to set user informations.

        :param parent: _description_
        :type parent: QWidget
        """
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "{}.ui".format(Path(__file__).stem), self)
