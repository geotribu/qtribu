# standard
from datetime import datetime
from pathlib import Path
from typing import Any

from qgis.gui import QgsDockWidget

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QTreeWidgetItem, QWidget

from qtribu.logic.qchat_client import QChatApiClient

# plugin
from qtribu.toolbelt import PlgLogger, PlgOptionsManager

# -- GLOBALS --
MARKER_VALUE = "---"


class QChatWidget(QgsDockWidget):
    def __init__(self, parent: QWidget = None):
        """QWidget to see and post messages on chat

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
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
            self.cb_room.addItem(room["name"])
        self.current_room = MARKER_VALUE

        self.cb_room.currentIndexChanged.connect(self.on_room_changed)

        # connect signal listener
        self.connected = False
        self.btn_connect.pressed.connect(self.on_connect_button_clicked)

        # tree widget initialization
        self.tw_chat.setHeaderLabels(
            [
                self.tr("Room"),
                self.tr("Date"),
                self.tr("Nick"),
                self.tr("Message"),
            ]
        )

    def load_settings(self) -> dict:
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
        if new_room == MARKER_VALUE:
            self.disconnect_from_room()
            self.current_room = MARKER_VALUE
            return
        self.disconnect_from_room(log=old_room != MARKER_VALUE)
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
        messages = self.qchat_client.get_last_messages(room)
        messages.reverse()
        if log:
            self.tw_chat.insertTopLevelItem(
                0,
                QTreeWidgetItem(
                    [
                        room,
                        datetime.now().strftime("%H:%M"),
                        self.tr("Admin"),
                        self.tr("Connected to room '{room}'").format(room=room),
                    ]
                ),
            )
        for message in messages:
            qtw_item = self.add_message_to_treeview(room, message)
            self.tw_chat.insertTopLevelItem(0, qtw_item)

        self.btn_connect.setText(self.tr("Disconnect"))
        self.lb_status.setText("Connected")
        self.connected = True

    def disconnect_from_room(self, log: bool = True) -> None:
        if log:
            self.tw_chat.insertTopLevelItem(
                0,
                QTreeWidgetItem(
                    [
                        self.current_room,
                        datetime.now().strftime("%H:%M"),
                        self.tr("Admin"),
                        self.tr("Disconnected from room '{room}'").format(
                            room=self.current_room
                        ),
                    ]
                ),
            )
        self.btn_connect.setText(self.tr("Connect"))
        self.lb_status.setText("Disconnected")
        self.connected = False

    def add_message_to_treeview(self, room: str, message: dict[str, Any]) -> None:
        item = QTreeWidgetItem(
            [
                room,
                # TODO: convert date to nice format like %H:%M
                message["date_posted"],
                message["author"],
                message["message"],
            ]
        )
        return item
