#! python3  # noqa: E265

# standard library
import logging
from functools import partial
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional

# PyQGIS
from qgis.core import QgsMessageLog, QgsMessageOutput
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtWidgets import QPushButton, QWidget
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
        duration: Optional[int] = None,
        # widget
        button: bool = False,
        button_label: Optional[str] = None,
        button_more_text: Optional[str] = None,
        button_connect: Optional[Callable] = None,
        # parent
        parent_location: Optional[QWidget] = None,
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
        :param button: display a button in the message bar. Defaults to False.
        :type button: bool, optional
        :param button_label: text label of the button. Defaults to None.
        :type button_label: str, optional
        :param button_more_text: text to display within the QgsMessageOutput
        :type button_more_text: str, optional
        :param button_connect: function to be called when the button is pressed. \
        If not set, a simple dialog (QgsMessageOutput) is used to dislay the message. \
        Defaults to None.
        :type button_connect: Callable, optional
        :param parent_location: parent location widget. \
        If not set, QGIS canvas message bar is used to push message, \
        otherwise if a QgsMessageBar is available in parent_location it is used instead. \
        Defaults to None.
        :type parent_location: Widget, optional

        :Example:

        .. code-block:: python

            log(message="Plugin loaded - INFO", log_level=0, push=False)
            log(message="Plugin loaded - WARNING", log_level=1, push=1, duration=5)
            log(message="Plugin loaded - ERROR", log_level=2, push=1, duration=0)
            log(
                message="Plugin loaded - SUCCESS",
                log_level=3,
                push=1,
                duration=10,
                button=True
            )
            log(
                message="Plugin loaded",
                log_level=2,
                push=1,
                duration=0
                button=True,
                button_label=self.tr("See details"),
                button_more_text=detailed_error_message
            )
            log(message="Plugin loaded - TEST", log_level=4, push=0)

            # also works using enums from Qgis:
            # Qgis.Info, Qgis.Warning, Qgis.Critical, Qgis.Success, Qgis.NoLevel
            from qgis.core import Qgis
            log(
                message="Something went wrong but it's not blocking",
                log_level=Qgis.Warning
            )

        """
        # if not debug mode and not push, let's ignore INFO, SUCCESS and TEST
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
        if push and iface is not None:
            msg_bar = None

            # QGIS or custom dialog
            if parent_location and isinstance(parent_location, QWidget):
                msg_bar = parent_location.findChild(QgsMessageBar)

            if not msg_bar:
                msg_bar = iface.messageBar()

            # calc duration
            if duration is None:
                duration = (log_level + 1) * 3

            # create message with/out a widget
            if button:
                # create output message
                notification = iface.messageBar().createMessage(
                    title=application, text=message
                )
                widget_button = QPushButton(button_label or "More...")
                if button_connect:
                    widget_button.clicked.connect(button_connect)
                else:
                    mini_dlg = QgsMessageOutput.createMessageOutput()
                    mini_dlg.setTitle(application)
                    mini_dlg.setMessage(
                        f"{message}\n{button_more_text}", QgsMessageOutput.MessageText
                    )
                    widget_button.clicked.connect(partial(mini_dlg.showMessage, False))

                notification.layout().addWidget(widget_button)
                msg_bar.pushWidget(
                    widget=notification, level=log_level, duration=duration
                )

            else:
                # send simple message
                msg_bar.pushMessage(
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
