# standard
import dataclasses
import json
from json import JSONEncoder

# PyQGIS
from qgis.core import Qgis
from qgis.PyQt.QtCore import QT_VERSION_STR, QObject, QUrl, pyqtSignal

# plugin
from qtribu.constants import (
    QCHAT_MESSAGE_TYPE_BBOX,
    QCHAT_MESSAGE_TYPE_CRS,
    QCHAT_MESSAGE_TYPE_EXITER,
    QCHAT_MESSAGE_TYPE_GEOJSON,
    QCHAT_MESSAGE_TYPE_IMAGE,
    QCHAT_MESSAGE_TYPE_LIKE,
    QCHAT_MESSAGE_TYPE_NB_USERS,
    QCHAT_MESSAGE_TYPE_NEWCOMER,
    QCHAT_MESSAGE_TYPE_POSITION,
    QCHAT_MESSAGE_TYPE_TEXT,
    QCHAT_MESSAGE_TYPE_UNCOMPLIANT,
)
from qtribu.logic.qchat_messages import (
    QChatBboxMessage,
    QChatCrsMessage,
    QChatExiterMessage,
    QChatGeojsonMessage,
    QChatImageMessage,
    QChatLikeMessage,
    QChatMessage,
    QChatNbUsersMessage,
    QChatNewcomerMessage,
    QChatPositionMessage,
    QChatTextMessage,
    QChatUncompliantMessage,
)
from qtribu.toolbelt import PlgLogger
from qtribu.toolbelt.exceptions import QChatMessageCanNotBeParsedException

# conditional import depending on Qt version
if int(QT_VERSION_STR.split(".")[0]) == 5:
    from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol  # noqa QGS103

    wS_PROTOCOL_VERSION = QWebSocketProtocol.Version13
elif int(QT_VERSION_STR.split(".")[0]) == 6:
    from PyQt6.QtWebSockets import QWebSocket, QWebSocketProtocol  # noqa QGS103

    wS_PROTOCOL_VERSION = QWebSocketProtocol.Version.Version13

    print("QtWebSockets imported from PyQt6")
else:
    QWebSocket = None


class EnhancedJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder for dataclass objects
    """

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class QChatWebsocket(QObject):
    """Websocket wrapper for handling the QChat communications and messages."""

    # QChat status signals
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(int)
    # QChat message signals
    bbox_message_received = pyqtSignal(QChatBboxMessage)
    crs_message_received = pyqtSignal(QChatCrsMessage)
    exiter_message_received = pyqtSignal(QChatExiterMessage)
    geojson_message_received = pyqtSignal(QChatGeojsonMessage)
    image_message_received = pyqtSignal(QChatImageMessage)
    like_message_received = pyqtSignal(QChatLikeMessage)
    nb_users_message_received = pyqtSignal(QChatNbUsersMessage)
    newcomer_message_received = pyqtSignal(QChatNewcomerMessage)
    position_message_received = pyqtSignal(QChatPositionMessage)
    text_message_received = pyqtSignal(QChatTextMessage)
    uncompliant_message_received = pyqtSignal(QChatUncompliantMessage)

    def __init__(self):
        super().__init__()
        self.log = PlgLogger().log

        if QWebSocket is None:
            self.log(
                message="QtWebSockets module not found. Please install PyQt5 or PyQt6.",
                log_level=Qgis.MessageLevel.Critical,
            )
            return
        self.ws_client = QWebSocket("", wS_PROTOCOL_VERSION, None)
        self.ws_client.error.connect(lambda code: self.error.emit(code))
        self.ws_client.textMessageReceived.connect(self.on_message_received)

    def open(self, qchat_instance_uri: str, room: str) -> None:
        """Opens a websocket to a QChat instance.

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
        """Closes a websocket connection."""
        self.ws_client.connected.disconnect()
        self.ws_client.close()

    def send_message(self, message: QChatMessage) -> None:
        """Sends a QChat message to the websocket."""
        self.ws_client.sendTextMessage(json.dumps(message, cls=EnhancedJSONEncoder))

    def error_string(self) -> str:
        """Returns the websocket error string if there is any."""
        return self.ws_client.errorString()

    def on_message_received(self, text: str) -> None:
        """Launched when a text message is received from the websocket.

        :param text: text message received, should be a jsonified string
        """
        message = json.loads(text)
        if "type" not in message:
            self.log(
                message="No 'type' key in received message. Please make sure your configured instance is running gischat v>=2.0.0",
                log_level=Qgis.MessageLevel.Critical,
            )
            return
        msg_type = message["type"]
        try:
            if msg_type == QCHAT_MESSAGE_TYPE_UNCOMPLIANT:
                self.uncompliant_message_received.emit(
                    QChatUncompliantMessage(**message)
                )
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
            elif msg_type == QCHAT_MESSAGE_TYPE_CRS:
                self.crs_message_received.emit(QChatCrsMessage(**message))
            elif msg_type == QCHAT_MESSAGE_TYPE_BBOX:
                self.bbox_message_received.emit(QChatBboxMessage(**message))
            elif msg_type == QCHAT_MESSAGE_TYPE_POSITION:
                self.position_message_received.emit(QChatPositionMessage(**message))
        except KeyError:
            text = self.tr(
                "Unintelligible message received. Please make sure you are using the latest plugin version. (type={type})"
            ).format(type=msg_type)
            message = QChatUncompliantMessage(reason=text)
            self.uncompliant_message_received.emit(message)
            raise QChatMessageCanNotBeParsedException(message=text)
