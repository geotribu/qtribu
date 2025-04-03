# standard

# 3rd party
from qgis.core import Qgis
from qgis.PyQt.QtCore import QT_VERSION_STR, QUrl
from qgis.PyQt.QtGui import QDesktopServices

# conditional import depending on Qt version
if int(QT_VERSION_STR.split(".")[0]) == 5:
    from qgis.PyQt.QtMultimedia import QMediaContent, QMediaPlayer  # noqa QGS103
elif int(QT_VERSION_STR.split(".")[0]) == 6:
    # see: https://doc.qt.io/qt-6/qtmultimedia-changes-qt6.html
    QMediaContent = QUrl
    from PyQt6.QtMultimedia import QMediaPlayer  # noqa QGS103
else:
    QMediaPlayer = None

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT

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


def play_resource_sound(resource: str, volume: int) -> None:
    """Play a sound inside QGIS.

    The file_name param must be the name (without extension) of a .mp3 audio file
    inside resources/sounds folder
    """
    file_path = DIR_PLUGIN_ROOT / f"resources/sounds/{resource}.mp3"
    if not file_path.exists():
        raise FileNotFoundError(
            f"File '{resource}.wav' not found in resources/sounds folder"
        )
    play_sound(f"{file_path.resolve()}", volume)


def play_sound(file: str, volume: int) -> None:
    """Play a sound using QtMultimedia QMediaPlayer."""
    url = QUrl.fromLocalFile(file)
    if QMediaPlayer is None:
        PlgLogger.log(
            message="QMediaPlayer is not available. Sound cannot be played.",
            log_level=Qgis.MessageLevel.Warning,
        )
        return

    # play sound
    player = QMediaPlayer()
    player.setMedia(QMediaContent(url))
    player.setVolume(volume)
    player.audioAvailableChanged.connect(lambda: player.play())
    player.play()
