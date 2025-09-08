# standard

# 3rd party
from qgis.core import Qgis
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices

try:
    from qtribu.logic.web_viewer import WebViewer

    web_viewer = WebViewer()
except ImportError:
    web_viewer = None

from qtribu.toolbelt.log_handler import PlgLogger
from qtribu.toolbelt.preferences import PlgOptionsManager


def open_url_in_browser(url: str) -> bool:
    """Opens an url in a browser using user's desktop environment.

    :param url: url to open
    :type url: str

    :return: true if successful otherwise false
    :rtype: bool
    """
    return QDesktopServices.openUrl(QUrl(url))


def open_url_in_webviewer(url: str, window_title: str) -> None:
    """Opens an url in Geotribu's webviewer.

    :param url: url to open
    :type url: str
    :param window_title: title to give to the webviewer window
    :type window_title: str
    """
    if web_viewer is None and PlgOptionsManager().get_plg_settings().browser == 1:
        PlgLogger.log(
            message="The embedded webviewer is not avaible, probably because "
            "of unfilled system dependencies (QtWebEngine). Using default system "
            "browser as fallback.",
            log_level=Qgis.MessageLevel.Critical,
        )
        open_url_in_browser(url=url)
        return

    if isinstance(web_viewer, WebViewer):
        web_viewer.display_web_page(url)
        if web_viewer.wdg_web:
            web_viewer.set_window_title(window_title)
