from qgis.PyQt.QtCore import QDesktopServices, QUrl


def open_url_in_browser(url: str) -> bool:
    return QDesktopServices.openUrl(QUrl(url))
