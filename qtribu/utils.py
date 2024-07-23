import os

from PyQt5 import QtMultimedia  # noqa QGS103
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound  # noqa QGS103
from qgis.PyQt.QtCore import QUrl

from qtribu.__about__ import DIR_PLUGIN_ROOT


def play_resource_sound(resource: str, volume: int) -> None:
    """
    Play a sound inside QGIS
    The file_name param must be the name (without extension) of a .ogg audio file inside resources/sounds folder
    """
    file_path = str(DIR_PLUGIN_ROOT / f"resources/sounds/{resource}.ogg")
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File '{resource}.wav' not found in resources/sounds folder"
        )
    play_sound(file_path, volume)


def play_sound(file: str, volume: int) -> None:
    """
    Play a sound using QTMultimedia QMediaPlayer
    """
    url = QUrl.fromLocalFile(file)
    player = QMediaPlayer()
    player.setMedia(QMediaContent(url))
    player.setVolume(volume)
    player.audioAvailableChanged.connect(lambda: player.play())
    player.play()
