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

from qtribu.__about__ import DIR_PLUGIN_ROOT

# project
from qtribu.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class SplashChanger:
    def __init__(self):
        """QGIS splash screen changer.

        In QGIS3.ini:

        [UI]
        Customization\enabled=true

        In QGISCUSTOMIZATION3.ini:
        [Customization]
        splash_path={/absolute_path/to/an_image_600x300.jpeg}

        """
        self.log = PlgLogger().log
        self.plugin_splash = f"{DIR_PLUGIN_ROOT / 'resources/images/'}{sep}"

        # configuration files
        profil = Path(QgsApplication.qgisSettingsDirPath())
        self.cfg_qgis_base = profil / "QGIS/QGIS3.ini"
        self.cfg_qgis_custom = profil / "QGIS/QGISCUSTOMIZATION3.ini"

    def check_ini(self):
        # enable customization
        ini_base = ConfigParser()
        ini_base.optionxform = str
        ini_base.read(self.cfg_qgis_base, encoding="UTF8")
        if "UI" in ini_base.sections():
            ini_base.set(
                section="UI",
                option=r"Customization\enabled",
                value="true",
            )
            self.log("héhé", log_level=3, push=True)
            with self.cfg_qgis_base.open("w", encoding="UTF8") as configfile:
                ini_base.write(configfile, space_around_delimiters=False)

        # modify splash path
        if self.cfg_qgis_custom.exists():
            ini_custom = ConfigParser()
            ini_custom.optionxform = str
            ini_custom.read(self.cfg_qgis_custom, encoding="UTF8")

            if "Customization" in ini_custom.sections():
                ini_custom.set(
                    section="Customization",
                    option="splashpath",
                    value=self.plugin_splash,
                )
                with self.cfg_qgis_custom.open("w", encoding="UTF8") as configfile:
                    ini_custom.write(configfile, space_around_delimiters=False)

        else:
            ini_custom = ConfigParser()
            ini_custom["Customization"] = {"splashpath": self.plugin_splash}
            with self.cfg_qgis_custom.open(mode="w", encoding="UTF8") as configfile:
                ini_custom.write(configfile, space_around_delimiters=False)

            self.log(
                message="Customization file did not exists. "
                f"It has been created with the new splash screen: {self.cfg_qgis_custom}"
            )
