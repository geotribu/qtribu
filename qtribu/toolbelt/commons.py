from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices


def open_url_in_browser(url: str) -> bool:
    return QDesktopServices.openUrl(QUrl(url))
