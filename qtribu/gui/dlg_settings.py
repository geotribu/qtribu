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
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QButtonGroup, QMessageBox

# project
from qtribu.__about__ import (
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from qtribu.logic.qchat_client import QChatApiClient
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser
from qtribu.toolbelt.preferences import PlgSettingsStructure
from qtribu.utils import play_resource_sound

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(Path(__file__).parent / f"{Path(__file__).stem}.ui")

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
        self.setObjectName(f"mOptionsPage{__title__}")

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        # group radio buttons
        self.opt_browser_group = QButtonGroup(self)
        self.opt_browser_group.addButton(self.opt_browser_qt, 1)
        self.opt_browser_group.addButton(self.opt_browser_os, 2)

        self.btn_rules.pressed.connect(self.show_instance_rules)
        self.btn_rules.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))

        # customization
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(partial(open_url_in_browser, __uri_homepage__))

        self.btn_report.setIcon(
            QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg"))
        )
        self.btn_report.pressed.connect(
            partial(open_url_in_browser, f"{__uri_tracker__}new/choose")
        )

        self.btn_reset_read_history.setIcon(
            QIcon(QgsApplication.iconPath("/console/iconClearConsole.svg"))
        )
        self.btn_reset_read_history.pressed.connect(self.reset_read_history)

        self.btn_reset.setIcon(QIcon(QgsApplication.iconPath("mActionUndo.svg")))
        self.btn_reset.pressed.connect(self.reset_settings)

        # load previously saved settings
        self.load_settings()

        # play sound on ringtone changed
        self.cbb_ring_tone.currentIndexChanged.connect(self.on_ring_tone_changed)

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        # features
        settings.browser = self.opt_browser_group.checkedId()
        settings.notify_push_info = self.opt_notif_push_msg.isChecked()
        settings.notify_push_duration = self.sbx_notif_duration.value()
        settings.integration_qgis_news_feed = self.chb_integration_news_feed.isChecked()
        settings.license_global_accept = self.chb_license_global_accept.isChecked()

        # qchat
        settings.qchat_instance_uri = self.le_qchat_instance_uri.text()
        settings.qchat_nickname = self.le_qchat_nickname.text()
        settings.qchat_activate_cheatcode = self.ckb_cheatcodes.isChecked()
        settings.qchat_play_sounds = self.ckb_play_sounds.isChecked()
        settings.qchat_sound_volume = self.hsl_sound_volume.value()
        settings.qchat_ring_tone = self.cbb_ring_tone.currentText()

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
        self.chb_integration_news_feed.setChecked(settings.integration_qgis_news_feed)
        self.chb_license_global_accept.setChecked(settings.license_global_accept)

        # qchat
        self.le_qchat_instance_uri.setText(settings.qchat_instance_uri)
        self.le_qchat_nickname.setText(settings.qchat_nickname)
        self.ckb_cheatcodes.setChecked(settings.qchat_activate_cheatcode)
        self.ckb_play_sounds.setChecked(settings.qchat_play_sounds)
        self.hsl_sound_volume.setValue(settings.qchat_sound_volume)
        # TODO: load and select item from settings
        # self.cbb_ring_tone.setItemText(settings.qchat_ring_tone)

        # misc
        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)

    def show_instance_rules(self) -> None:
        instance_url = self.le_qchat_instance_uri.text()
        client = QChatApiClient(instance_url)
        rules = client.get_rules()
        QMessageBox.information(
            self,
            self.tr("Instance rules"),
            self.tr("Instance rules ({instance_url}):\n\n{rules}").format(
                instance_url=instance_url, rules=rules["rules"]
            ),
        )

    def on_ring_tone_changed(self) -> None:
        """
        Action called when ringtone value is changed
        """
        play_resource_sound(
            self.cbb_ring_tone.currentText(), self.hsl_sound_volume.value()
        )

    def reset_read_history(self):
        """Set latest_content_guid to None."""
        new_settings = PlgSettingsStructure(
            latest_content_guid="",
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

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)

        # update the form
        self.load_settings()


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
