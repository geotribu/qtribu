#! python3  # noqa: E265

"""
    Plugin settings form integrated into QGIS 'Options' menu.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QButtonGroup

# project
from qtribu.__about__ import (
    DIR_PLUGIN_ROOT,
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)

# ############################################################################
# ########## Classes ###############
# ##################################


class ConfigOptionsPage(FORM_CLASS, QgsOptionsPageWidget):
    """Settings form embedded into QGIS 'options' menu."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # load UI and set objectName
        self.setupUi(self)
        self.setObjectName("mOptionsPage{}".format(__title__))

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # group radio buttons
        self.opt_browser_group = QButtonGroup(self)
        self.opt_browser_group.addButton(self.opt_browser_qt, 1)
        self.opt_browser_group.addButton(self.opt_browser_os, 2)

        # customization
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg"))
        )
        self.btn_report.pressed.connect(
            partial(QDesktopServices.openUrl, QUrl(f"{__uri_tracker__}new/choose"))
        )

        self.btn_reset_read_history.setIcon(
            QIcon(QgsApplication.iconPath("/console/iconClearConsole.svg"))
        )
        self.btn_reset_read_history.pressed.connect(self.reset_read_history)

        # load previously saved settings
        self.load_settings()

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # features
        settings.browser = self.opt_browser_group.checkedId()
        settings.notify_push_info = self.opt_notif_push_msg.isChecked()
        settings.notify_push_duration = self.sbx_notif_duration.value()
        settings.license_global_accept = self.chb_license_global_accept.isChecked()

        # misc
        settings.debug_mode = self.opt_debug.isChecked()
        settings.version = __version__

        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(settings)

        # sub widgets
        self.wdg_author.save_settings()

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )

    def load_settings(self) -> dict:
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # set UI from saved options
        self.opt_browser_group.button(settings.browser).setChecked(True)
        self.opt_notif_push_msg.setChecked(settings.notify_push_info)
        self.sbx_notif_duration.setValue(settings.notify_push_duration)
        self.chb_license_global_accept.setChecked(settings.license_global_accept)

        # misc
        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)

    def reset_read_history(self):
        """Set latest_content_guid to None."""
        new_settings = PlgSettingsStructure(
            latest_content_guid=None,
        )

        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(new_settings)

        # inform end user
        self.log(
            message=self.tr("Read history has been reset."),
            log_level=3,
            duration=2,
            push=True,
        )


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    def __init__(self):
        super().__init__()

    def icon(self) -> QIcon:
        return QIcon(str(__icon_path__))

    def createWidget(self, parent) -> ConfigOptionsPage:
        return ConfigOptionsPage(parent)

    def title(self) -> str:
        return __title__

    def helpId(self) -> str:
        return __uri_homepage__
