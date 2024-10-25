import dataclasses
import json
from json import JSONEncoder

from PyQt5 import QtWebSockets  # noqa QGS103
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal

from qtribu.logic.qchat_messages import (
    QChatExiterMessage,
    QChatImageMessage,
    QChatLikeMessage,
    QChatMessage,
    QChatNbUsersMessage,
    QChatNewcomerMessage,
    QChatTextMessage,
)
from qtribu.toolbelt import PlgLogger


class EnhancedJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder for dataclass objects
    """

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class QChatWebsocket(QObject):

    def __init__(self):
        super().__init__()
        self.log = PlgLogger().log

        self.ws_client = QtWebSockets.QWebSocket(
            "", QtWebSockets.QWebSocketProtocol.Version13, None
        )
        self.ws_client.error.connect(lambda code: self.error.emit(code))
        self.ws_client.textMessageReceived.connect(self.on_message_received)

    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(int)

    text_message_received = pyqtSignal(QChatTextMessage)
    image_message_received = pyqtSignal(QChatImageMessage)
    nb_users_message_received = pyqtSignal(QChatNbUsersMessage)
    newcomer_message_received = pyqtSignal(QChatNewcomerMessage)
    exiter_message_received = pyqtSignal(QChatExiterMessage)
    like_message_received = pyqtSignal(QChatLikeMessage)

    def open(self, qchat_instance_uri: str, room: str) -> None:
        protocol, domain = qchat_instance_uri.split("://")
        ws_protocol = "wss" if protocol == "https" else "ws"
        ws_instance_url = f"{ws_protocol}://{domain}"
        ws_url = f"{ws_instance_url}/room/{room}/ws"
        self.ws_client.open(QUrl(ws_url))
        self.ws_client.connected.connect(self.connected.emit)

    def close(self) -> None:
        self.ws_client.connected.disconnect()
        self.ws_client.close()

    def send_message(self, message: QChatMessage) -> None:
        self.ws_client.sendTextMessage(json.dumps(message, cls=EnhancedJSONEncoder))

    def error_string(self) -> str:
        return self.ws_client.errorString()

    def on_message_received(self, text: str) -> None:
        message = json.loads(text)
        msg_type = message["type"]
        if msg_type == "text":
            self.text_message_received.emit(QChatTextMessage(**message))
        elif msg_type == "image":
            self.image_message_received.emit(QChatImageMessage(**message))
        elif msg_type == "nb_users":
            self.nb_users_message_received.emit(QChatNbUsersMessage(**message))
        elif msg_type == "newcomer":
            self.newcomer_message_received.emit(QChatNewcomerMessage(**message))
        elif msg_type == "exiter":
            self.exiter_message_received.emit(QChatExiterMessage(**message))
        elif msg_type == "like":
            self.like_message_received.emit(QChatLikeMessage(**message))
