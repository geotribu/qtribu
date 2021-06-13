#! python3  # noqa: E265


"""
    QGIS Splash changer.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
from configparser import ConfigParser
from os import sep  # required since pathlib strips trailing whitespace
from pathlib import Path

# pyqgis
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.toolbelt import PlgLogger
from qtribu.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class SplashChanger:
    """QGIS splash screen changer."""

    def __init__(self, parent):
        """Initialization."""
        self.log = PlgLogger().log
        self.parent = parent

        # get folder path, handling different operating systems (especially Windows)
        self.plugin_splash_folder = repr(
            str(Path(DIR_PLUGIN_ROOT / "resources/images/").resolve()) + sep
        ).replace("'", "")
        self.log(
            message=f"DEBUG - Folder to look for splash screen: {self.plugin_splash_folder}",
            log_level=4,
        )

        # configuration files
        profil = Path(QgsApplication.qgisSettingsDirPath())
        self.cfg_qgis_base = profil / "QGIS/QGIS3.ini"
        self.cfg_qgis_custom = profil / "QGIS/QGISCUSTOMIZATION3.ini"

    @property
    def menu_action(self) -> QAction:
        """Returns the menu action according to the feature status.

        :return: QAction for the feature
        :rtype: QAction
        """
        feature_status = PlgOptionsManager.get_plg_settings().splash_screen_enabled

        if feature_status:
            action_splash = QAction(
                QIcon(QgsApplication.iconPath("repositoryUnavailable.svg")),
                self.tr("Splash screen: restore"),
            )
            action_splash.setToolTip(self.tr("Restore the QGIS default splash screen."))
        else:
            action_splash = QAction(
                QIcon(QgsApplication.iconPath("propertyicons/symbology.svg")),
                self.tr("Splash screen: apply custom"),
            )
            action_splash.setToolTip(
                self.tr("Apply Geotribu banner as QGIS splash screen")
            )

        return action_splash

    def switch(self) -> bool:
        """Enable or disable custom splash screen.

        :return: True if it has been enabled.
        :rtype: bool
        """
        feature_status = PlgOptionsManager.get_plg_settings().splash_screen_enabled

        if feature_status:
            self.apply_restore()
            self.log(
                message=self.tr(
                    "Splash screen: QGIS default restored. Please, restart."
                ),
                log_level=3,
                push=True,
            )
            PlgOptionsManager.set_value_from_key(
                key="splash_screen_enabled", value=False
            )
            return False
        else:
            self.enable_customization()
            self.apply_custom()
            PlgOptionsManager.set_value_from_key(
                key="splash_screen_enabled", value=True
            )
            self.log(
                message=self.tr("Splash screen: custom applied. Please, restart."),
                log_level=3,
                push=True,
            )
            return True

    def enable_customization(self):
        """Enable UI customization in QGIS for current user."""
        # read QGIS configuration file
        ini_base = ConfigParser()
        ini_base.optionxform = str
        ini_base.read(self.cfg_qgis_base, encoding="UTF8")

        # check if customization is already enabled
        if "UI" in ini_base.sections():
            ini_base.set(
                section="UI",
                option=r"Customization\enabled",
                value="true",
            )
            with self.cfg_qgis_base.open("w", encoding="UTF8") as configfile:
                ini_base.write(configfile, space_around_delimiters=False)

            self.log(message="Customization has been enabled.", log_level=1)
        else:
            self.log(message="DEBUG - Customization is already enabled.", log_level=4)

    def apply_custom(self):
        """Apply custom splash screen."""
        # modify splash path
        if self.cfg_qgis_custom.exists():
            ini_custom = ConfigParser()
            ini_custom.optionxform = str
            ini_custom.read(self.cfg_qgis_custom, encoding="UTF8")

            if "Customization" in ini_custom.sections():
                ini_custom.set(
                    section="Customization",
                    option="splashpath",
                    value=self.plugin_splash_folder,
                )
                with self.cfg_qgis_custom.open("w", encoding="UTF8") as configfile:
                    ini_custom.write(configfile, space_around_delimiters=False)

        else:
            ini_custom = ConfigParser()
            ini_custom["Customization"] = {"splashpath": self.plugin_splash_folder}
            with self.cfg_qgis_custom.open(mode="w", encoding="UTF8") as configfile:
                ini_custom.write(configfile, space_around_delimiters=False)

            self.log(
                message="Customization file did not exists. "
                f"It has been created with the new splash screen: {self.cfg_qgis_custom}"
            )

    def apply_restore(self):
        """Restore QGIS default splash screen."""
        # read customization ini file
        ini_custom = ConfigParser()
        ini_custom.optionxform = str
        ini_custom.read(self.cfg_qgis_custom, encoding="UTF8")

        if ini_custom.has_option(section="Customization", option="splashpath"):
            ini_custom.remove_option(section="Customization", option="splashpath")

        with self.cfg_qgis_custom.open(mode="w", encoding="UTF8") as configfile:
            ini_custom.write(configfile, space_around_delimiters=False)

    def tr(self, text: str) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: str
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(self.__class__.__name__, text)
