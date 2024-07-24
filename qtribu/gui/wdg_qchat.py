# standard
import json
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Optional

# PyQGIS
#
from PyQt5 import QtWebSockets  # noqa QGS103
from qgis.core import Qgis, QgsApplication
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QBrush, QColor, QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QTreeWidgetItem, QWidget

from qtribu.__about__ import __title__
from qtribu.constants import (
    CHEATCODE_10OCLOCK,
    CHEATCODE_DIZZY,
    CHEATCODE_DONTCRYBABY,
    CHEATCODE_IAMAROBOT,
)
from qtribu.logic.qchat_client import QChatApiClient
from qtribu.tasks.dizzy import DizzyTask

# plugin
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.preferences import PlgSettingsStructure
from qtribu.utils import play_resource_sound

# -- GLOBALS --
MARKER_VALUE = "---"
DISPLAY_DATE_FORMAT = "%H:%M:%S"

ADMIN_MESSAGES_NICKNAME = "admin"
ADMIN_MESSAGES_COLOR = "#ffa500"
MENTION_MESSAGES_COLOR = "#00cc00"
USER_MESSAGES_COLOR = "#4169e1"


class QChatWidget(QgsDockWidget):

    connected: bool = False
    current_room: Optional[str] = None

    qchat_client = QChatApiClient

    def __init__(self, iface: QgisInterface, parent: QWidget = None):
        """QWidget to see and post messages on chat

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        self.iface = iface
        self.task_manager = QgsApplication.taskManager()
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # rules and status signal listener
        self.btn_rules.pressed.connect(self.on_rules_button_clicked)
        self.btn_rules.setIcon(QIcon(QgsApplication.iconPath("processingResult.svg")))
        self.btn_status.pressed.connect(self.on_status_button_clicked)
        self.btn_status.setIcon(QIcon(QgsApplication.iconPath("mIconInfo.svg")))

        # open settings signal listener
        self.btn_settings.pressed.connect(
            lambda: self.iface.showOptionsDialog(currentPage=f"mOptionsPage{__title__}")
        )
        self.btn_settings.setIcon(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg")
        )

        # widget opened / closed signals
        self.opened.connect(self.on_widget_opened)
        self.closed.connect(self.on_widget_closed)

        # connect signal listener
        self.connected = False
        self.btn_connect.pressed.connect(self.on_connect_button_clicked)
        self.btn_connect.setIcon(QIcon(QgsApplication.iconPath("mIconConnect.svg")))

        # tree widget initialization
        self.twg_chat.setHeaderLabels(
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
        self.lne_message.returnPressed.connect(self.on_send_button_clicked)
        self.btn_send.pressed.connect(self.on_send_button_clicked)
        self.btn_send.setIcon(
            QIcon(QgsApplication.iconPath("mActionDoubleArrowRight.svg"))
        )

    @property
    def settings(self) -> PlgSettingsStructure:
        return self.plg_settings.get_plg_settings()

    def load_settings(self) -> None:
        """Load options from QgsSettings into UI form."""
        self.lbl_instance.setText(self.settings.qchat_instance_uri)
        self.lbl_nickname.setText(self.settings.qchat_nickname)

    def on_widget_opened(self) -> None:
        """
        Action called when the widget is opened
        """

        # fill fields from saved settings
        self.load_settings()

        # initialize QChat API client
        self.qchat_client = QChatApiClient(self.settings.qchat_instance_uri)

        # clear rooms combobox items
        self.cbb_room.clear()  # delete all items from comboBox

        # load rooms
        self.cbb_room.addItem(MARKER_VALUE)
        try:
            rooms = self.qchat_client.get_rooms()
            for room in rooms:
                self.cbb_room.addItem(room)
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.Critical)
        finally:
            self.current_room = MARKER_VALUE

        self.cbb_room.currentIndexChanged.connect(self.on_room_changed)

    def on_rules_button_clicked(self) -> None:
        """
        Action called when clicking on "Rules" button
        """
        try:
            rules = self.qchat_client.get_rules()
            QMessageBox.information(
                self,
                self.tr("Instance rules"),
                self.tr("Instance rules ({instance_url}):\n\n{rules}").format(
                    instance_url=self.qchat_client.instance_uri, rules=rules["rules"]
                ),
            )
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.Critical)

    def on_status_button_clicked(self) -> None:
        """
        Action called when clicking on "Status" button
        """
        try:
            status = self.qchat_client.get_status()
            text = """Status: {status}

