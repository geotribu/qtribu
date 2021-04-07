#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
import logging
from typing import NamedTuple

# PyQGIS
from qgis.core import QgsSettings

# package
from qtribu.__about__ import __title__, __version__
from qtribu.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
plg_logger = PlgLogger()

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgSettingsStructure(NamedTuple):
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # RSS feed
    rss_source: str = "https://static.geotribu.fr/feed_rss_created.xml"

    # usage
    browser: int = 1

    # network
    network_http_user_agent: str = f"{__title__}/{__version__}"

    defaults = [
        False,
        __version__,
        "https://static.geotribu.fr/feed_rss_created.xml",
        1,
        f"{__title__}/{__version__}",
    ]

    @property
    def browser_as_str(self) -> str:
        if self.browser == 1:
            return "qgis"
        elif self.browser == 2:
            return "system"
        else:
            logger.error(f"Invalid browser code: {self.impex_access_mode}")
            return "qgis"


class PlgOptionsManager:
    @staticmethod
    def get_plg_settings() -> PlgSettingsStructure:
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings
        :rtype: PlgSettingsStructure
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        options = PlgSettingsStructure(
            # normal
            debug_mode=settings.value(key="debug_mode", defaultValue=False, type=bool),
            version=settings.value(key="version", defaultValue=__version__, type=str),
            # usage
            browser=settings.value(key="browser", defaultValue=1, type=int),
            # network
            network_http_user_agent=settings.value(
                key="network_http_user_agent",
                defaultValue=f"{__title__}/{__version__}",
                type=str,
            ),
        )

        settings.endGroup()

        return options

    @staticmethod
    def get_value_from_key(key: str, default=None, exp_type=None):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            logger.error(
                "Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                )
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            logger.error(err)
            plg_logger.log(err)
            out_value = None

        settings.endGroup()

        return out_value
