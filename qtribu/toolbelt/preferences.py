#! python3  # noqa: E265

"""
    Plugin settings.
"""

# standard
from dataclasses import asdict, dataclass, fields

# PyQGIS
from qgis.core import QgsSettings

# package
import qtribu.toolbelt.log_handler as log_hdlr
from qtribu.__about__ import __title__, __version__

# ############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class PlgSettingsStructure:
    """Plugin settings structure and defaults values."""

    # global
    debug_mode: bool = False
    version: str = __version__

    # RSS feed
    rss_source: str = "https://static.geotribu.fr/feed_rss_created.xml"

    # usage
    browser: int = 1
    notify_push_info: bool = True
    notify_push_duration: int = 10
    latest_content_guid: str = None
    splash_screen_enabled: bool = False
    license_global_accept: bool = False

    # network
    network_http_user_agent: str = f"{__title__}/{__version__}"
    request_path: str = (
        f"utm_source=QGIS&utm_medium={__title__}&utm_campaign=plugin_{__version__}"
    )

    # authoring
    author_firstname: str = ""
    author_lastname: str = ""
    author_email: str = ""
    author_github: str = ""
    author_linkedin: str = ""
    author_twitter: str = ""

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
        # get dataclass fields definition
        settings_fields = fields(PlgSettingsStructure)

        # retrieve settings from QGIS/Qt
        settings = QgsSettings()
        settings.beginGroup(__title__)

        # instanciate new settings object
        options = PlgSettingsStructure(
            # normal
            settings.value(
                key=settings_fields[0].name,
                defaultValue=settings_fields[0].default,
                type=settings_fields[0].type,
            ),
            settings.value(
                key=settings_fields[1].name,
                defaultValue=settings_fields[1].default,
                type=settings_fields[1].type,
            ),
            # network and authentication
            settings.value(
                key=settings_fields[2].name,
                defaultValue=settings_fields[2].default,
                type=settings_fields[2].type,
            ),
            settings.value(
                key=settings_fields[3].name,
                defaultValue=settings_fields[3].default,
                type=settings_fields[3].type,
            ),
            settings.value(
                key=settings_fields[4].name,
                defaultValue=settings_fields[4].default,
                type=settings_fields[4].type,
            ),
            settings.value(
                key=settings_fields[5].name,
                defaultValue=settings_fields[5].default,
                type=settings_fields[5].type,
            ),
            settings.value(
                key=settings_fields[6].name,
                defaultValue=settings_fields[6].default,
                type=settings_fields[6].type,
            ),
            settings.value(
                key=settings_fields[7].name,
                defaultValue=settings_fields[7].default,
                type=settings_fields[7].type,
            ),
            settings.value(
                key=settings_fields[8].name,
                defaultValue=settings_fields[8].default,
                type=settings_fields[8].type,
            ),
            settings.value(
                key=settings_fields[9].name,
                defaultValue=settings_fields[9].default,
                type=settings_fields[9].type,
            ),
            settings.value(
                key=settings_fields[10].name,
                defaultValue=settings_fields[10].default,
                type=settings_fields[10].type,
            ),
            settings.value(
                key=settings_fields[11].name,
                defaultValue=settings_fields[11].default,
                type=settings_fields[11].type,
            ),
            settings.value(
                key=settings_fields[12].name,
                defaultValue=settings_fields[12].default,
                type=settings_fields[12].type,
            ),
            settings.value(
                key=settings_fields[13].name,
                defaultValue=settings_fields[13].default,
                type=settings_fields[13].type,
            ),
            settings.value(
                key=settings_fields[14].name,
                defaultValue=settings_fields[14].default,
                type=settings_fields[14].type,
            ),
            settings.value(
                key=settings_fields[15].name,
                defaultValue=settings_fields[15].default,
                type=settings_fields[15].type,
            ),
            settings.value(
                key=settings_fields[16].name,
                defaultValue=settings_fields[16].default,
                type=settings_fields[16].type,
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
            print(out_value)
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

        for k, v in asdict(plugin_settings_obj).items():
            cls.set_value_from_key(k, v)

        settings.endGroup()
