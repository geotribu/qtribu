#! python3  # noqa: E265

"""
    Form to submit a news for a GeoRDP.
TODO: markdown highlight https://github.com/rupeshk/MarkdownHighlighter/blob/master/editor.py
https://github.com/baudren/NoteOrganiser/blob/devel/noteorganiser/syntax.py
"""

# standard
from functools import partial
from pathlib import Path
from urllib.parse import urlparse

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QDialog

# plugin
from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.constants import GEORDP_NEWS_CATEGORIES, GEORDP_NEWS_ICONS, GeotribuImage
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager


class RdpNewsForm(QDialog):
    """QDialog form to submit a news to a next GeoRDP."""

    LOCAL_CDN_PATH: Path = Path().home() / ".geotribu/cdn/"

    def __init__(self, parent=None):
        """Constructor.

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        uic.loadUi(Path(__file__).parent / "{}.ui".format(Path(__file__).stem), self)

        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        self.qntwk = NetworkRequestsManager()

        # custom icon
        self.setWindowIcon(QIcon(str(DIR_PLUGIN_ROOT / "resources/images/news.png")))

        # title
        self.lne_title.textChanged.connect(self.auto_preview)

        # populate combobox of news category
        self.cbb_category.addItem("", None)
        for rdp_category in GEORDP_NEWS_CATEGORIES:
            self.cbb_category.addItem(rdp_category.name)
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

        # connect help button
        self.btn_box.helpRequested.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl("https://static.geotribu.fr/contribuer/rdp/add_news/"),
            )
        )

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

        self.cbb_icon.setCurrentIndex(current_item_idx)

    def cbb_icon_selected(self) -> None:
        """Download selected icon locally if it doesn't exist already."""
        selected_icon: GeotribuImage = self.cbb_icon.currentData()
        if not selected_icon:
            return

        icon_local_path = selected_icon.local_path()
        if not icon_local_path.is_file():
            self.log(message=f"icon not exists: {icon_local_path}", log_level=4)
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
            icon_local_path = Path(
                self.LOCAL_CDN_PATH / icon_remote_url_parsed.path[1:]
            )
            md_txt += f"\n![selected_icon.description]({icon_local_path})\n"
        else:
            md_txt += "\n"

        md_txt += f"\n{self.txt_body.toPlainText()}\n"

        # show it
        self.txt_preview.clear()
        self.txt_preview.setMarkdown(md_txt)
