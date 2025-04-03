# standard
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.core import Qgis, QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QWidget

# plugin
from qtribu.constants import QCHAT_USER_AVATARS
from qtribu.gui.gui_commons import QVAL_ALPHANUM, QVAL_EMAIL, QVAL_URL
from qtribu.toolbelt import PlgLogger, PlgOptionsManager


class AuthoringWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
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

        # avatar combobox
        self.cbb_avatars_populate()

        # fill fields from saved settings
        self.load_settings()

    def load_settings(self) -> None:
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # author
        self.lne_qchat_nickname.setText(settings.author_nickname)

        # retrieve avatar amon values
        if settings.author_avatar in QCHAT_USER_AVATARS.values():
            self.cbb_qchat_avatar.setCurrentIndex(
                list(QCHAT_USER_AVATARS.values()).index(settings.author_avatar)
            )
        else:
            self.log(
                message="Avatar {} has not been found among available one: {}".format(
                    settings.author_avatar, ", ".join(QCHAT_USER_AVATARS.values())
                ),
                log_level=Qgis.Warning,
                push=True,
            )
            self.cbb_qchat_avatar.setCurrentIndex(4)

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
        settings.author_avatar = QCHAT_USER_AVATARS.get(
            self.cbb_qchat_avatar.currentText(), "mIconInfo.svg"
        )
        settings.author_firstname = self.lne_firstname.text()
        settings.author_lastname = self.lne_lastname.text()
        settings.author_email = self.lne_email.text()
        settings.author_github = self.lne_github_account.text()
        settings.author_linkedin = self.lne_linkedin_account.text()
        settings.author_twitter = self.lne_twitter_account.text()
        settings.author_mastodon = self.lne_mastodon_account.text()

        # save it
        self.plg_settings.save_from_object(settings)

    def cbb_avatars_populate(self) -> None:
        """Populate combobox of avatars."""
        # save current index
        current_item_idx = self.cbb_qchat_avatar.currentIndex()

        # clear
        self.cbb_qchat_avatar.clear()

        # populate
        for avatar_description, avatar_path in QCHAT_USER_AVATARS.items():
            # avatar
            self.cbb_qchat_avatar.addItem(
                QIcon(QgsApplication.iconPath(avatar_path)),
                avatar_description,
            )

        # restore current index
        self.cbb_qchat_avatar.setCurrentIndex(current_item_idx)
