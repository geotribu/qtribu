#! python3  # noqa: E265

"""
    Easter egg on widget Coordinates.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging

# PyQGIS
from qgis.core import QgsApplication, QgsProject, QgsProjectMetadata
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QLineEdit, QMessageBox
from qgis.utils import iface

# project
from qtribu.logic.eastereggs.egg_tribu import EggGeotribu
from qtribu.toolbelt import PlgLogger
from qtribu.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes ###############
# ##################################


class PlgEasterEggs:

    CONNECTION_ENABLED: bool = False
    EGG_TROLL_APPLIED: bool = False

    def __init__(self, parent):
        """Instancitation logic."""
        self.log = PlgLogger().log
        self.parent = parent

        # -- Easter eggs ---------------------------------------------------------------
        self.eggs: tuple = (EggGeotribu(),)

        # on attrape la barre de statut de QGIS
        qgis_st = iface.mainWindow().statusBar()

        # on filtre la barre de statut pour ne garder le widget des coordonnées
        for wdgt in qgis_st.children()[1].children():
            if wdgt.objectName() == "mCoordsEdit":
                break

        # dans le widget, on ne garde que la ligne de saisie
        self.le_coords = wdgt.findChild(QLineEdit)

    def switch(self):
        if self.CONNECTION_ENABLED:
            self.parent.action_eastereggs.setIcon(
                QIcon(QgsApplication.iconPath("repositoryConnected.svg")),
            )
            self.le_coords.editingFinished.disconnect(self.on_coords_changed)
            self.CONNECTION_ENABLED = False
            PlgOptionsManager.set_value_from_key(key="easter_eggs_enabled", value=False)
            self.log(message="Easter eggs connection has been disabled.")
        else:
            self.parent.action_eastereggs.setIcon(
                QIcon(QgsApplication.iconPath("repositoryUnavailable.svg")),
            )
            self.le_coords.editingFinished.connect(self.on_coords_changed)
            self.CONNECTION_ENABLED = True
            PlgOptionsManager.set_value_from_key(key="easter_eggs_enabled", value=True)
            self.log(message="Easter eggs connection has been enabled.")

            for egg in self.eggs:
                if egg.APPLIED:
                    egg.revert()

    def on_coords_changed(self):
        for egg in self.eggs:
            if not egg.APPLIED and self.le_coords.text() in egg.KEYWORDS:
                self.le_coords.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
                egg.apply()
                break

    # -- Easter eggs -------------------------------------------------------------------
    def egg_coords_arcgis(self):
        """Easter egg to mimic the behavior of ArcGIS Pro license subscription."""
        if not self.EGG_TROLL_APPLIED:
            app = QApplication.instance()
            app.setStyleSheet(".QWidget {color: green; background-color: blue;}")
            self.log(
                message="Easter egg found! Let's ask end-user for his QGIS license subscription."
            )

            # message box
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("QGIS Pro")
            msg.setInformativeText(
                "Your account is not licensed for QGIS Pro. "
                "Please ask your organization administrator to assign you a user type "
                "that is compatible with QGIS Pro (e.g. Creator) along with an add-on "
                "QGIS Pro license, or a user type that includes QGIS Pro "
                "(e.g. GIS Professional)."
            )
            msg.exec_()

            self.EGG_TROLL_APPLIED = True
        else:
            self.EGG_TROLL_APPLIED = False

    def tr(self, message: str) -> str:
        """Translation method.

        :param message: text to be translated
        :type message: str

        :return: translated text
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
