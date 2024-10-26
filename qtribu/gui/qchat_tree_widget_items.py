import base64
from typing import Optional

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QTime
from qgis.PyQt.QtGui import QBrush, QColor, QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QDialog,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from qtribu.constants import ADMIN_MESSAGES_AVATAR, ADMIN_MESSAGES_NICKNAME
from qtribu.logic.qchat_messages import QChatImageMessage, QChatTextMessage
from qtribu.toolbelt import PlgOptionsManager
from qtribu.toolbelt.preferences import PlgSettingsStructure

TIME_COLUMN = 0
AUTHOR_COLUM = 1
MESSAGE_COLUMN = 2


class QChatTreeWidgetItem(QTreeWidgetItem):
    """
    Custom QTreeWidgetItem implementation for QChat
    A QChatTreeWidgetItem should not be implemented
    See inheriting classes for implementation
    """

    def __init__(
        self, parent: QTreeWidget, time: QTime, author: str, avatar: Optional[str]
    ):
        super().__init__(parent)
        self.plg_settings = PlgOptionsManager()
        self.time = time
        self.author = author
        self.avatar = avatar

    @property
    def settings(self) -> PlgSettingsStructure:
        return self.plg_settings.get_plg_settings()

    def init_time_and_author(self) -> None:
        self.setText(TIME_COLUMN, self.time.toString())
        self.setText(AUTHOR_COLUM, self.author)
        if self.settings.qchat_show_avatars and self.avatar:
            self.setIcon(AUTHOR_COLUM, QIcon(QgsApplication.iconPath(self.avatar)))

    def set_foreground_color(self, color: str) -> None:
        fg_color = QBrush(QColor(color))
        self.setForeground(TIME_COLUMN, fg_color)
        self.setForeground(AUTHOR_COLUM, fg_color)
        self.setForeground(MESSAGE_COLUMN, fg_color)

    def on_click(self, column: int) -> None:
        """
        Triggered when simple clicking on the item
        Empty because this is the expected behaviour
        """
        pass


class QChatAdminTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, text: str):
        super().__init__(
            parent, QTime.currentTime(), ADMIN_MESSAGES_NICKNAME, ADMIN_MESSAGES_AVATAR
        )
        self.text = text
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, text)
        self.setToolTip(MESSAGE_COLUMN, text)
        self.set_foreground_color(self.settings.qchat_color_admin)


class QChatTextTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, message: QChatTextMessage):
        super().__init__(parent, QTime.currentTime(), message.author, message.avatar)
        self.message = message
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, message.text)

        # set foreground color if  user is mentioned
        words = message.text.split(" ")
        if f"@{self.settings.author_nickname}" in words or "@all" in words:
            self.set_foreground_color(self.settings.qchat_color_mention)

        # set foreground color if sent by user
        if message.author == self.settings.author_nickname:
            self.set_foreground_color(self.settings.qchat_color_self)


class QChatImageTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, message: QChatImageMessage):
        super().__init__(parent, QTime.currentTime(), message.author, message.avatar)
        self.message = message
        self.init_time_and_author()

        # set foreground color if sent by user
        if message.author == self.settings.author_nickname:
            self.set_foreground_color(self.settings.qchat_color_self)

        self.pixmap = QPixmap()
        data = base64.b64decode(message.image_data)
        self.pixmap.loadFromData(data)
        label = QLabel(self.parent())
        label.setPixmap(self.pixmap)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, label)
        self.setSizeHint(MESSAGE_COLUMN, self.pixmap.size())

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            dialog = QDialog(self.treeWidget())
            dialog.setWindowTitle(f"QChat image {self.message.author}")
            layout = QVBoxLayout()
            label = QLabel()
            label.setPixmap(self.pixmap)
            layout.addWidget(label)
            dialog.setLayout(layout)
            dialog.setModal(True)
            dialog.show()
