import dataclasses
import json
from json import JSONEncoder

from PyQt5 import QtWebSockets  # noqa QGS103
from qgis.core import Qgis
from qgis.PyQt.QtCore import QObject, QUrl, pyqtSignal

from qtribu.constants import (
    QCHAT_MESSAGE_TYPE_EXITER,
    QCHAT_MESSAGE_TYPE_GEOJSON,
    QCHAT_MESSAGE_TYPE_IMAGE,
    QCHAT_MESSAGE_TYPE_LIKE,
    QCHAT_MESSAGE_TYPE_NB_USERS,
    QCHAT_MESSAGE_TYPE_NEWCOMER,
    QCHAT_MESSAGE_TYPE_TEXT,
    QCHAT_MESSAGE_TYPE_UNCOMPLIANT,
)
from qtribu.logic.qchat_messages import (
    QChatExiterMessage,
    QChatGeojsonMessage,
    QChatImageMessage,
    QChatLikeMessage,
    QChatMessage,
    QChatNbUsersMessage,
    QChatNewcomerMessage,
    QChatTextMessage,
    QChatUncompliantMessage,
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
    """
    Websocket wrapper for handling the QChat communications and messages
    """

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

    # QChat message signals
    uncompliant_message_received = pyqtSignal(QChatUncompliantMessage)
    text_message_received = pyqtSignal(QChatTextMessage)
    image_message_received = pyqtSignal(QChatImageMessage)
    nb_users_message_received = pyqtSignal(QChatNbUsersMessage)
    newcomer_message_received = pyqtSignal(QChatNewcomerMessage)
    exiter_message_received = pyqtSignal(QChatExiterMessage)
    like_message_received = pyqtSignal(QChatLikeMessage)
    geojson_message_received = pyqtSignal(QChatGeojsonMessage)

    def open(self, qchat_instance_uri: str, room: str) -> None:
        """
        Opens a websocket to a QChat instance
        :param qchat_instance_uri: URI of the QChat instance to connect to
        :param room: room to connect to
        """
        protocol, domain = qchat_instance_uri.split("://")
        ws_protocol = "wss" if protocol == "https" else "ws"
        ws_instance_url = f"{ws_protocol}://{domain}"
        ws_url = f"{ws_instance_url}/room/{room}/ws"
        self.ws_client.open(QUrl(ws_url))
        self.ws_client.connected.connect(self.connected.emit)

    def close(self) -> None:
        """
        Closes a websocket connection
        """
        self.ws_client.connected.disconnect()
        self.ws_client.close()

    def send_message(self, message: QChatMessage) -> None:
        """
        Sends a QChat message to the websocket
        """
        self.ws_client.sendTextMessage(json.dumps(message, cls=EnhancedJSONEncoder))

    def error_string(self) -> str:
        """
        Returns the websocket error string if there is any
        """
        return self.ws_client.errorString()

    def on_message_received(self, text: str) -> None:
        """
        Launched when a text message is received from the websocket
        :param text: text message received, should be a jsonified string
        """
        message = json.loads(text)
        if "type" not in message:
            self.log(
                message="No 'type' key in received message. Please make sure your configured instance is running gischat v>=2.0.0",
                log_level=Qgis.Critical,
            )
            return
        msg_type = message["type"]
        if msg_type == QCHAT_MESSAGE_TYPE_UNCOMPLIANT:
            self.uncompliant_message_received.emit(QChatUncompliantMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_TEXT:
            self.text_message_received.emit(QChatTextMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_IMAGE:
            self.image_message_received.emit(QChatImageMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_NB_USERS:
            self.nb_users_message_received.emit(QChatNbUsersMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_NEWCOMER:
            self.newcomer_message_received.emit(QChatNewcomerMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_EXITER:
            self.exiter_message_received.emit(QChatExiterMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_LIKE:
            self.like_message_received.emit(QChatLikeMessage(**message))
        elif msg_type == QCHAT_MESSAGE_TYPE_GEOJSON:
            self.geojson_message_received.emit(QChatGeojsonMessage(**message))
