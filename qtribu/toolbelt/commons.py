from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices


def open_url_in_browser(url: str) -> bool:
    """Opens an url in a browser using user's desktop environment

    :param url: url to open
    :type url: str

    :return: true if successful otherwise false
    :rtype: bool
    """
    return QDesktopServices.openUrl(QUrl(url))
