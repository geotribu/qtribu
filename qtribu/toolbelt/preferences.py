#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
from typing import NamedTuple

# PyQGIS
from qgis.core import QgsSettings

# package
import qtribu.toolbelt.log_handler as log_hdlr
from qtribu.__about__ import __title__, __version__

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgSettingsStructure(NamedTuple):
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # remote
    website_url: str = "https://static.geotribu.fr"
    cdn_url: str = "https://cdn.geotribu.fr"
    rss_source: str = f"{website_url}/feed_rss_created.xml"

    # usage
    browser: int = 1
    notify_push_info: bool = True
    notify_push_duration: int = 10
    latest_content_guid: str = None
    splash_screen_enabled: bool = False

    # network
    network_http_user_agent: str = f"{__title__}/{__version__}"
    request_path: str = (
        f"utm_source=QGIS&utm_medium={__title__}&utm_campaign=plugin_{__version__}"
    )

    @property
    def browser_as_str(self) -> str:
        """Returns mathcing browser value name from its code.

        :return: browser value name
        :rtype: str
        """
        if self.browser == 1:
            return "qgis"
        elif self.browser == 2:
            return "system"
        else:
            log_hdlr.PlgLogger.log(
                message=f"Invalid browser code: {self.impex_access_mode}", log_level=1
            )
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
            # global
            debug_mode=settings.value(key="debug_mode", defaultValue=False, type=bool),
            version=settings.value(key="version", defaultValue=__version__, type=str),
            # usage
            browser=settings.value(key="browser", defaultValue=1, type=int),
            notify_push_info=settings.value(
                key="notify_push_info", defaultValue=True, type=bool
            ),
            notify_push_duration=settings.value(
                key="notify_push_duration", defaultValue=10, type=int
            ),
            latest_content_guid=settings.value(
                key="latest_content_guid", defaultValue="", type=str
            ),
            website_url=settings.value(
                key="geotribu_url",
                defaultValue="https://static.geotribu.fr",
                type=str,
            ),
            rss_source=settings.value(
                key="rss_source",
                defaultValue="https://static.geotribu.fr/feed_rss_created.xml",
                type=str,
            ),
            splash_screen_enabled=settings.value(
                key="splash_screen_enabled",
                defaultValue=False,
                type=bool,
            ),
            # network
            network_http_user_agent=settings.value(
                key="network_http_user_agent",
                defaultValue=f"{__title__}/{__version__}",
                type=str,
            ),
            request_path=settings.value(
                key="request_path",
                defaultValue=f"utm_source=QGIS&utm_medium={__title__}"
                f"&utm_campaign=plugin_{__version__}",
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
            log_hdlr.PlgLogger.log(
                message="Bad settings key. Must be one of: {}".format(
                    ",".join(PlgSettingsStructure._fields)
                ),
                log_level=1,
            )
            return None

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            out_value = settings.value(key=key, defaultValue=default, type=exp_type)
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to get settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = None

        settings.endGroup()

        return out_value

    @classmethod
    def set_value_from_key(cls, key: str, value):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key: {}. Must be one of: {}".format(
                    key, ",".join(PlgSettingsStructure._fields)
                ),
                log_level=2,
            )
            return False

        settings = QgsSettings()
        settings.beginGroup(__title__)

        try:
            settings.setValue(key, value)
            out_value = True
            log_hdlr.PlgLogger.log(
                f"Setting `{key}` saved with value `{value}`", log_level=4
            )
        except Exception as err:
            log_hdlr.PlgLogger.log(
                message="Error occurred trying to set settings: {}.Trace: {}".format(
                    key, err
                )
            )
            out_value = False

        settings.endGroup()

        return out_value

    @classmethod
    def save_from_object(cls, plugin_settings_obj: PlgSettingsStructure):
        """Load and return plugin settings as a dictionary. \
        Useful to get user preferences across plugin logic.

        :return: plugin settings value matching key
        """
        settings = QgsSettings()
        settings.beginGroup(__title__)

        for k, v in plugin_settings_obj._asdict().items():
            cls.set_value_from_key(k, v)

        settings.endGroup()
