# standard
from pathlib import Path

from nio import AsyncClient, MatrixRoom, RoomMessageText
from PySide6 import QtAsyncio
from qasync import asyncSlot

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QWidget

# plugin
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.preferences import PlgSettingsStructure

# -- GLOBALS --
MARKER_VALUE = "---"


class QChatMatrixWidget(QgsDockWidget):
    matrix_client = None

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

        # connect signal listener
        self.connected = False
        self.btn_connect.pressed.connect(self.on_connect_button_clicked)
        self.btn_connect.setIcon(QIcon(QgsApplication.iconPath("mIconConnect.svg")))

        # send signal listener
        self.btn_send.pressed.connect(self.on_send_message)
        self.btn_send.setIcon(QIcon(QgsApplication.iconPath("mIconConnect.svg")))

        self.opened.connect(self.on_opened)
        self.closed.connect(self.on_closed)

        QtAsyncio.run(handle_sigint=True)

    @property
    def settings(self) -> PlgSettingsStructure:
        return self.plg_settings.get_plg_settings()

    def on_opened(self) -> None:
        print("widget opened")

    def on_closed(self) -> None:
        print("widget closed")

    @asyncSlot()
    async def on_connect_button_clicked(self) -> None:
        homeserver = self.lne_homeserver.text()
        user = self.lne_user.text()
        password = self.lne_password.text()
        if not homeserver or not user or not password:
            QMessageBox.warning(
                self,
                self.tr("Login"),
                "Please fill the homeserver, user and password part",
            )
            return

        await self.connect(homeserver, user, password, "qtribu")

    async def connect(
        self, homeserver: str, user: str, password: str, device_id: str
    ) -> None:
        self.matrix_client = AsyncClient(
            homeserver=homeserver, user=user, device_id=device_id
        )
        self.matrix_client.add_event_callback(self.on_message_received, RoomMessageText)
        await self.matrix_client.login(password)
        await self.matrix_client.sync_forever(timeout=30000)
        self.connected = True
        self.btn_connect.setText(self.tr("Disconnect"))
        print(await self.matrix_client.get_displayname())

    async def on_message_received(
        self, room: MatrixRoom, event: RoomMessageText
    ) -> None:
        QMessageBox.information(
            self,
            self.tr("Matrix message received"),
            f"Message received in room {room.display_name}\n"
            f"{room.user_name(event.sender)} | {event.body}",
        )
        print(dir(room))
        print(dir(event))

    @asyncSlot()
    async def on_send_message(self) -> None:
        if not self.connected:
            QMessageBox.warning(
                self, self.tr("Matrix"), self.tr("Not connected. Please connect first")
            )
        msg = self.lne_message.text()
        await self.matrix_client.room_send(
            # Watch out! If you join an old room you'll see lots of old messages
            room_id=self.lne_room.text(),
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": msg},
        )
        self.lne_message.setText("")
