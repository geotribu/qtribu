# standard
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

# plugin
from qtribu.gui.gui_commons import QVAL_EMAIL, QVAL_URL
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
        self.lne_email.setValidator(QVAL_EMAIL)
        self.lne_github_account.setValidator(QVAL_URL)
        self.lne_linkedin_account.setValidator(QVAL_URL)
        self.lne_twitter_account.setValidator(QVAL_URL)

        # fill fields from saved settings
        self.load_settings()

    def load_settings(self) -> dict:
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # author
        self.lne_firstname.setText(settings.author_firstname)
        self.lne_lastname.setText(settings.author_lastname)
        self.lne_email.setText(settings.author_email)
        self.lne_github_account.setText(settings.author_github)
        self.lne_linkedin_account.setText(settings.author_linkedin)
        self.lne_twitter_account.setText(settings.author_twitter)

    def save_settings(self) -> None:
        """Save form text into QgsSettings."""
        # get settings
        settings = self.plg_settings.get_plg_settings()

        # store user inputs
        settings.author_firstname = self.lne_firstname.text()
        settings.author_lastname = self.lne_lastname.text()
        settings.author_email = self.lne_email.text()
        settings.author_github = self.lne_github_account.text()
        settings.author_linkedin = self.lne_linkedin_account.text()
        settings.author_twitter = self.lne_twitter_account.text()

        # save it
        self.plg_settings.save_from_object(settings)
