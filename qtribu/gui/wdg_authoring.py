# standard
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QWidget

# plugin
from qtribu.gui.gui_commons import QVAL_ALPHANUM, QVAL_EMAIL, QVAL_URL
from qtribu.toolbelt import PlgLogger, PlgOptionsManager


class AuthoringWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        """QWidget to set user informations.

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # check inputs
        self.lne_qchat_nickname.setValidator(QVAL_ALPHANUM)
        self.lne_email.setValidator(QVAL_EMAIL)
        self.lne_github_account.setValidator(QVAL_URL)
        self.lne_linkedin_account.setValidator(QVAL_URL)
        self.lne_twitter_account.setValidator(QVAL_URL)

        # play sound on ringtone changed
        self.cbb_qchat_avatar.currentIndexChanged.connect(self.on_avatar_index_changed)

        # fill fields from saved settings
        self.load_settings()

    def load_settings(self) -> dict:
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # author
        self.lne_qchat_nickname.setText(settings.author_nickname)
        avatar_index = self.cbb_qchat_avatar.findText(
            settings.author_avatar, Qt.MatchFixedString
        )
        if avatar_index >= 0:
            self.cbb_qchat_avatar.setCurrentIndex(avatar_index)
            self.btn_avatar_preview.setIcon(
                QIcon(QgsApplication.iconPath(settings.author_avatar))
            )

        self.lne_firstname.setText(settings.author_firstname)
        self.lne_lastname.setText(settings.author_lastname)
        self.lne_email.setText(settings.author_email)
        self.lne_github_account.setText(settings.author_github)
        self.lne_linkedin_account.setText(settings.author_linkedin)
        self.lne_twitter_account.setText(settings.author_twitter)
        self.lne_mastodon_account.setText(settings.author_mastodon)

    def save_settings(self) -> None:
        """Save form text into QgsSettings."""
        # get settings
        settings = self.plg_settings.get_plg_settings()

        # store user inputs
        settings.author_nickname = self.lne_qchat_nickname.text()
        settings.author_avatar = self.cbb_qchat_avatar.currentText()
        settings.author_firstname = self.lne_firstname.text()
        settings.author_lastname = self.lne_lastname.text()
        settings.author_email = self.lne_email.text()
        settings.author_github = self.lne_github_account.text()
        settings.author_linkedin = self.lne_linkedin_account.text()
        settings.author_twitter = self.lne_twitter_account.text()
        settings.author_mastodon = self.lne_mastodon_account.text()

        # save it
        self.plg_settings.save_from_object(settings)

    def on_avatar_index_changed(self) -> None:
        """
        Action launched when avatar index is changed in combobox
        """
        self.btn_avatar_preview.setIcon(
            QIcon(QgsApplication.iconPath(self.cbb_qchat_avatar.currentText()))
        )
