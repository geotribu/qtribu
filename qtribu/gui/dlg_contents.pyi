"""Type hints auto-generated from dlg_contents.ui"""

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
)
from qgsmessagebar import QgsMessageBar

class geotribu_toolbox(QDialog):
    btn_donate: QPushButton
    btn_submit_article: QPushButton
    btn_submit_news: QPushButton
    cbb_authors: QComboBox
    cbb_tags: QComboBox
    grp_contents: QGroupBox
    lbl_authors: QLabel
    lbl_search: QLabel
    lbl_tags: QLabel
    lne_search: QLineEdit
    msg_bar: QgsMessageBar
    tree_contents: QTreeWidget

    def __init__(self, parent=None) -> None: ...
