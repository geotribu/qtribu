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
from urllib.parse import urlparse

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QWidget

# plugin
from qtribu.__about__ import __title__, __version__
from qtribu.constants import (
    GEORDP_NEWS_CATEGORIES,
    GEORDP_NEWS_ICONS,
    ICON_GEORDP,
    LOCAL_CDN_PATH,
    GeotribuImage,
)
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser


class RdpNewsForm(QDialog):
    """QDialog form to submit a news to a next GeoRDP."""

    ISSUE_FORM_BASE_URL: str = (
        "https://github.com/geotribu/website/issues/new?template=RDP_NEWS.yml"
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
        self.setWindowIcon(ICON_GEORDP)

        # title
        self.lne_title.textChanged.connect(self.auto_preview)

        # populate combobox of news category
        self.cbb_category.addItem("", None)
        for rdp_category in GEORDP_NEWS_CATEGORIES:
            self.cbb_category.addItem(rdp_category.name, rdp_category)
            self.cbb_category.setItemData(
                rdp_category.order - 1, rdp_category.description, Qt.ToolTipRole
            )

        # icon combobox
        self.cbb_icon_populate()
        self.cbb_icon.textActivated.connect(self.cbb_icon_selected)

        # connect preview button
        self.btn_preview.setIcon(
            QIcon(QgsApplication.iconPath("mActionShowAllLayersGray.svg"))
        )
        self.btn_preview.clicked.connect(self.generate_preview)
        self.txt_preview.setStyleSheet("background-color:transparent;")

        self.txt_body.textChanged.connect(self.auto_preview)

        # publication
        self.chb_license.setChecked(
            self.plg_settings.get_value_from_key(
                key="license_global_accept", exp_type=bool
            )
        )

        # connect standard buttons
        self.btn_box.helpRequested.connect(
            partial(
                open_url_in_browser,
                "https://contribuer.geotribu.fr/rdp/add_news/",
            )
        )
        self.btn_box.button(QDialogButtonBox.Ok).clicked.connect(self.on_btn_submit)
        self.btn_box.button(QDialogButtonBox.Ok).setDefault(True)
        self.btn_box.button(QDialogButtonBox.Ok).setText(self.tr("Submit"))

    def cbb_icon_populate(self) -> None:
        """Populate combobox of news icons."""
        # save current index
        current_item_idx = self.cbb_icon.currentIndex()

        # clear
        self.cbb_icon.clear()

        # populate
        self.cbb_icon.addItem("", None)
        for rdp_icon in GEORDP_NEWS_ICONS:
            if rdp_icon.kind != "icon":
                continue

            if rdp_icon.local_path().is_file():
                self.cbb_icon.addItem(
                    QIcon(str(rdp_icon.local_path().resolve())), rdp_icon.name, rdp_icon
                )
            else:
                self.cbb_icon.addItem(rdp_icon.name, rdp_icon)

            # icon tooltip
            self.cbb_icon.setItemData(
                GEORDP_NEWS_ICONS.index(rdp_icon) + 1,
                rdp_icon.description,
                Qt.ToolTipRole,
            )

        # restore current index
        self.cbb_icon.setCurrentIndex(current_item_idx)

    def cbb_icon_selected(self) -> None:
        """Download selected icon locally if it doesn't exist already."""
        selected_icon: GeotribuImage = self.cbb_icon.currentData()
        if not selected_icon:
            return

        icon_local_path = selected_icon.local_path()
        if not icon_local_path.is_file():
            self.log(
                message=f"Icon doesn't exist locally: {icon_local_path}", log_level=4
            )
            icon_local_path.parent.mkdir(parents=True, exist_ok=True)
            self.qntwk.download_file(
                remote_url=selected_icon.url,
                local_path=str(icon_local_path.resolve()),
            )
            # repopulate combobx to get updated items icons
            self.cbb_icon_populate()

        self.auto_preview()

    def auto_preview(self) -> None:
        """To be connected to input widgets. Triggers the preview if the related
        checkbox is checked.
        """
        if self.chb_auto_preview.isChecked():
            self.generate_preview()

    def generate_preview(self) -> None:
        """Render news in the preview area."""
        # title
        md_txt = f"### {self.lne_title.text()}\n"

        # icon
        selected_icon: GeotribuImage = self.cbb_icon.currentData()
        if selected_icon:
            icon_remote_url_parsed = urlparse(selected_icon.url)
            icon_local_path = Path(LOCAL_CDN_PATH / icon_remote_url_parsed.path[1:])
            md_txt += f"\n![selected_icon.description]({icon_local_path})\n"
        else:
            md_txt += "\n"

        md_txt += f"\n{self.txt_body.toPlainText()}\n"

        # show it
        self.txt_preview.clear()
        self.txt_preview.setMarkdown(md_txt)

    def check_required_fields(self) -> bool:
        invalid_fields = []
        error_message = ""

        # check category
        if not self.cbb_category.currentData():
            invalid_fields.append(self.cbb_category)
            error_message += self.tr("- A category is required.\n")

        # check title
        if len(self.lne_title.text()) < 3:
            invalid_fields.append(self.lne_title)
            error_message += self.tr(
                "- A title is required, with at least 3 characters.\n"
            )

        # check body
        if len(self.txt_body.toPlainText()) < 25:
            invalid_fields.append(self.txt_body)
            error_message += self.tr(
                "- News is not long enough (25 characters at least).\n"
            )

        # check license
        if not self.chb_license.isChecked():
            invalid_fields.append(self.chb_license)
            error_message += self.tr("- License must be accepted.\n")

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
            f"&dr_news_category={self.cbb_category.currentText()}"
            f"&in_news_title={self.lne_title.text()}"
            f"&in_news_icon={self.cbb_icon.currentText()}"
            f"&tx_news_content={self.txt_body.toPlainText()}"
            f"&tx_misc_comment={self.txt_comment.toPlainText()} "
            f"\n---\n\n{__title__} {__version__}"
            f"&title=[GeoRDP] {self.lne_title.text()} - {__title__} {__version__}"
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
