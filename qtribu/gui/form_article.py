#! python3  # noqa: E265

"""
    Form to submit a news for a GeoRDP.
TODO: markdown highlight https://github.com/rupeshk/MarkdownHighlighter/blob/master/editor.py
https://github.com/baudren/NoteOrganiser/blob/devel/noteorganiser/syntax.py
"""

# standard
from functools import partial
from pathlib import Path
from typing import Optional, Union

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QWidget

# plugin
from qtribu.__about__ import __title__, __version__
from qtribu.constants import ICON_ARTICLE
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser


class ArticleForm(QDialog):
    """QDialog form to submit an article."""

    ISSUE_FORM_BASE_URL: str = (
        "https://github.com/geotribu/website/issues/new?template=ARTICLE.yml"
    )

    def __init__(self, parent: Optional[QWidget] = None):
        """Constructor.

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        self.qntwk = NetworkRequestsManager()

        # custom icon
        self.setWindowIcon(ICON_ARTICLE)

        # publication
        self.cbb_license.addItems(
            [
                "Creative Commons International BY-NC-SA 4.0",
                "Creative Commons International BY-SA 4.0",
                "Beerware (Révision 42)",
                "autre - merci de préciser dans le champ libre en fin de formulaire",
            ]
        )

        # connect help button
        self.btn_box.helpRequested.connect(
            partial(
                open_url_in_browser,
                "https://contribuer.geotribu.fr/articles/workflow/",
            )
        )
        self.btn_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_btn_submit)
        self.btn_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.btn_box.button(QDialogButtonBox.Ok).setText(self.tr("Submit"))

    def check_required_fields(self) -> bool:
        invalid_fields = []
        error_message = ""

        # check title
        if len(self.lne_title.text()) < 3:
            invalid_fields.append(self.lne_title)
            error_message += self.tr(
                "- A title is required, with at least 3 characters.\n"
            )

        # check description
        if len(self.txt_description.toPlainText()) < 10:
            invalid_fields.append(self.txt_description)
            error_message += self.tr(
                "- The description is not long enough (10 characters at least).\n"
            )

        # check date
        if not len(self.dte_proposed_date.date().toString("dd/MM/yyyy")):
            invalid_fields.append(self.txt_description)
            error_message += self.tr("- Date has to be filled.\n")

        # check license
        # if not self.cbb_license.isChecked():
        #     invalid_fields.append(self.chb_license)
        #     error_message += self.tr("- License must be accepted.\n")

        # check author firstname
        if len(self.wdg_author.lne_firstname.text()) < 2:
            invalid_fields.append(self.wdg_author.lne_firstname)
            error_message += self.tr(
                "- For attribution purpose, author's firstname is required.\n"
            )

        # check author lastname
        if len(self.wdg_author.lne_lastname.text()) < 2:
            invalid_fields.append(self.wdg_author.lne_lastname)
            error_message += self.tr(
                "- For attribution purpose, author's lastname is required.\n"
            )

        # check author email
        if len(self.wdg_author.lne_email.text()) < 5:
            invalid_fields.append(self.wdg_author.lne_email)
            error_message += self.tr(
                "- For attribution purpose, author's email is required.\n"
            )

        # inform
        if len(invalid_fields):
            self.log(
                parent_location=self,
                message=self.tr("Some of required fields are incorrectly filled."),
                push=True,
                log_level=2,
                duration=20,
                button=True,
                button_label=self.tr("See details..."),
                button_more_text=self.tr(
                    "Fields in bold must be filled. Missing fields:\n"
                )
                + error_message,
            )
            for wdg in invalid_fields:
                wdg.setStyleSheet("border: 1px solid red;")
            return False

        return True

    def on_btn_submit(self) -> Union[bool, str, None]:
        """Check if required form fields are correctly filled and submit to Github issue
        form.

        :return: False if some check fails. True and emit accepted() signal if
            everything is ok.
        :rtype: bool
        """
        if not self.check_required_fields():
            return False

        completed_url = (
            f"{self.ISSUE_FORM_BASE_URL}"
            f"&in_author_name={self.wdg_author.lne_firstname.text()} "
            f"{self.wdg_author.lne_lastname.text()}"
            f"&in_author_mail={self.wdg_author.lne_email.text()}"
            f"&in_author_linkedin={self.wdg_author.lne_linkedin_account.text()}"
            f"&in_author_mastodon={self.wdg_author.lne_mastodon_account.text()}"
            f"&in_author_twitter={self.wdg_author.lne_twitter_account.text()}"
            f"&in_author_license=true"
            f"&cb_author_content_relationship={self.chb_transparency.isChecked()}"
            f"&in_art_title={self.lne_title.text()}"
            f"&in_art_date={self.dte_proposed_date.date().toString('dd/MM/yyyy')}"
            f"&tx_art_content={self.txt_description.toPlainText()}"
            f"&tx_misc_comment={self.txt_comment.toPlainText()} "
            f"\n---\n\n{__title__} {__version__}"
            f"&title=[Proposition] {self.lne_title.text()} - {__title__} {__version__}"
        )
        self.log(message=f"Opening issue form: {completed_url}", log_level=4)
        url_opened = open_url_in_browser(url=completed_url)
        if url_opened:
            self.log(
                message=self.tr("Issue form URL opened in default system web browser."),
                log_level=4,
            )
            super().accept()
            return True
        else:
            self.log(
                parent_location=self,
                message=self.tr(
                    "Opening issue form URL in default system web browser failed. "
                    "Check if there is any special characters in form fields and try again."
                ),
                push=True,
                duration=10,
                log_level=2,
            )
            return False
