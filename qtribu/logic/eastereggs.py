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
import PyQt5
from qgis.gui import QgisInterface
from qgis.core import QgsProject, QgsProjectMetadata

from qgis.PyQt.QtWidgets import QLineEdit
from qgis.PyQt.QtWidgets import QApplication

# project
from qtribu.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes ###############
# ##################################


class PlgEasterEggs:

    CONNECTION_ENABLED: bool = False
    EGG_GEOTRIBU_APPLIED: bool = False
    EGG_TROLL_APPLIED: bool = False

    def __init__(self, iface: QgisInterface):
        """Instancitation logic."""
        self.log = PlgLogger().log

        # on attrape la barre de statut de QGIS
        qgis_st = iface.mainWindow().statusBar()

        # on filtre la barre de statut pour ne garder le widget des coordonnées
        for wdgt in qgis_st.children()[1].children():
            if wdgt.objectName() == "mCoordsEdit":
                break

        # dans le widget, on ne garde que la ligne de saisie
        self.le_coords = wdgt.findChild(PyQt5.QtWidgets.QLineEdit)

    def switch(self):
        if self.CONNECTION_ENABLED:
            self.le_coords.editingFinished.disconnect(self.on_coords_changed)
            self.log(message="Easter eggs connection has been disabled.")
        else:
            self.le_coords.editingFinished.connect(self.on_coords_changed)
            self.log(message="Easter eggs connection has been enabled.")

    def egg_coords_arcgis(self):
        if not self.EGG_TROLL_APPLIED:
            app = QApplication.instance()
            app.setStyleSheet(".QWidget {color: blue; background-color: yellow;}")
            self.log(message="Easter egg found! Let's ask end-user for his QGIS licensesubscription.")


    def egg_coords_geotribu(self):
        if not self.EGG_GEOTRIBU_APPLIED:
            self.log(message="Easter egg found! Let's ask end-user for his QGIS licensesubscription.")
            self.le_coords.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)

            current_project = QgsProject.instance()
            current_project.setTitle("Geotribu Easter Egg")

            # metadata
            gt_md = QgsProjectMetadata()
            gt_md.setAuthor("Geotribu")
            gt_md.setLanguage("FRE")
            current_project.setMetadata(gt_md)

    def on_coords_changed(self, text: str):
        if self.le_coords.text() == "geotribu":
            self.egg_coords_geotribu()
        elif self.le_coords.text() in ("arcgis", "qgis pro"):
            self.egg_coords_arcgis()
        else:
            pass
