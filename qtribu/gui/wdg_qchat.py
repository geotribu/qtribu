# standard
import json
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any

# PyQGIS
#
from PyQt5 import QtWebSockets  # noqa QGS103
from qgis.core import QgsApplication
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QTreeWidgetItem, QWidget

from qtribu.constants import CHEATCODE_DIZZY
from qtribu.logic.qchat_client import QChatApiClient
from qtribu.tasks.dizzy import DizzyTask

# plugin
from qtribu.toolbelt import PlgLogger, PlgOptionsManager

# -- GLOBALS --
MARKER_VALUE = "---"
DISPLAY_DATE_FORMAT = "%H:%M:%S"


class QChatWidget(QgsDockWidget):
    def __init__(self, iface: QgisInterface, parent: QWidget = None):
        """QWidget to see and post messages on chat

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        self.iface = iface
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # fill fields from saved settings
        self.settings = self.plg_settings.get_plg_settings()
        self.load_settings()

        # initialize QChat API client
        self.qchat_client = QChatApiClient(self.settings.qchat_instance_uri)

        # load rooms
        rooms = self.qchat_client.get_rooms()
        self.cb_room.addItem(MARKER_VALUE)
        for room in rooms:
            self.cb_room.addItem(room)
        self.current_room = MARKER_VALUE

        self.cb_room.currentIndexChanged.connect(self.on_room_changed)

        # connect signal listener
        self.connected = False
        self.btn_connect.pressed.connect(self.on_connect_button_clicked)
        self.btn_connect.setIcon(QIcon(QgsApplication.iconPath("mIconConnect.svg")))

        # tree widget initialization
        self.tw_chat.setHeaderLabels(
            [
                self.tr("Room"),
                self.tr("Date"),
                self.tr("Nickname"),
                self.tr("Message"),
            ]
        )

        # clear chat signal listener
        self.btn_clear_chat.pressed.connect(self.on_clear_chat_button_clicked)
        self.btn_clear_chat.setIcon(
            QIcon(QgsApplication.iconPath("mActionDeleteSelectedFeatures.svg"))
        )

        # initialize websocket client
        self.ws_client = QtWebSockets.QWebSocket(
            "", QtWebSockets.QWebSocketProtocol.Version13, None
        )
        self.ws_client.textMessageReceived.connect(self.on_ws_message_received)

        # send message signal listener
        self.le_message.returnPressed.connect(self.on_send_button_clicked)
        self.btn_send.pressed.connect(self.on_send_button_clicked)
        self.btn_send.setIcon(
            QIcon(QgsApplication.iconPath("mActionDoubleArrowRight.svg"))
        )

    def load_settings(self) -> None:
        """Load options from QgsSettings into UI form."""
        self.lb_instance.setText(self.settings.qchat_instance_uri)
        self.le_nickname.setText(self.settings.qchat_nickname)

    def save_settings(self) -> None:
        """Save form text into QgsSettings."""
        self.settings.qchat_nickname = self.le_nickname.text()
        self.plg_settings.save_from_object(self.settings)

    def on_room_changed(self) -> None:
        """
        Action called when room index is changed in the room combobox
        """
        old_room = self.current_room
        new_room = self.cb_room.currentText()
        old_is_marker = old_room != MARKER_VALUE
        if new_room == MARKER_VALUE:
            if self.connected:
                self.disconnect_from_room(log=old_is_marker, close_ws=old_is_marker)
            self.current_room = MARKER_VALUE
            return
        self.disconnect_from_room(log=old_is_marker, close_ws=old_is_marker)
        self.connect_to_room(new_room)
        self.current_room = new_room

    def on_connect_button_clicked(self) -> None:
        """
        Action called when clicking on "Connect" / "Disconnect" button
        """
        if self.connected:
            self.disconnect_from_room()
        else:
            room = self.cb_room.currentText()
            if room == MARKER_VALUE:
                return
            self.connect_to_room(room)

    def connect_to_room(self, room: str, log: bool = True) -> None:
        """
        Connect widget to a specific room
        """
        if log:
            self.tw_chat.insertTopLevelItem(
                0,
                QTreeWidgetItem(
                    [
                        room,
                        datetime.now().strftime(DISPLAY_DATE_FORMAT),
                        self.tr("Admin"),
                        self.tr("Connected to room '{room}'").format(room=room),
                    ]
                ),
            )

        ws_instance_url = "ws://" + self.settings.qchat_instance_uri.split("://")[-1]
        ws_url = f"{ws_instance_url}/room/{room}/ws"
        self.ws_client.open(QUrl(ws_url))
        self.ws_client.connected.connect(partial(self.on_ws_connected, room))

    def on_ws_connected(self, room: str) -> None:
        """
        Action called when websocket is connected to a room
        """
        self.btn_connect.setText(self.tr("Disconnect"))
        self.lb_status.setText("Connected")
        self.grb_user.setEnabled(True)
        self.current_room = room
        self.connected = True

    def disconnect_from_room(self, log: bool = True, close_ws: bool = True) -> None:
        """
        Disconnect widget from the current room
        """
        if log:
            self.tw_chat.insertTopLevelItem(
                0,
                QTreeWidgetItem(
                    [
                        self.current_room,
                        datetime.now().strftime(DISPLAY_DATE_FORMAT),
                        self.tr("Admin"),
                        self.tr("Disconnected from room '{room}'").format(
                            room=self.current_room
                        ),
                    ]
                ),
            )
        self.btn_connect.setText(self.tr("Connect"))
        self.lb_status.setText("Disconnected")
        self.grb_user.setEnabled(False)
        self.connected = False
        if close_ws:
            self.ws_client.connected.disconnect()
            self.ws_client.close()

    def on_ws_disconnected(self) -> None:
        """
        Action called when websocket is disconnected
        """
        self.btn_connect.setText(self.tr("Connect"))
        self.lb_status.setText("Disconnected")
        self.grb_user.setEnabled(False)
        self.connected = False

    def on_ws_error(self, error_code: int) -> None:
        """
        Action called when an error appears on the websocket
        """
        QTreeWidgetItem(
            [
                "ERROR",
                datetime.now().strftime(DISPLAY_DATE_FORMAT),
                self.tr("Admin"),
                self.ws_client.errorString(),
            ]
        ),

    def on_ws_message_received(self, message: str) -> None:
        """
        Action called when a message is received from the websocket
        """
        message = json.loads(message)
        if message["message"] == CHEATCODE_DIZZY:
            task = DizzyTask("Cheatcode activation", self.iface)
            QgsApplication.taskManager().addTask(task)
            return
        self.tw_chat.insertTopLevelItem(
            0, self.add_message_to_treeview(self.current_room, message)
        )

    def on_clear_chat_button_clicked(self) -> None:
        """
        Action called when the clear chat button is clicked
        """
        self.tw_chat.clear()

    def on_send_button_clicked(self) -> None:
        """
        Action called when the send button is clicked
        """

        # retrieve nickname and message
        nickname = self.le_nickname.text()
        message_text = self.le_message.text()

        # check if nickname and message are correctly filled
        if not nickname or not message_text:
            QMessageBox.warning(
                self,
                self.tr("Impossible"),
                self.tr("Nickname and message boxes must be filled"),
            )
            return

        # send message to websocket
        message = {"message": message_text, "author": nickname}
        self.ws_client.sendTextMessage(json.dumps(message))
        self.le_message.setText("")
        self.save_settings()

    def add_message_to_treeview(
        self, room: str, message: dict[str, Any]
    ) -> QTreeWidgetItem:
        """
        Creates a QTreeWidgetItem from a QChat message dict
        """
        item = QTreeWidgetItem(
            [
                room,
                datetime.now().strftime("%H:%M:%S"),
                message["author"],
                message["message"],
            ]
        )
        return item
