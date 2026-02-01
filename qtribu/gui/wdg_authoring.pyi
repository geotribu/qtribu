"""Type hints auto-generated from wdg_authoring.ui"""

from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget
from qgscollapsiblegroupbox import QgsCollapsibleGroupBox

class AuthorInformationsWidget(QWidget):
    grp_author: QgsCollapsibleGroupBox
    lbl_email: QLabel
    lbl_firstname: QLabel
    lbl_github_account: QLabel
    lbl_lastname: QLabel
    lbl_linked_account: QLabel
    lbl_mastodon_account: QLabel
    lbl_twitter_account: QLabel
    lne_email: QLineEdit
    lne_firstname: QLineEdit
    lne_github_account: QLineEdit
    lne_lastname: QLineEdit
    lne_linkedin_account: QLineEdit
    lne_mastodon_account: QLineEdit
    lne_twitter_account: QLineEdit

    def __init__(self, parent=None) -> None: ...
