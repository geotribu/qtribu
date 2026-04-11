"""Type hints auto-generated from form_rdp_news.ui"""

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QWidget,
)
from qgscollapsiblegroupbox import QgsCollapsibleGroupBox
from qgsmessagebar import QgsMessageBar

from qtribu.gui.wdg_authoring import AuthoringWidget

class dlg_form_rdp_news(QDialog):
    btn_box: QDialogButtonBox
    btn_preview: QPushButton
    cbb_category: QComboBox
    cbb_icon: QComboBox
    cbb_tags: QComboBox
    chb_auto_preview: QCheckBox
    chb_license: QCheckBox
    chb_transparency: QCheckBox
    grp_meta: QGroupBox
    grp_news: QGroupBox
    grp_preview: QgsCollapsibleGroupBox
    lbl_body: QLabel
    lbl_category: QLabel
    lbl_comment: QLabel
    lbl_icon: QLabel
    lbl_keywords: QLabel
    lbl_license: QLabel
    lbl_preview: QLabel
    lbl_title: QLabel
    lbl_transparency: QLabel
    line: Line
    line_2: Line
    lne_title: QLineEdit
    msg_bar: QgsMessageBar
    scrollArea: QScrollArea
    scrollAreaWidgetContents: QWidget
    txt_body: QTextEdit
    txt_comment: QPlainTextEdit
    txt_preview: QTextEdit
    wdg_author: AuthoringWidget

    def __init__(self, parent=None) -> None: ...
