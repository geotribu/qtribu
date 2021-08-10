#! python3  # noqa: E265

# standard library
import logging
from logging.handlers import RotatingFileHandler

# PyQGIS
from qgis.core import QgsMessageLog
from qgis.utils import iface

# project package
import qtribu.toolbelt.preferences as plg_prefs_hdlr
from qtribu.__about__ import DIR_PLUGIN_ROOT, __title__, __title_clean__

# ############################################################################
# ########## Classes ###############
# ##################################


class PlgLogger(logging.Handler):
    """Python logging handler supercharged with QGIS useful methods."""

    @staticmethod
    def log(
        message: str,
        application: str = __title__,
        log_level: int = 0,
        push: bool = False,
        duration: int = None,
    ):
        """Send messages to QGIS messages windows and to the user as a message bar. \
        Plugin name is used as title. If debug mode is disabled, only warnings (1) and \
        errors (2) or with push are sent.

        :param message: message to display
        :type message: str
        :param application: name of the application sending the message. \
        Defaults to __about__.__title__
        :type application: str, optional
        :param log_level: message level. Possible values: 0 (info), 1 (warning), \
        2 (critical), 3 (success), 4 (none - grey). Defaults to 0 (info)
        :type log_level: int, optional
        :param push: also display the message in the QGIS message bar in addition to \
        the log, defaults to False
        :type push: bool, optional
        :param duration: duration of the message in seconds. If not set, the \
        duration is calculated from the log level: `(log_level + 1) * 3`. seconds. \
        If set to 0, then the message must be manually dismissed by the user. \
        Defaults to None.
        :type duration: int, optional

        :Example:

        .. code-block:: python

            log(message="Plugin loaded - INFO", log_level=0, push=1)
            log(message="Plugin loaded - WARNING", log_level=1, push=1)
            log(message="Plugin loaded - ERROR", log_level=2, push=1)
            log(message="Plugin loaded - SUCCESS", log_level=3, push=1)
            log(message="Plugin loaded - TEST", log_level=4, push=1)
        """
        # if debug mode, let's ignore INFO, SUCCESS and TEST
        debug_mode = plg_prefs_hdlr.PlgOptionsManager.get_plg_settings().debug_mode
        if not debug_mode and not push and (log_level < 1 or log_level > 2):
            return

        # ensure message is a string
        if not isinstance(message, str):
            try:
                message = str(message)
            except Exception as err:
                err_msg = "Log message must be a string, not: {}. Trace: {}".format(
                    type(message), err
                )
                logging.error(err_msg)
                message = err_msg

        # send it to QGIS messages panel
        QgsMessageLog.logMessage(
            message=message, tag=application, notifyUser=push, level=log_level
        )

        # optionally, display message on QGIS Message bar (above the map canvas)
        if push:
            # calc duration
            if not duration:
                duration = (log_level + 1) * 3

            # send it
            iface.messageBar().pushMessage(
                title=application,
                text=message,
                level=log_level,
                duration=duration,
            )

    def set_logger(self):

        # create logger
        logger = logging.getLogger(__title_clean__)
        logging.captureWarnings(True)
        log_form = logging.Formatter(
            "%(asctime)s || %(levelname)s "
            "|| %(module)s - %(lineno)d ||"
            " %(funcName)s || %(message)s"
        )

        # if debug, add rotating file
        debug_mode = plg_prefs_hdlr.PlgOptionsManager.get_plg_settings().debug_mode
        if debug_mode:
            log_level = logging.DEBUG
            logfile_path = DIR_PLUGIN_ROOT / f"log_{__title_clean__}.log"
            logfile = RotatingFileHandler(logfile_path, "a", 5000000, 1)
            logfile.setLevel(log_level)
            logfile.setFormatter(log_form)
            logger.addHandler(logfile)
        else:
            log_level = logging.WARNING

        logger.setLevel(log_level)

        return logger
