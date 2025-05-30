# standard
import base64
import json
import tempfile
from functools import partial
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.core import Qgis, QgsApplication, QgsJsonExporter, QgsMapLayer, QgsProject
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QPoint, Qt
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QFileDialog,
    QMenu,
    QMessageBox,
    QTreeWidgetItem,
    QWidget,
)

# plugin
from qtribu.__about__ import __title__
from qtribu.constants import (
    ADMIN_MESSAGES_NICKNAME,
    CHEATCODE_10OCLOCK,
    CHEATCODE_DIZZY,
    CHEATCODE_IAMAROBOT,
    CHEATCODE_QGIS_PRO_LICENSE,
    CHEATCODES,
    QCHAT_MESSAGE_TYPE_BBOX,
    QCHAT_MESSAGE_TYPE_CRS,
    QCHAT_MESSAGE_TYPE_GEOJSON,
    QCHAT_MESSAGE_TYPE_IMAGE,
    QCHAT_MESSAGE_TYPE_LIKE,
    QCHAT_MESSAGE_TYPE_NEWCOMER,
    QCHAT_MESSAGE_TYPE_TEXT,
    QCHAT_NICKNAME_MINLENGTH,
)
from qtribu.gui.qchat_tree_widget_items import (
    MESSAGE_COLUMN,
    QChatAdminTreeWidgetItem,
    QChatBboxTreeWidgetItem,
    QChatCrsTreeWidgetItem,
    QChatGeojsonTreeWidgetItem,
    QChatImageTreeWidgetItem,
    QChatTextTreeWidgetItem,
)
from qtribu.logic.qchat_api_client import QChatApiClient
from qtribu.logic.qchat_messages import (
    QChatBboxMessage,
    QChatCrsMessage,
    QChatExiterMessage,
    QChatGeojsonMessage,
    QChatImageMessage,
    QChatLikeMessage,
    QChatNbUsersMessage,
    QChatNewcomerMessage,
    QChatTextMessage,
    QChatUncompliantMessage,
)
from qtribu.logic.qchat_websocket import QChatWebsocket
from qtribu.tasks.dizzy import DizzyTask
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_webviewer, play_resource_sound
from qtribu.toolbelt.preferences import PlgSettingsStructure

# -- GLOBALS --
MARKER_VALUE = "---"