Rooms:
{rooms_status}""".format(
                status=status["status"],
                rooms_status="\n".join(
                    [
                        f"- {r['name']} : {r['nb_connected_users']} user{'s' if r['nb_connected_users'] > 1 else ''}"
                        for r in status["rooms"]
                    ]
                ),
            )
            QMessageBox.information(self, self.tr("QChat instance status"), text)
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.Critical)

    def on_room_changed(self) -> None:
        """
        Action called when room index is changed in the room combobox
        """
        old_room = self.current_room
        new_room = self.cbb_room.currentText()
        old_is_marker = old_room != MARKER_VALUE
        if new_room == MARKER_VALUE:
            if self.connected:
                self.disconnect_from_room(log=old_is_marker, close_ws=old_is_marker)
            self.current_room = MARKER_VALUE
            return
        if self.connected:
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
            room = self.cbb_room.currentText()
            if room == MARKER_VALUE:
                return
            self.connect_to_room(room)

    def connect_to_room(self, room: str, log: bool = True) -> None:
        """
        Connect widget to a specific room
        """
        if log:
            item = QTreeWidgetItem(
                [
                    room,
                    datetime.now().strftime(DISPLAY_DATE_FORMAT),
                    ADMIN_MESSAGES_NICKNAME,
                    self.tr("Connected to room '{room}'").format(room=room),
                ]
            )
            item.setForeground(0, QBrush(QColor(ADMIN_MESSAGES_COLOR)))
            self.twg_chat.insertTopLevelItem(0, item)

        protocol, domain = self.settings.qchat_instance_uri.split("://")
        ws_protocol = "wss" if protocol == "https" else "ws"
        ws_instance_url = f"{ws_protocol}://{domain}"
        ws_url = f"{ws_instance_url}/room/{room}/ws"
        self.ws_client.open(QUrl(ws_url))
        self.ws_client.connected.connect(partial(self.on_ws_connected, room))

    def on_ws_connected(self, room: str) -> None:
        """
        Action called when websocket is connected to a room
        """
        self.btn_connect.setText(self.tr("Disconnect"))
        self.lbl_status.setText("Connected")
        self.grb_user.setEnabled(True)
        self.current_room = room
        self.connected = True

    def disconnect_from_room(self, log: bool = True, close_ws: bool = True) -> None:
        """
        Disconnect widget from the current room
        """
        if log:
            item = QTreeWidgetItem(
                [
                    self.current_room,
                    datetime.now().strftime(DISPLAY_DATE_FORMAT),
                    ADMIN_MESSAGES_NICKNAME,
                    self.tr("Disconnected from room '{room}'").format(
                        room=self.current_room
                    ),
                ]
            )
            item.setForeground(0, QBrush(QColor(ADMIN_MESSAGES_COLOR)))
            self.twg_chat.insertTopLevelItem(0, item)
        self.btn_connect.setText(self.tr("Connect"))
        self.lbl_status.setText("Disconnected")
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
        self.lbl_status.setText("Disconnected")
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

        # check if a cheatcode is activated
        if self.settings.qchat_activate_cheatcode:
            activated = self.check_cheatcode(message)
            if activated:
                return

        # check if message mentions current user
        if f"@{self.settings.qchat_nickname}" in message["message"]:
            item = self.create_message_item(
                self.current_room, message, color=MENTION_MESSAGES_COLOR
            )
            self.log(
                message=self.tr("You were mentionned by {sender}: {message}").format(
                    sender=message["author"], message=message["message"]
                ),
                log_level=Qgis.Info,
                push=PlgOptionsManager().get_plg_settings().notify_push_info,
                duration=PlgOptionsManager().get_plg_settings().notify_push_duration,
            )
        elif message["author"] == self.settings.qchat_nickname:
            item = self.create_message_item(
                self.current_room, message, color=USER_MESSAGES_COLOR
            )
        else:
            item = self.create_message_item(self.current_room, message)
        self.twg_chat.insertTopLevelItem(0, item)

        # check if a notification sound should be played
        if self.settings.qchat_play_sounds:
            play_resource_sound(
                self.settings.qchat_ring_tone, self.settings.qchat_sound_volume
            )

    def on_clear_chat_button_clicked(self) -> None:
        """
        Action called when the clear chat button is clicked
        """
        self.twg_chat.clear()

    def on_send_button_clicked(self) -> None:
        """
        Action called when the send button is clicked
        """

        # retrieve nickname and message
        nickname = self.settings.qchat_nickname
        message_text = self.lne_message.text()

        if not nickname:
            self.log(
                message=self.tr("Nickname not set : please open settings and set it"),
                log_level=Qgis.Warning,
                push=PlgOptionsManager().get_plg_settings().notify_push_info,
                duration=PlgOptionsManager().get_plg_settings().notify_push_duration,
                button=True,
                button_label=self.tr("Open Settings"),
                button_connect=lambda: self.iface.showOptionsDialog(
                    currentPage=f"mOptionsPage{__title__}"
                ),
            )
            return

        if not message_text:
            return

        # send message to websocket
        message = {"message": message_text, "author": nickname}
        self.ws_client.sendTextMessage(json.dumps(message))
        self.lne_message.setText("")

    @staticmethod
    def create_message_item(
        room: str, message: dict[str, Any], color: str = None
    ) -> QTreeWidgetItem:
        """
        Creates a QTreeWidgetItem from a QChat message dict
        Optionally with a color given as hexa string
        """
        item = QTreeWidgetItem(
            [
                room,
                datetime.now().strftime(DISPLAY_DATE_FORMAT),
                message["author"],
                message["message"],
            ]
        )
        if color:
            item.setForeground(0, QBrush(QColor(color)))
        return item

    def on_widget_closed(self) -> None:
        """
        Action called when the widget is closed
        """
        if self.connected:
            self.disconnect_from_room()
        self.cbb_room.currentIndexChanged.disconnect()

    def check_cheatcode(self, message: dict[str, str]) -> bool:
        """
        Checks if a received message contains a cheatcode
        Does action if necessary
        Returns true if a cheatcode has been activated
        """
        msg = message["message"]

        # make QGIS shuffle for a few seconds
        if msg == CHEATCODE_DIZZY:
            task = DizzyTask(f"Cheatcode activation: {CHEATCODE_DIZZY}", self.iface)
            self.task_manager.addTask(task)
            return True

        # play sounds
        if self.settings.qchat_play_sounds:
            if msg in [CHEATCODE_DONTCRYBABY, CHEATCODE_IAMAROBOT, CHEATCODE_10OCLOCK]:
                play_resource_sound(msg, self.settings.qchat_sound_volume)
                return True
        return False
