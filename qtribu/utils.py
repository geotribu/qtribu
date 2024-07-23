from PyQt5 import QtMultimedia  # noqa QGS103
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound  # noqa QGS103
from qgis.PyQt.QtCore import QUrl


def play_sound(file: str) -> None:
    """
    Play a sound using QSound object
    """
    QSound.play(file)


def play_sound_media(file: str) -> None:
    """
    Play a sound using QTMultimedia QMediaPlayer
    """
    url = QUrl.fromLocalFile(file)
    player = QMediaPlayer()
    player.setMedia(QMediaContent(url))
    player.setVolume(100)
    player.audioAvailableChanged.connect(lambda: player.play())
    player.play()
