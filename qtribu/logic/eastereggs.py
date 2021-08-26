#! python3  # noqa: E265

"""
    Easter egg on widget Coordinates.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging

# 3rd party
import PyQt5

# PyQGIS
from qgis.core import QgsApplication, QgsProject, QgsProjectMetadata
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QLineEdit

# project
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
    EGG_GEOTRIBU_APPLIED: bool = False
    EGG_TROLL_APPLIED: bool = False

    def __init__(self, parent):
        """Instancitation logic."""
        self.log = PlgLogger().log
        self.parent = parent

        # on attrape la barre de statut de QGIS
        qgis_st = parent.iface.mainWindow().statusBar()

        # on filtre la barre de statut pour ne garder le widget des coordonnées
        for wdgt in qgis_st.children()[1].children():
            if wdgt.objectName() == "mCoordsEdit":
                break

        # dans le widget, on ne garde que la ligne de saisie
        self.le_coords = wdgt.findChild(PyQt5.QtWidgets.QLineEdit)

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

    def on_coords_changed(self):
        if self.le_coords.text() == "geotribu":
            self.egg_coords_geotribu()
        elif self.le_coords.text() in ("arcgis", "qgis pro"):
            self.egg_coords_arcgis()
        else:
            pass

    # -- Easter eggs -------------------------------------------------------------------
    def egg_coords_arcgis(self):
        """Easter egg to mimic the behavior of ArcGIS Pro license subscription."""
        if not self.EGG_TROLL_APPLIED:
            app = QApplication.instance()
            app.setStyleSheet(".QWidget {color: blue; background-color: yellow;}")
            self.log(
                message="Easter egg found! Let's ask end-user for his QGIS licensesubscription."
            )

            self.EGG_TROLL_APPLIED = True
        else:
            self.EGG_TROLL_APPLIED = False

    def egg_coords_geotribu(self):
        """Easter egg just for the fun."""
        if not self.EGG_GEOTRIBU_APPLIED:
            self.log(
                message="Easter egg found! Let's make a little mess just for the fun!"
            )
            self.le_coords.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)

            current_project = QgsProject.instance()
            bkp_project = {"title": current_project.title()}
            current_project.setTitle("Geotribu Easter Egg")

            # metadata
            bkp_project["metadata"] = current_project.Metadata()
            gt_md = QgsProjectMetadata()
            gt_md.setAuthor("Geotribu")
            gt_md.setLanguage("FRE")
            current_project.setMetadata(gt_md)

            self.EGG_GEOTRIBU_APPLIED = True
        else:
            self.EGG_GEOTRIBU_APPLIED = False
