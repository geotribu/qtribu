#! python3  # noqa: E265

"""
    Plugin settings dialog.
"""

# standard
import logging
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsSettings
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QButtonGroup, QHBoxLayout, QWidget

# project
from qtribu.__about__ import (
    DIR_PLUGIN_ROOT,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from qtribu.toolbelt import PlgLogger, PlgOptionsManager

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

        # customization
        self.btn_help.setIcon(QIcon(":/images/themes/default/mActionHelpContents.svg"))
        self.btn_help.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(":images/themes/default/console/iconSyntaxErrorConsole.svg")
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_tracker__))
        )

        # load previously saved settings
        self.load_settings()

    def closeEvent(self, event):
        """Map on plugin close.

        :param event: [description]
        :type event: [type]
        """
        self.closingPlugin.emit()
        event.accept()

    def load_settings(self) -> dict:
        """Load options from QgsSettings into UI form."""
        settings = PlgOptionsManager.get_plg_settings()

        # set UI from saved options
        self.opt_browser_group.button(settings.browser).setChecked(True)
        self.opt_notif_push_msg.setChecked(settings.notify_push_info)

        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)

    def save_settings(self):
        """Save options from UI form into QSettings."""
        # open settings group
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # save features
        settings.setValue("browser", self.opt_browser_group.checkedId())
        settings.setValue("notify_push_info", self.opt_notif_push_msg.isChecked())

        # save miscellaneous
        settings.setValue("debug_mode", self.opt_debug.isChecked())
        settings.setValue("version", __version__)

        # close settings group
        settings.endGroup()

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    def __init__(self):
        super().__init__()

    def icon(self):
        return QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_geotribu.png"))

    def createWidget(self, parent):
        return ConfigOptionsPage(parent)

    def title(self):
        return __title__


class ConfigOptionsPage(QgsOptionsPageWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dlg_settings = DlgSettings(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.dlg_settings.setLayout(layout)
        self.setLayout(layout)
        self.setObjectName("mOptionsPage{}".format(__title__))

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        self.dlg_settings.save_settings()
