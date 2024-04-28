#! python3  # noqa: E265

"""
    Form to submit a news for a GeoRDP.
TODO: markdown highlight https://github.com/rupeshk/MarkdownHighlighter/blob/master/editor.py
https://github.com/baudren/NoteOrganiser/blob/devel/noteorganiser/syntax.py
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog

# plugin
from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.constants import GEORDP_NEWS_ICONS, GeotribuImage
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser


class ArticleForm(QDialog):
    """QDialog form to submit an article."""

    LOCAL_CDN_PATH: Path = Path().home() / ".geotribu/cdn/"

    def __init__(self, parent=None):
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
        self.setWindowIcon(QIcon(str(DIR_PLUGIN_ROOT / "resources/images/news.png")))

        # icon combobox
        self.cbb_icon_populate()
        self.cbb_icon.textActivated.connect(self.cbb_icon_selected)

        # publication
        self.chb_license.setChecked(
            self.plg_settings.get_value_from_key(
                key="license_global_accept", exp_type=bool
            )
        )

        # connect help button
        self.btn_box.helpRequested.connect(
            partial(
                open_url_in_browser,
                "https://contribuer.geotribu.fr/rdp/add_news/",
            )
        )

    def cbb_icon_populate(self) -> None:
        """Populate combobox of article icons."""
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

    def accept(self) -> bool:
        """Auto-connected to the OK button (within the button box), i.e. the `accepted`
        signal. Check if required form fields are correctly filled.

        :return: False if some check fails. True and emit accepted() signal if everything is ok.
        :rtype: bool
        """
        invalid_fields = []
        error_message = ""

        # check title
        if len(self.lne_title.text()) < 3:
            invalid_fields.append(self.lne_title)
            error_message += self.tr(
                "- A title is required, with at least 3 characters.\n"
            )

        # check description
        if len(self.txt_description.toPlainText()) < 25:
            invalid_fields.append(self.txt_description)
            error_message += self.tr(
                "- Description is not long enough (25 characters at least).\n"
            )
        if len(self.txt_description.toPlainText()) > 160:
            invalid_fields.append(self.txt_description)
            error_message += self.tr(
                "- Description is too long (160 characters at least).\n"
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
        else:
            super().accept()
            return True
