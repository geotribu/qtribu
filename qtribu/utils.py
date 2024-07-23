from PyQt5 import QtMultimedia  # noqa QGS103
from PyQt5.QtMultimedia import QSound  # noqa QGS103
from qgis.PyQt.QtCore import QUrl


def play_sound(file: str) -> None:
    """
    Play a sound using QSound object
    """
    QSound.play(file)


def play_soundmedia(file: str) -> None:
    """
    Play a sound using QTMultimedia QMediaPlayer
    """
    url = QUrl.fromLocalFile(file)
    content = QtMultimedia.QMediaContent(url)
    player = QtMultimedia.QMediaPlayer()
    player.setMedia(content)
    player.play()
