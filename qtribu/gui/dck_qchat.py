# standard
import json
from functools import partial
from pathlib import Path
from typing import Any, Optional

# PyQGIS
from PyQt5 import QtWebSockets  # noqa QGS103
from qgis.core import Qgis, QgsApplication
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QPoint, Qt, QTime, QUrl
from qgis.PyQt.QtGui import QBrush, QColor, QCursor, QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QMessageBox, QTreeWidgetItem, QWidget

from qtribu.__about__ import __title__
from qtribu.constants import (
    ADMIN_MESSAGES_AVATAR,
    ADMIN_MESSAGES_NICKNAME,
    CHEATCODE_10OCLOCK,
    CHEATCODE_DIZZY,
    CHEATCODE_DONTCRYBABY,
    CHEATCODE_IAMAROBOT,
    CHEATCODE_QGIS_PRO_LICENSE,
    CHEATCODES,
    INTERNAL_MESSAGE_AUTHOR,
    QCHAT_NICKNAME_MINLENGTH,
)
from qtribu.logic.qchat_client import QChatApiClient
from qtribu.tasks.dizzy import DizzyTask

# plugin
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_webviewer, play_resource_sound
from qtribu.toolbelt.preferences import PlgSettingsStructure

# -- GLOBALS --
MARKER_VALUE = "---"


