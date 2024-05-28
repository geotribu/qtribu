from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices

from qtribu.logic import WebViewer

web_viewer = WebViewer()


def open_url_in_browser(url: str) -> bool:
    """Opens an url in a browser using user's desktop environment

    :param url: url to open
    :type url: str

    :return: true if successful otherwise false
    :rtype: bool
    """
    return QDesktopServices.openUrl(QUrl(url))


def open_url_in_webviewer(url: str, window_title: str) -> None:
    """Opens an url in Geotribu's webviewer

    :param url: url to open
    :type url: str

    :param window_title: title to give to the webviewer window
    :type window_title: str
    """
    web_viewer.display_web_page(url)
    if web_viewer.wdg_web:
        web_viewer.set_window_title(window_title)
