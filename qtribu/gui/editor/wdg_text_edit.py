"""Widget for text display with preview option."""

# standard
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QToolBar, QWidget


class TextEditPreviewWidget(QWidget):
    """QWidget to display text with a preview option

    :param parent: dialog parent, defaults to None
    :type parent: Optional[QWidget], optional
    """

    # Signal to indicate changes in issue displayed
    textChanged = QtCore.pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        ui_path = Path(__file__).resolve(True).parent / "wdg_text_edit.ui"
        uic.loadUi(ui_path, self)

        self.btn_switch.clicked.connect(self._switch_mode)
        self.btn_switch.setText(self.tr("Preview"))

        self.txt_edit.textChanged.connect(self.textChanged.emit)

        self.txt_edit.setVisible(True)
        self.txt_preview.setVisible(False)

        # Add toolbar for edition
        self.edit_toolbar = QToolBar(self)
        self.edit_toolbar.setIconSize(QSize(16, 16))
        self.lyt_toolbar.addWidget(self.edit_toolbar)

        for action in self.txt_edit.get_edit_actions():
            self.edit_toolbar.addAction(action)

    def set_project_id(self, project_id: str) -> None:
        """Define project id, needed form upload download

        :param project_id: project id
        :type project_id: str
        """
        self.txt_preview.set_project_id(project_id)
        self.txt_edit.set_project_id(project_id)

    def _switch_mode(self) -> None:
        """Switch current mode"""
        if self.txt_preview.isVisible():
            self.btn_switch.setText(self.tr("Preview"))
            self.txt_edit.setVisible(True)
            self.frm_edit_toolbar.setVisible(True)
            self.txt_preview.setVisible(False)
        else:
            self.btn_switch.setText(self.tr("Edit"))
            self.txt_edit.setVisible(False)
            self.frm_edit_toolbar.setVisible(False)
            self.txt_preview.setVisible(True)
            self.txt_preview.setMarkdown(self.toPlainText())

    def setText(self, text: str) -> None:
        """Set text displayed

        :param text: text displayed
        :type text: str
        """
        self.txt_edit.setPlainText(text)
        self.txt_preview.setMarkdown(text)

    def toPlainText(self) -> str:
        """Get edit plain text

        :return: edit plain text
        :rtype: str
        """
        return self.txt_edit.toPlainText()

    def setReadOnly(self, read_only: bool = True) -> None:
        """Disable / Enable edition of text

        :param read_only: True to disable edition, Falst to enable edition, defaults to True
        :type read_only: bool, optional
        """
        self.frm_buttons.setVisible(not read_only)
        self.txt_edit.setVisible(not read_only)
        self.txt_preview.setVisible(read_only)
        self.btn_switch.setText(self.tr("Edit") if read_only else self.tr("Preview"))

    def setPlaceholderText(self, text: str) -> None:
        """Define text edit place holder text

        :param text: place holder text
        :type text: str
        """
        self.txt_edit.setPlaceholderText(text)

    def clear(self) -> None:
        """Clear current content"""
        self.txt_edit.clear()
        self.txt_preview.clear()