class QChatWidget(QgsDockWidget):
    initialized: bool = False
    connected: bool = False
    current_room: Optional[str] = None

    qchat_client: QChatApiClient
    qchat_ws: QChatWebsocket

    min_author_length: int
    max_author_length: int

    def __init__(
        self,
        iface: QgisInterface,
        parent: Optional[QWidget] = None,
        auto_reconnect_room: Optional[str] = None,
    ):
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

        # set room to autoreconnect to when widget will open
        self.auto_reconnect_room = auto_reconnect_room

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
        self.twg_chat.itemClicked.connect(self.on_message_clicked)
        self.twg_chat.itemDoubleClicked.connect(self.on_message_double_clicked)
        self.twg_chat.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.twg_chat.customContextMenuRequested.connect(
            self.on_custom_context_menu_requested
        )

        # list users signal listener
        self.btn_list_users.pressed.connect(self.on_list_users_button_clicked)
        self.btn_list_users.setIcon(
            QIcon(QgsApplication.iconPath("processingResult.svg"))
        )

        self.ckb_autoscroll.setChecked(True)

        # clear chat signal listener
        self.btn_clear_chat.pressed.connect(self.on_clear_chat_button_clicked)
        self.btn_clear_chat.setIcon(
            QIcon(QgsApplication.iconPath("mActionDeleteSelectedFeatures.svg"))
        )

        # initialize websocket client
        self.qchat_ws = QChatWebsocket()
        self.qchat_ws.error.connect(self.on_ws_error)
        self.qchat_ws.uncompliant_message_received.connect(
            self.on_uncompliant_message_received
        )
        self.qchat_ws.text_message_received.connect(self.on_text_message_received)
        self.qchat_ws.image_message_received.connect(self.on_image_message_received)
        self.qchat_ws.nb_users_message_received.connect(
            self.on_nb_users_message_received
        )
        self.qchat_ws.newcomer_message_received.connect(
            self.on_newcomer_message_received
        )
        self.qchat_ws.exiter_message_received.connect(self.on_exiter_message_received)
        self.qchat_ws.like_message_received.connect(self.on_like_message_received)
        self.qchat_ws.geojson_message_received.connect(self.on_geojson_message_received)
        self.qchat_ws.crs_message_received.connect(self.on_crs_message_received)
        self.qchat_ws.bbox_message_received.connect(self.on_bbox_message_received)

        # send message signal listener
        self.lne_message.returnPressed.connect(self.on_send_button_clicked)
        self.btn_send.pressed.connect(self.on_send_button_clicked)
        self.btn_send.setIcon(
            QIcon(QgsApplication.iconPath("mActionDoubleArrowRight.svg"))
        )

        # send image message signal listener
        self.btn_send_image.pressed.connect(self.on_send_image_button_clicked)
        self.btn_send_image.setIcon(
            QIcon(QgsApplication.iconPath("mActionAddImage.svg"))
        )

        # send QGIS screenshot message signal listener
        self.btn_send_screenshot.pressed.connect(self.on_send_screenshot_button_clicked)
        self.btn_send_screenshot.setIcon(
            QIcon(QgsApplication.iconPath("mActionAddImage.svg"))
        )

        # send extent message signal listener
        self.btn_send_extent.pressed.connect(self.on_send_bbox_button_clicked)
        self.btn_send_extent.setIcon(
            QIcon(QgsApplication.iconPath("mActionViewExtentInCanvas.svg"))
        )

        # send CRS message signal listener
        self.btn_send_crs.pressed.connect(self.on_send_crs_button_clicked)
        self.btn_send_crs.setIcon(
            QIcon(QgsApplication.iconPath("mActionSetProjection.svg"))
        )

    @property
    def settings(self) -> PlgSettingsStructure:
        return self.plg_settings.get_plg_settings()

    def load_settings(self) -> None:
        """Load options from QgsSettings into UI form."""
        self.grb_instance.setTitle(
            self.tr("Instance: {uri}").format(uri=self.settings.qchat_instance_uri)
        )
        self.grb_user.setTitle(
            self.tr("User: {nickname}").format(nickname=self.settings.author_nickname)
        )
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

        # fetch rules for author min/max length
        try:
            rules = self.qchat_client.get_rules()
            self.min_author_length = rules["min_author_length"]
            self.max_author_length = rules["max_author_length"]
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.min_author_length = 3
            self.max_author_length = 32

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
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)
        finally:
            self.current_room = MARKER_VALUE

        self.cbb_room.currentIndexChanged.connect(self.on_room_changed)

        # context menu on vector layer for sending as geojson in QChat
        self.iface.layerTreeView().contextMenuAboutToShow.connect(
            self.generate_qaction_send_geojson_layer
        )

        # auto reconnect to room if needed
        if self.auto_reconnect_room:
            self.cbb_room.setCurrentText(self.auto_reconnect_room)

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
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)

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
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)

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
        if (
            not self.min_author_length
            <= len(self.settings.author_nickname)
            <= self.max_author_length
        ):
            self.log(
                message=self.tr(
                    "QChat nickname not set or too short (between {min} and {max} characters). Please open settings to fix it."
                ).format(min=self.min_author_length, max=self.max_author_length),
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_label=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return
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

        # write new room value to auto-reconnect room in settings if needed
        settings = self.settings
        if settings.qchat_auto_reconnect:
            settings.qchat_auto_reconnect_room = new_room
            self.plg_settings.save_from_object(settings)

    def on_connect_button_clicked(self) -> None:
        """
        Action called when clicking on "Connect" / "Disconnect" button
        """
        if self.connected:
            self.disconnect_from_room()
        else:
            if (
                not self.min_author_length
                <= len(self.settings.author_nickname)
                <= self.max_author_length
            ):
                self.log(
                    message=self.tr(
                        "QChat nickname not set or too short (between {min} and {max} characters). Please open settings to fix it."
                    ).format(min=self.min_author_length, max=self.max_author_length),
                    log_level=Qgis.MessageLevel.Warning,
                    push=self.settings.notify_push_info,
                    duration=self.settings.notify_push_duration,
                    button=True,
                    button_label=self.tr("Open Settings"),
                    button_connect=self.on_settings_button_clicked,
                )
                return
            room = self.cbb_room.currentText()
            if room == MARKER_VALUE:
                return
            self.connect_to_room(room)

    def connect_to_room(self, room: str) -> None:
        """
        Connect widget to a specific room
        """
        self.qchat_ws.open(self.settings.qchat_instance_uri, room)
        self.qchat_ws.connected.connect(partial(self.on_ws_connected, room))

    def on_ws_connected(self, room: str) -> None:
        """
        Action called when websocket is connected to a room
        """
        self.btn_connect.setText(self.tr("Disconnect"))
        self.btn_list_users.setEnabled(True)
        self.grb_user.setEnabled(True)
        self.current_room = room

        # write new room value to auto-reconnect room in settings if needed
        settings = self.settings
        if settings.qchat_auto_reconnect:
            settings.qchat_auto_reconnect_room = room
            self.plg_settings.save_from_object(settings)

        self.connected = True
        self.twg_chat.clear()
        if self.settings.qchat_display_admin_messages:
            self.add_admin_message(
                self.tr("Connected to room '{room}'").format(room=room)
            )

        # send newcomer message to websocket
        if not self.settings.qchat_incognito_mode:
            message = QChatNewcomerMessage(
                type=QCHAT_MESSAGE_TYPE_NEWCOMER, newcomer=self.settings.author_nickname
            )
            self.qchat_ws.send_message(message)

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
        self.grb_qchat.setTitle(self.tr("QChat"))
        self.btn_list_users.setEnabled(False)
        self.grb_user.setEnabled(False)
        self.connected = False
        if close_ws:
            self.qchat_ws.connected.disconnect()
            self.qchat_ws.close()

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
            self.add_admin_message(self.qchat_ws.error_string())
        self.log(
            message=f"{error_code}: {self.qchat_ws.error_string()}",
            log_level=Qgis.MessageLevel.Critical,
        )

    # region websocket message received

    def on_uncompliant_message_received(self, message: QChatUncompliantMessage) -> None:
        self.log(
            message=self.tr("Uncompliant message: {reason}").format(
                reason=message.reason
            ),
            application=self.tr("QChat"),
            log_level=Qgis.MessageLevel.Critical,
            push=self.settings.notify_push_info,
            duration=self.settings.notify_push_duration,
        )

    def on_text_message_received(self, message: QChatTextMessage) -> None:
        """
        Launched when a text message is received from the websocket
        """
        # check if a cheatcode is activated
        if self.settings.qchat_activate_cheatcode:
            activated = self.check_cheatcode(message.text)
            if activated:
                return

        # do not display cheatcodes even if not activated
        if message.text in CHEATCODES:
            return

        item = QChatTextTreeWidgetItem(self.twg_chat, message)

        # check if message mentions current user
        words = message.text.split(" ")
        if f"@{self.settings.author_nickname}" in words or "@all" in words:
            if message.author != self.settings.author_nickname:
                self.log(
                    message=self.tr(
                        "You were mentionned by {sender}: {message}"
                    ).format(sender=message.author, message=message.text),
                    application=self.tr("QChat"),
                    log_level=Qgis.MessageLevel.Info,
                    push=self.settings.notify_push_info,
                    duration=self.settings.notify_push_duration,
                )

                # check if a notification sound should be played
                if self.settings.qchat_play_sounds:
                    play_resource_sound(
                        self.settings.qchat_ring_tone, self.settings.qchat_sound_volume
                    )

        self.add_tree_widget_item(item)

    def on_image_message_received(self, message: QChatImageMessage) -> None:
        """
        Launched when an image message is received from the websocket
        """
        item = QChatImageTreeWidgetItem(self.twg_chat, message)
        self.add_tree_widget_item(item)

    def on_nb_users_message_received(self, message: QChatNbUsersMessage) -> None:
        """
        Launched when a nb_users message is received from the websocket
        """
        self.grb_qchat.setTitle(
            self.tr("QChat - room: {room} - {nb_users} {user_txt}").format(
                room=self.current_room,
                nb_users=message.nb_users,
                user_txt=self.tr("user") if message.nb_users <= 1 else self.tr("users"),
            )
        )

    def on_newcomer_message_received(self, message: QChatNewcomerMessage) -> None:
        """
        Launched when a newcomer message is received from the websocket
        """
        if (
            self.settings.qchat_display_admin_messages
            and message.newcomer != self.settings.author_nickname
        ):
            self.add_admin_message(
                self.tr("{newcomer} has joined the room").format(
                    newcomer=message.newcomer
                )
            )

    def on_exiter_message_received(self, message: QChatExiterMessage) -> None:
        """
        Launched when an exiter message is received from the websocket
        """
        if (
            self.settings.qchat_display_admin_messages
            and message.exiter != self.settings.author_nickname
        ):
            self.add_admin_message(
                self.tr("{exiter} has left the room").format(exiter=message.exiter)
            )

    def on_like_message_received(self, message: QChatLikeMessage) -> None:
        """
        Launched when a like message is received from the websocket
        """
        if message.liked_author == self.settings.author_nickname:
            self.log(
                message=self.tr("{liker_author} liked your message: {message}").format(
                    liker_author=message.liker_author, message=message.message
                ),
                application=self.tr("QChat"),
                log_level=Qgis.MessageLevel.Success,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            # play a notification sound if enabled
            if self.settings.qchat_play_sounds:
                play_resource_sound(
                    self.settings.qchat_ring_tone, self.settings.qchat_sound_volume
                )

    def on_geojson_message_received(self, message: QChatGeojsonMessage) -> None:
        """
        Launched when a geojson message is received from the websocket
        """
        item = QChatGeojsonTreeWidgetItem(self.twg_chat, message)
        self.add_tree_widget_item(item)

    def on_crs_message_received(self, message: QChatCrsMessage) -> None:
        """
        Launched when a CRS message is received from the websocket
        """
        item = QChatCrsTreeWidgetItem(self.twg_chat, message)
        self.add_tree_widget_item(item)

    def on_bbox_message_received(self, message: QChatBboxMessage) -> None:
        """
        Launched when a BBOX message is received from the websocket
        """
        item = QChatBboxTreeWidgetItem(self.twg_chat, message, self.iface.mapCanvas())
        self.add_tree_widget_item(item)

    # endregion

    def on_message_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Action called when clicking on a chat message
        """
        item.on_click(column)

    def on_message_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Action called when double clicking on a chat message
        """
        author = item.author
        # do nothing if double click on admin message
        if author == ADMIN_MESSAGES_NICKNAME or author == self.settings.author_nickname:
            return
        text = self.lne_message.text()
        self.lne_message.setText(f"{text}@{author} ")
        self.lne_message.setFocus()

    def on_like_message(self, liked_author: str, msg: str) -> None:
        """
        Action called when the "Like message" action is triggered
        This may happen on right-click on a message
        """
        message = QChatLikeMessage(
            type=QCHAT_MESSAGE_TYPE_LIKE,
            liker_author=self.settings.author_nickname,
            liked_author=liked_author,
            message=msg,
        )
        self.qchat_ws.send_message(message)

    def on_custom_context_menu_requested(self, point: QPoint) -> None:
        """
        Action called when right clicking on a chat message
        """
        item = self.twg_chat.itemAt(point)

        menu = QMenu(self.tr("QChat Menu"), self)

        # if this is a geojson message
        if type(item) is QChatGeojsonTreeWidgetItem:
            load_geojson_action = QAction(
                QgsApplication.getThemeIcon("mActionAddLayer.svg"),
                self.tr("Load layer in QGIS"),
            )
            load_geojson_action.triggered.connect(
                partial(item.on_click, MESSAGE_COLUMN)
            )
            menu.addAction(load_geojson_action)

        # if this is a crs message
        if type(item) is QChatCrsTreeWidgetItem:
            set_crs_action = QAction(
                QgsApplication.getThemeIcon("mActionSetProjection.svg"),
                self.tr("Set current project CRS"),
            )
            set_crs_action.triggered.connect(partial(item.on_click, MESSAGE_COLUMN))
            menu.addAction(set_crs_action)

        # if this is a bbox message
        if type(item) is QChatBboxTreeWidgetItem:
            set_bbox_action = QAction(
                QgsApplication.getThemeIcon("mActionViewExtentInCanvas.svg"),
                self.tr("Set current extent"),
            )
            set_bbox_action.triggered.connect(partial(item.on_click, MESSAGE_COLUMN))
            menu.addAction(set_bbox_action)

        # like message action if possible
        if item.can_be_liked:
            like_action = QAction(
                QgsApplication.getThemeIcon("mActionInOverview.svg"),
                self.tr("Like message"),
            )
            like_action.triggered.connect(
                partial(self.on_like_message, item.author, item.liked_message)
            )
            menu.addAction(like_action)

        # mention author action if possible
        if item.can_be_mentioned:
            mention_action = QAction(
                QgsApplication.getThemeIcon("mMessageLogRead.svg"),
                self.tr("Mention user"),
            )
            mention_action.triggered.connect(
                partial(self.on_message_double_clicked, item, 2)
            )
            menu.addAction(mention_action)

        # copy message to clipboard action if possible
        if item.can_be_copied_to_clipboard:
            copy_action = QAction(
                QgsApplication.getThemeIcon("mActionEditCopy.svg"),
                self.tr("Copy message to clipboard"),
            )
            copy_action.triggered.connect(item.copy_to_clipboard)
            menu.addAction(copy_action)

        # hide message action
        hide_action = QAction(
            QgsApplication.getThemeIcon("mActionHideSelectedLayers.svg"),
            self.tr("Hide message"),
        )
        hide_action.triggered.connect(partial(self.on_hide_message, item))
        menu.addAction(hide_action)

        menu.exec(QCursor.pos())

    def on_hide_message(self, item: QTreeWidgetItem) -> None:
        """
        Action called when hide message menu action is triggered
        """
        root = self.twg_chat.invisibleRootItem()
        (item.parent() or root).removeChild(item)

    def on_list_users_button_clicked(self) -> None:
        """
        Action called when the list users button is clicked
        """
        if self.settings.qchat_incognito_mode:
            QMessageBox.warning(
                self,
                self.tr("Registered users"),
                self.tr(
                    "You're using incognito mode. Please disable it to see registered users."
                ),
            )
            return
        try:
            users = self.qchat_client.get_registered_users(self.current_room)
            QMessageBox.information(
                self,
                self.tr("Registered users"),
                self.tr(
                    """Registered users in room ({room}):

{users}"""
                ).format(room=self.current_room, users=",".join(users)),
            )
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)

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
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_label=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        if len(nickname) < QCHAT_NICKNAME_MINLENGTH:
            self.log(
                message=self.tr(
                    "Nickname too short: must be at least 3 characters. Please open settings and set it"
                ),
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_label=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        if not message_text:
            return

        # send message to websocket
        message = QChatTextMessage(
            type=QCHAT_MESSAGE_TYPE_TEXT,
            author=nickname,
            avatar=avatar,
            text=message_text.strip(),
        )
        self.qchat_ws.send_message(message)
        self.lne_message.setText("")

    def on_send_image_button_clicked(self) -> None:
        """
        Action called when the send image button is clicked
        """

        # select some image files on disk
        files = QFileDialog.getOpenFileNames(
            parent=self,
            caption=self.tr("Select images to send to the chat"),
            filter="Images (*.png *.jpg *.jpeg)",
        )
        for fp in files[0]:
            # send the image through the websocket
            with open(fp, "rb") as file:
                data = file.read()
                message = QChatImageMessage(
                    type=QCHAT_MESSAGE_TYPE_IMAGE,
                    author=self.settings.author_nickname,
                    avatar=self.settings.author_avatar,
                    image_data=base64.b64encode(data).decode("utf-8"),
                )
                self.qchat_ws.send_message(message)

    def on_send_screenshot_button_clicked(self) -> None:
        """
        Action called when the Send QGIS screenshot button is clicked
        """

        sc_fp = Path(tempfile.gettempdir()) / "qgis_screenshot.png"
        self.iface.mapCanvas().saveAsImage(str(sc_fp))
        with open(sc_fp, "rb") as file:
            data = file.read()
            message = QChatImageMessage(
                type=QCHAT_MESSAGE_TYPE_IMAGE,
                author=self.settings.author_nickname,
                avatar=self.settings.author_avatar,
                image_data=base64.b64encode(data).decode("utf-8"),
            )
            self.qchat_ws.send_message(message)

    def on_send_bbox_button_clicked(self) -> None:
        """
        Action called when the Send extent button is clicked
        """
        crs = QgsProject.instance().crs()
        rect = self.iface.mapCanvas().extent()
        message = QChatBboxMessage(
            type=QCHAT_MESSAGE_TYPE_BBOX,
            author=self.settings.author_nickname,
            avatar=self.settings.author_avatar,
            crs_wkt=crs.toWkt(),
            crs_authid=crs.authid(),
            xmin=rect.xMinimum(),
            xmax=rect.xMaximum(),
            ymin=rect.yMinimum(),
            ymax=rect.yMaximum(),
        )
        self.qchat_ws.send_message(message)

    def on_send_crs_button_clicked(self) -> None:
        """
        Action called when the Send CRS button is clicked
        """
        crs = QgsProject.instance().crs()
        message = QChatCrsMessage(
            type=QCHAT_MESSAGE_TYPE_CRS,
            author=self.settings.author_nickname,
            avatar=self.settings.author_avatar,
            crs_wkt=crs.toWkt(),
            crs_authid=crs.authid(),
        )
        self.qchat_ws.send_message(message)

    def add_admin_message(self, text: str) -> None:
        """
        Adds an admin message to QTreeWidget chat
        """
        item = QChatAdminTreeWidgetItem(self.twg_chat, text)
        self.add_tree_widget_item(item)

    def add_tree_widget_item(self, item: QTreeWidgetItem) -> None:
        self.twg_chat.addTopLevelItem(item)
        if self.ckb_autoscroll.isChecked():
            self.twg_chat.scrollToItem(item)

    def on_widget_closed(self) -> None:
        """
        Action called when the widget is closed
        """
        if self.connected:
            self.disconnect_from_room()
        self.cbb_room.currentIndexChanged.disconnect()
        self.initialized = False

        # remove context menu on vector layer for sending as geojson in QChat
        self.iface.layerTreeView().contextMenuAboutToShow.disconnect(
            self.generate_qaction_send_geojson_layer
        )

    def check_cheatcode(self, text: str) -> bool:
        """
        Checks if a received message contains a cheatcode
        Does action if necessary
        Returns true if a cheatcode has been activated
        """
        # make QGIS shuffle for a few seconds
        if text == CHEATCODE_DIZZY:
            task = DizzyTask(f"Cheatcode activation: {CHEATCODE_DIZZY}", self.iface)
            self.task_manager.addTask(task)
            return True

        # QGIS pro license expiration message
        if text == CHEATCODE_QGIS_PRO_LICENSE:
            self.log(
                message=self.tr("Your QGIS Pro license is about to expire"),
                application="QGIS Pro",
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_label=self.tr("Click here to renew it"),
                button_connect=self.on_renew_clicked,
            )
            return True
        # play sounds
        if self.settings.qchat_play_sounds:
            if text in [CHEATCODE_IAMAROBOT, CHEATCODE_10OCLOCK]:
                play_resource_sound(text, self.settings.qchat_sound_volume)
                return True
        return False

    def on_renew_clicked(self) -> None:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("QGIS")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            self.tr(
                """No... it was a joke!

QGIS is Free and Open Source software, forever.
Free to use, not to make.

Visit the website ?
"""
            )
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes)
        return_value = msg_box.exec()
        if return_value == QMessageBox.StandardButton.Yes:
            open_url_in_webviewer("https://qgis.org/funding/donate/", "qgis.org")

    def generate_qaction_send_geojson_layer(self, menu: QMenu) -> None:
        menu.addSeparator()
        send_geojson_action = QAction(
            QgsApplication.getThemeIcon("mMessageLog.svg"),
            self.tr("Send on QChat"),
            self.iface.mainWindow(),
        )
        send_geojson_action.triggered.connect(self.on_send_layer_to_qchat)
        menu.addAction(send_geojson_action)

    def on_send_layer_to_qchat(self) -> None:
        if not self.connected:
            self.log(
                message=self.tr(
                    "Not connected to QChat. Please connect to a room first"
                ),
                application="QChat",
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return
        layer = self.iface.activeLayer()
        if not layer:
            self.log(
                message=self.tr("No active layer in current QGIS project"),
                application=self.tr("QChat"),
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return
        if layer.type() != QgsMapLayer.LayerType.VectorLayer:
            self.log(
                message=self.tr("Only vector layers can be sent on QChat"),
                application=self.tr("QChat"),
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return

        exporter = QgsJsonExporter(layer)
        exporter.setSourceCrs(layer.crs())
        exporter.setDestinationCrs(layer.crs())
        exporter.setTransformGeometries(True)
        geojson_str = exporter.exportFeatures(layer.getFeatures())

        # save and read QML style to and from temp file
        save_style_path = Path(tempfile.gettempdir()) / "qchat_layer_style.qml"
        layer.saveNamedStyle(
            str(save_style_path),
            categories=QgsMapLayer.StyleCategory.AllStyleCategories,
        )
        with open(save_style_path, "r", encoding="utf-8") as file:
            qml_style = file.read()

        message = QChatGeojsonMessage(
            type=QCHAT_MESSAGE_TYPE_GEOJSON,
            author=self.settings.author_nickname,
            avatar=self.settings.author_avatar,
            layer_name=layer.name(),
            crs_wkt=layer.crs().toWkt(),
            crs_authid=layer.crs().authid(),
            geojson=json.loads(geojson_str),
            style=qml_style,
        )
        self.qchat_ws.send_message(message)