class QChatWidget(QgsDockWidget):

    initialized: bool = False
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
        self.btn_settings.pressed.connect(self.on_settings_button_clicked)
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
                self.tr("Date"),
                self.tr("Nickname"),
                self.tr("Message"),
            ]
        )
        self.twg_chat.itemDoubleClicked.connect(self.on_message_double_clicked)
        self.twg_chat.setContextMenuPolicy(Qt.CustomContextMenu)
        self.twg_chat.customContextMenuRequested.connect(
            self.on_custom_context_menu_requested
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
        self.ws_client.error.connect(self.on_ws_error)
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
        self.grb_instance.setTitle(
            self.tr("Instance: {uri}").format(uri=self.settings.qchat_instance_uri)
        )
        self.lbl_nickname.setText(self.settings.author_nickname)
        self.btn_send.setIcon(
            QIcon(QgsApplication.iconPath(self.settings.author_avatar))
        )

    def on_widget_opened(self) -> None:
        """
        Action called when the widget is opened
        """

        # hack to bypass multiple widget opened triggers when moving widget
        if self.initialized:
            return
        self.initialized = True

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
                self.tr(
                    """Instance rules ({instance_url}):

{rules}

Main language: {main_lang}
Max message length: {max_message_length}
Min nickname length: {min_nickname_length}
Max nickname length: {max_nickname_length}"""
                ).format(
                    instance_url=self.qchat_client.instance_uri,
                    rules=rules["rules"],
                    main_lang=rules["main_lang"],
                    max_message_length=rules["max_message_length"],
                    min_nickname_length=rules["min_author_length"],
                    max_nickname_length=rules["max_author_length"],
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
            user_txt = self.tr("user")
            text = self.tr(
                """Status: {status}

Rooms:

{rooms_status}"""
            ).format(
                status=status["status"],
                rooms_status="\n".join(
                    [
                        f"- {r['name']} : {r['nb_connected_users']} {user_txt}{'s' if r['nb_connected_users'] > 1 else ''}"
                        for r in status["rooms"]
                    ]
                ),
            )
            QMessageBox.information(self, self.tr("QChat instance status"), text)
        except Exception as exc:
            self.log(message=str(exc), log_level=Qgis.Critical)

    def on_settings_button_clicked(self) -> None:
        """
        Action called when clicking on "Settings" button
        """
        # save current instance and nickname to check afterwards if they have changed
        old_instance = self.settings.qchat_instance_uri
        old_nickname = self.settings.author_nickname
        self.iface.showOptionsDialog(currentPage=f"mOptionsPage{__title__}")

        # get new instance and nickname settings
        new_instance = self.settings.qchat_instance_uri
        new_nickname = self.settings.author_nickname

        # disconnect if instance or nickname have changed
        if old_instance != new_instance or old_nickname != new_nickname:
            self.disconnect_from_room(log=self.connected, close_ws=self.connected)
            self.on_widget_closed()
            self.on_widget_opened()

        # reload settings
        self.load_settings()

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

    def connect_to_room(self, room: str) -> None:
        """
        Connect widget to a specific room
        """
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
        self.grb_room.setTitle(self.tr("Room: {room}").format(room=room))
        self.grb_user.setEnabled(True)
        self.current_room = room
        self.connected = True
        self.log(message=f"Websocket connected to room {room}")
        if self.settings.qchat_display_admin_messages:
            self.add_admin_message(
                self.tr("Connected to room '{room}'").format(room=room)
            )

    def disconnect_from_room(self, log: bool = True, close_ws: bool = True) -> None:
        """
        Disconnect widget from the current room
        """
        if log and self.settings.qchat_display_admin_messages:
            self.add_admin_message(
                self.tr("Disconnected from room '{room}'").format(
                    room=self.current_room
                ),
            )
        self.btn_connect.setText(self.tr("Connect"))
        self.lbl_status.setText("Disconnected")
        self.grb_room.setTitle(self.tr("Room"))
        self.grb_qchat.setTitle(self.tr("QChat"))
        self.grb_user.setEnabled(False)
        self.connected = False
        if close_ws:
            self.ws_client.connected.disconnect()
            self.ws_client.close()

    def on_ws_disconnected(self) -> None:
        """
        Action called when websocket is disconnected
        """
        self.connected = False
        self.log(message="Websocket disconnected")

    def on_ws_error(self, error_code: int) -> None:
        """
        Action called when an error appears on the websocket
        """
        if self.settings.qchat_display_admin_messages:
            self.add_admin_message(self.ws_client.errorString())
        self.log(
            message=f"{error_code}: {self.ws_client.errorString()}",
            log_level=Qgis.Critical,
        )

    def on_ws_message_received(self, message: str) -> None:
        """
        Action called when a message is received from the websocket
        """
        message = json.loads(message)

        # check if this is an internal message
        if message["author"] == INTERNAL_MESSAGE_AUTHOR:
            self.handle_internal_message(message)
            return

        self.log(
            message=f"Message received: [{message['author']}]: '{message['message']}'"
        )

        # check if a cheatcode is activated
        if self.settings.qchat_activate_cheatcode:
            activated = self.check_cheatcode(message)
            if activated:
                return

        # do not display cheatcodes
        if message["message"] in CHEATCODES:
            return

        # check if message mentions current user
        words = message["message"].split(" ")
        if f"@{self.settings.author_nickname}" in words or "@all" in words:
            item = self.create_message_item(
                message["author"],
                message["avatar"],
                message["message"],
                foreground_color=self.settings.qchat_color_mention,
            )
            if message["author"] != self.settings.author_nickname:
                self.log(
                    message=self.tr(
                        "You were mentionned by {sender}: {message}"
                    ).format(sender=message["author"], message=message["message"]),
                    application=self.tr("QChat"),
                    log_level=Qgis.Info,
                    push=PlgOptionsManager().get_plg_settings().notify_push_info,
                    duration=PlgOptionsManager()
                    .get_plg_settings()
                    .notify_push_duration,
                )

                # check if a notification sound should be played
                if self.settings.qchat_play_sounds:
                    play_resource_sound(
                        self.settings.qchat_ring_tone, self.settings.qchat_sound_volume
                    )
        elif message["author"] == self.settings.author_nickname:
            item = self.create_message_item(
                message["author"],
                message["avatar"],
                message["message"],
                foreground_color=self.settings.qchat_color_self,
            )
        else:
            item = self.create_message_item(
                message["author"],
                message["avatar"],
                message["message"],
            )
        self.twg_chat.addTopLevelItem(item)
        self.twg_chat.scrollToItem(item)

    def handle_internal_message(self, message: dict[str, Any]) -> None:
        """
        Handle an internal message, spotted by its author
        """
        if "nb_users" in message:
            nb_users = message["nb_users"]
            self.grb_qchat.setTitle(
                self.tr("QChat - {nb_users} {user_txt}").format(
                    nb_users=nb_users,
                    user_txt=self.tr("user") if nb_users <= 1 else self.tr("users"),
                )
            )
            self.log(message=f"Internal message received: {nb_users} users in room")

    def on_message_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Action called when double clicking on a chat message
        """
        text = self.lne_message.text()
        author = item.text(1)
        self.lne_message.setText(f"{text}@{author} ")
        self.lne_message.setFocus()

    def on_custom_context_menu_requested(self, point: QPoint) -> None:
        """
        Action called when right clicking on a chat message
        """
        item = self.twg_chat.itemAt(point)
        author = item.text(1)
        message = item.text(2)

        menu = QMenu(self.tr("QChat Menu"), self)

        # copy message to clipboard action
        copy_action = QAction(
            QgsApplication.getThemeIcon("mActionEditCopy.svg"),
            self.tr("Copy message to clipboard"),
        )
        copy_action.triggered.connect(
            partial(self.on_copy_message_to_clipboard, message)
        )
        menu.addAction(copy_action)

        # hide message action
        hide_action = QAction(
            QgsApplication.getThemeIcon("mActionHideSelectedLayers.svg"),
            self.tr("Hide message"),
        )
        hide_action.triggered.connect(partial(self.on_hide_message, item))
        menu.addAction(hide_action)

        # mention user action
        if (
            author != self.settings.author_nickname
            and author != ADMIN_MESSAGES_NICKNAME
        ):
            mention_action = QAction(
                QgsApplication.getThemeIcon("mMessageLogRead.svg"),
                self.tr("Mention user"),
            )
            mention_action.triggered.connect(
                partial(self.on_message_double_clicked, item, 2)
            )
            menu.addAction(mention_action)

        menu.exec(QCursor.pos())

    def on_copy_message_to_clipboard(self, message: str) -> None:
        """
        Action called when copy to clipboard menu action is triggered
        """
        QgsApplication.instance().clipboard().setText(message)

    def on_hide_message(self, item: QTreeWidgetItem) -> None:
        """
        Action called when hide message menu action is triggered
        """
        root = self.twg_chat.invisibleRootItem()
        (item.parent() or root).removeChild(item)

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
        nickname = self.settings.author_nickname
        avatar = self.settings.author_avatar
        message_text = self.lne_message.text()

        if not nickname:
            self.log(
                message=self.tr("Nickname not set : please open settings and set it"),
                log_level=Qgis.Warning,
                push=PlgOptionsManager().get_plg_settings().notify_push_info,
                duration=PlgOptionsManager().get_plg_settings().notify_push_duration,
                button=True,
                button_label=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        if len(nickname) < QCHAT_NICKNAME_MINLENGTH:
            self.log(
                message=self.tr(
                    "Nickname too short : must be at least 3 characters. Please open settings and set it"
                ),
                log_level=Qgis.Warning,
                push=PlgOptionsManager().get_plg_settings().notify_push_info,
                duration=PlgOptionsManager().get_plg_settings().notify_push_duration,
                button=True,
                button_label=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        if not message_text:
            return

        # send message to websocket
        message = {
            "message": message_text.strip(),
            "author": nickname,
            "avatar": avatar,
        }
        self.ws_client.sendTextMessage(json.dumps(message))
        self.lne_message.setText("")

    def add_admin_message(self, message: str) -> None:
        """
        Adds an admin message to QTreeWidget chat
        """
        item = self.create_message_item(
            ADMIN_MESSAGES_NICKNAME,
            ADMIN_MESSAGES_AVATAR,
            message,
            foreground_color=self.settings.qchat_color_admin,
        )
        self.twg_chat.addTopLevelItem(item)
        self.twg_chat.scrollToItem(item)

    def create_message_item(
        self,
        author: str,
        avatar: Optional[str],
        message: str,
        foreground_color: str = None,
        background_color: str = None,
    ) -> QTreeWidgetItem:
        """
        Creates a QTreeWidgetItem for adding to QTreeWidget chat
        Optionally with foreground / background colors given as hexa string
        """
        item_data = [
            QTime.currentTime().toString(),
            author,
            message,
        ]
        item = QTreeWidgetItem(item_data)
        if self.settings.qchat_show_avatars and avatar:
            item.setIcon(1, QIcon(QgsApplication.iconPath(avatar)))
        item.setToolTip(2, message)
        if foreground_color:
            for i in range(len(item_data)):
                item.setForeground(i, QBrush(QColor(foreground_color)))
        if background_color:
            for i in range(len(item_data)):
                item.setBackground(i, QBrush(QColor(background_color)))
        return item

    def on_widget_closed(self) -> None:
        """
        Action called when the widget is closed
        """
        if self.connected:
            self.disconnect_from_room()
        self.cbb_room.currentIndexChanged.disconnect()
        self.initialized = False

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

        # QGIS pro license expiration message
        if msg == CHEATCODE_QGIS_PRO_LICENSE:
            self.log(
                message=self.tr("Your QGIS Pro license is about to expire"),
                application=self.tr("QGIS Pro"),
                log_level=Qgis.Warning,
                push=PlgOptionsManager().get_plg_settings().notify_push_info,
                duration=PlgOptionsManager().get_plg_settings().notify_push_duration,
                button=True,
                button_label=self.tr("Click here to renew it"),
                button_connect=self.on_renew_clicked,
            )
            return True
        # play sounds
        if self.settings.qchat_play_sounds:
            if msg in [CHEATCODE_DONTCRYBABY, CHEATCODE_IAMAROBOT, CHEATCODE_10OCLOCK]:
                play_resource_sound(msg, self.settings.qchat_sound_volume)
                return True
        return False

    def on_renew_clicked(self) -> None:
        msg_box = QMessageBox()
        msg_box.setWindowTitle(self.tr("QGIS"))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(
            self.tr(
                """No... it was a joke!

QGIS is Free and Open Source software, forever.
Free to use, not to make.

Visit the website ?
"""
            )
        )
        msg_box.setStandardButtons(QMessageBox.Yes)
        return_value = msg_box.exec()
        if return_value == QMessageBox.Yes:
            open_url_in_webviewer("https://qgis.org/funding/donate/", "qgis.org")
