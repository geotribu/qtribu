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
from qgis.core import QgsProject, QgsProjectMetadata
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface

# project
from qtribu.__about__ import __icon_path__
from qtribu.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## Classes ###############
# ##################################


class EggGeotribu(object):

    APPLIED: bool = False
    KEYWORDS: tuple = ("geotribu",)
    NAME: str = "Geotribu"
    PRIORITY: int = 1

    def __init__(self):
        """Instancitation logic."""
        self.log = PlgLogger().log

    def apply(self) -> bool:
        self.log(
            message=self.tr(f"Easter egg found: {self.NAME}"),
            log_level=4,
        )

        # QGIS main window
        self.bkp_title = iface.mainWindow().windowTitle()
        # new_title = self.bkp_title.replace("QGIS", "GIStribu")
        iface.mainWindow().setWindowTitle("GISTribu")
        iface.mainWindow().setWindowIcon(QIcon(str(__icon_path__.resolve())))
        iface.pluginToolBar().setVisible(False)

        # modify menus
        iface.editMenu().setTitle("Créer")
        iface.helpMenu().setTitle("Débrouille toi !")
        iface.helpMenu().setEnabled(False)

        # Project
        current_project = QgsProject.instance()
        self.bkp_project = {"title": current_project.title()}
        current_project.setTitle(f"Easter Egg {self.NAME}")
        try:
            self.bkp_project["metadata"] = current_project.Metadata()
        except AttributeError as err:
            self.log(
                message="Project doesn't exist yet. Trace: {}".format(err),
                log_level=4,
            )
            self.bkp_project["metadata"] = None
        gt_md = QgsProjectMetadata()
        gt_md.setAuthor("Geotribu")
        gt_md.setLanguage("FRE")
        current_project.setMetadata(gt_md)

        self.APPLIED = True
        return True

    def revert(self) -> bool:
        iface.mainWindow().setWindowTitle(self.bkp_title)
        iface.pluginToolBar().setVisible(True)

        self.APPLIED = False
        return False

    def tr(self, message: str) -> str:
        """Translation method.

        :param message: text to be translated
        :type message: str

        :return: translated text
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
