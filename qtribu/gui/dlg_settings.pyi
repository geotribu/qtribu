"""Type hints auto-generated from dlg_settings.ui"""

from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QWidget,
)

class dlg_settings(QDialog):
    btn_help: QPushButton
    btn_report: QPushButton
    btn_reset: QPushButton
    btn_reset_read_history: QPushButton
    chb_integration_news_feed: QCheckBox
    chb_license_global_accept: QCheckBox
    grp_features: QGroupBox
    grp_misc: QGroupBox
    lbl_browser: QLabel
    lbl_notif_duration: QLabel
    lbl_notification: QLabel
    lbl_title: QLabel
    lbl_version_saved: QLabel
    lbl_version_saved_value: QLabel
    opt_browser_os: QRadioButton
    opt_browser_qt: QRadioButton
    opt_debug: QCheckBox
    opt_notif_push_msg: QCheckBox
    sbx_notif_duration: QSpinBox
    sca_settings: QScrollArea
    scrollAreaWidgetContents: QWidget

    def __init__(self, parent=None) -> None: ...
