"""Type hints auto-generated from form_article.ui"""

from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QScrollArea,
    QTextEdit,
    QWidget,
)

class dlg_form_rdp_news(QDialog):
    btn_box: QDialogButtonBox
    cbb_license: QComboBox
    cbb_tags: QComboBox
    chb_transparency: QCheckBox
    dte_proposed_date: QDateEdit
    grp_meta: QGroupBox
    grp_news: QGroupBox
    lbl_comment: QLabel
    lbl_description: QLabel
    lbl_keywords: QLabel
    lbl_license: QLabel
    lbl_proposed_date: QLabel
    lbl_title: QLabel
    lbl_transparency: QLabel
    lne_title: QLineEdit
    scrollArea: QScrollArea
    scrollAreaWidgetContents: QWidget
    txt_comment: QPlainTextEdit
    txt_description: QTextEdit

    def __init__(self, parent=None) -> None: ...
