from PyQt5 import QtMultimedia  # noqa QGS103
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound  # noqa QGS103
from qgis.PyQt.QtCore import QUrl


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
