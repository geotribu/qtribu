#! python3  # noqa: E265

"""
    Plugin settings dialog.
"""

# standard
import logging
from pathlib import Path

# PyQGIS
from qgis.core import QgsSettings
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QButtonGroup, QWidget

# project
from qtribu.__about__ import __title__, __version__
from qtribu.toolbelt import PlgLogger

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
        self.log = PlgLogger().log

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # group radio buttons
        self.opt_browser_group = QButtonGroup(self)
        self.opt_browser_group.addButton(self.opt_browser_qt, 1)
        self.opt_browser_group.addButton(self.opt_browser_os, 2)

        # load previously saved settings
        self.load()

    def closeEvent(self, event):
        """Map on plugin close.

        :param event: [description]
        :type event: [type]
        """
        self.closingPlugin.emit()
        event.accept()

    def save(self):
        """Save options from UI form into QSettings."""
        # open settings group
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # save user options
        settings.setValue("browser", self.opt_browser_group.checkedId())

        # save plugin version
        settings.setValue("version", __version__)

        # close settings group
        settings.endGroup()

    def load(self) -> dict:
        """Load options from QgsSettings into UI form."""
        options_dict = {}

        # start
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # retrieve options
        self.opt_browser_group.button(
            settings.value(key="browser", defaultValue=1, type=int)
        ).setChecked(True)

        # store into output dict
        options_dict["browser"] = settings.value("browser", 1)

        # end
        settings.endGroup()

        return options_dict
