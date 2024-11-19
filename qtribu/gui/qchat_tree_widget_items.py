import base64
import json
import os
import tempfile
from typing import Optional

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas
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
from qtribu.logic.qchat_messages import (
    QChatBboxMessage,
    QChatCrsMessage,
    QChatGeojsonMessage,
    QChatImageMessage,
    QChatTextMessage,
)
from qtribu.toolbelt import PlgOptionsManager
from qtribu.toolbelt.preferences import PlgSettingsStructure

TIME_COLUMN = 0
AUTHOR_COLUM = 1
MESSAGE_COLUMN = 2

MAX_IMAGE_ITEM_HEIGHT = 24


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
        :param column: column that has been clicked
        """
        pass

    @property
    def can_be_liked(self) -> bool:
        """
        Returns if the item can be liked
        """
        return self.author != self.settings.author_nickname

    @property
    def liked_message(self) -> str:
        """
        Returns the text message that was liked
        """
        pass

    @property
    def can_be_mentioned(self) -> bool:
        """
        Returns if the item can be mentioned
        """
        return self.author != self.settings.author_nickname

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        """
        Returns if the item can be copied to clipboard
        """
        return False

    def copy_to_clipboard(self) -> None:
        """
        Performs action of copying message to clipboard
        If the can_be_copied_to_clipboard is enabled ofc
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

    @property
    def can_be_liked(self) -> bool:
        return False

    @property
    def can_be_mentioned(self) -> bool:
        return False


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

    @property
    def liked_message(self) -> str:
        return self.message.text

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.message.text)


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
        label.setMaximumSize(label.sizeHint().width(), MAX_IMAGE_ITEM_HEIGHT)
        self.treeWidget().setItemWidget(self, MESSAGE_COLUMN, label)

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

    @property
    def liked_message(self) -> str:
        return "image"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setPixmap(self.pixmap)


class QChatGeojsonTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, message: QChatGeojsonMessage):
        super().__init__(parent, QTime.currentTime(), message.author, message.avatar)
        self.message = message
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, self.liked_message)
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.author_nickname:
            self.set_foreground_color(self.settings.qchat_color_self)

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            # save geojson to temp file
            save_path = os.path.join(
                tempfile.gettempdir(), f"{self.message.layer_name}.geojson"
            )
            with open(save_path, "w") as file:
                json.dump(self.message.geojson, file)
            # load geojson file into QGIS
            layer = QgsVectorLayer(save_path, self.message.layer_name, "ogr")
            layer.setCrs(QgsCoordinateReferenceSystem.fromWkt(self.message.crs_wkt))
            QgsProject.instance().addMapLayer(layer)

    @property
    def liked_message(self) -> str:
        layer_name = self.message.layer_name
        nb_features = len(self.message.geojson["features"])
        crs = self.message.crs_authid
        return f'<layer "{layer_name}": {nb_features} features, CRS={crs}>'

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(json.dumps(self.message.geojson))


class QChatCrsTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(self, parent: QTreeWidget, message: QChatCrsMessage):
        super().__init__(parent, QTime.currentTime(), message.author, message.avatar)
        self.message = message
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, self.liked_message)
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.author_nickname:
            self.set_foreground_color(self.settings.qchat_color_self)

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            # set current QGIS project CRS to the message one
            crs = QgsCoordinateReferenceSystem.fromWkt(self.message.crs_wkt)
            QgsProject.instance().setCrs(crs)

    @property
    def liked_message(self) -> str:
        return f"<CRS {self.message.crs_authid}>"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        QgsApplication.instance().clipboard().setText(self.message.crs_wkt)


class QChatBboxTreeWidgetItem(QChatTreeWidgetItem):
    def __init__(
        self, parent: QTreeWidget, message: QChatBboxMessage, canvas: QgsMapCanvas
    ):
        super().__init__(parent, QTime.currentTime(), message.author, message.avatar)
        self.message = message
        self.canvas = canvas
        self.init_time_and_author()
        self.setText(MESSAGE_COLUMN, self.liked_message)
        self.setToolTip(MESSAGE_COLUMN, self.liked_message)

        # set foreground color if sent by user
        if message.author == self.settings.author_nickname:
            self.set_foreground_color(self.settings.qchat_color_self)

    def on_click(self, column: int) -> None:
        if column == MESSAGE_COLUMN:
            # set current canvas extent to the received one
            project = QgsProject.instance()
            tr = QgsCoordinateTransform(
                QgsCoordinateReferenceSystem(self.message.crs_wkt),
                project.crs(),
                project,
            )
            rect = QgsRectangle(
                tr.transform(QgsPointXY(self.message.xmin, self.message.ymin)),
                tr.transform(QgsPointXY(self.message.xmax, self.message.ymax)),
            )
            self.canvas.setExtent(rect)
            self.canvas.refresh()

    @property
    def liked_message(self) -> str:
        msg = f"[{self.message.xmin} {self.message.ymin}, {self.message.xmax} {self.message.ymax}]"
        return f"<BBOX {self.message.crs_authid}: {msg}>"

    @property
    def can_be_copied_to_clipboard(self) -> bool:
        return True

    def copy_to_clipboard(self) -> None:
        msg = f"[{self.message.xmin} {self.message.ymin}, {self.message.xmax} {self.message.ymax}]"
        QgsApplication.instance().clipboard().setText(msg)
