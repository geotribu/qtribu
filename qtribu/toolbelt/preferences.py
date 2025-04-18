#! python3  # noqa: E265

"""
Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields
from pathlib import Path

# PyQGIS
from qgis.core import Qgis, QgsSettings

# package
import qtribu.toolbelt.log_handler as log_hdlr
from qtribu.__about__ import __title__, __version__
from qtribu.toolbelt.application_folder import get_app_dir

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__
    local_app_folder: Path = get_app_dir(dir_name="cache")

    # RSS feed
    json_feed_source: str = "https://geotribu.fr/feed_json_created.json"
    latest_content_guid: str = ""
    rss_source: str = "https://geotribu.fr/feed_rss_created.xml"
    rss_poll_frequency_hours: int = 24

    # QChat
    qchat_instance_uri: str = "https://gischat.geotribu.net"
    qchat_auto_reconnect: bool = True
    qchat_auto_reconnect_room: str = None
    qchat_activate_cheatcode: bool = True
    qchat_display_admin_messages: bool = False
    qchat_show_avatars: bool = True
    qchat_incognito_mode: bool = False
    qchat_play_sounds: bool = True
    qchat_sound_volume: int = 33
    qchat_ring_tone: str = "beep_1"
    qchat_color_mention: str = "#4169e1"
    qchat_color_self: str = "#00cc00"
    qchat_color_admin: str = "#ffa500"

    # usage
    browser: int = 1
    notify_push_info: bool = True
    notify_push_duration: int = 10
    splash_screen_enabled: bool = False
    license_global_accept: bool = False
    integration_qgis_news_feed: bool = True

    # network
    network_http_user_agent: str = f"{__title__}/{__version__}"
    request_path: str = (
        f"utm_source=QGIS&utm_medium={__title__}&utm_campaign=plugin_{__version__}"
    )

    # authoring
    author_nickname: str = ""
    author_avatar: str = "mGeoPackage.svg"
    author_firstname: str = ""
    author_lastname: str = ""
    author_email: str = ""
    author_github: str = ""
    author_linkedin: str = ""
    author_twitter: str = ""
    author_mastodon: str = ""

    @property
    def browser_as_str(self) -> str:
        """Returns matching browser value name from its code.

        :return: browser value name
        :rtype: str
        """
        if self.browser == 1:
            return "qgis"
        elif self.browser == 2:
            return "system"
        else:
            log_hdlr.PlgLogger.log(
                message=f"Invalid browser code: {self.browser}", log_level=1
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
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # map settings values to preferences object
        li_settings_values = []
        for i in settings_fields:
            li_settings_values.append(
                settings.value(key=i.name, defaultValue=i.default, type=i.type)
            )

        # instanciate new settings object
        options = PlgSettingsStructure(*li_settings_values)

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
                log_level=Qgis.MessageLevel.Warning,
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
        """Set plugin QgsSettings value using the key.

        :param key: QSettings key
        :type key: str
        :param value: value to set
        :type value: depending on the settings

        :return: plugin settings value or False if failed
        """
        if not hasattr(PlgSettingsStructure, key):
            log_hdlr.PlgLogger.log(
                message="Bad settings key: {}. Must be one of: {}".format(
                    key, ",".join(PlgSettingsStructure._fields)
                ),
                log_level=Qgis.MessageLevel.Critical,
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

        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)

        settings.endGroup()
