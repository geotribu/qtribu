# standard
from functools import partial
from pathlib import Path
from urllib.parse import urlparse

# PyQGIS
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialog

# plugin
from qtribu.constants import GEORDP_NEWS_CATEGORIES, GEORDP_NEWS_ICONS
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

        # populate combobox of news category
        for rdp_category in GEORDP_NEWS_CATEGORIES:
            self.cbb_category.addItem(rdp_category.name)
            self.cbb_category.setItemData(
                rdp_category.order - 1, rdp_category.description, Qt.ToolTipRole
            )

        # populate combobox of news icons
        self.cbb_icon.addItem("", None)
        for rdp_icon in GEORDP_NEWS_ICONS:
            if rdp_icon.kind != "icon":
                continue
            self.cbb_icon.addItem(rdp_icon.name, rdp_icon.url)
            self.cbb_icon.setItemData(
                GEORDP_NEWS_ICONS.index(rdp_icon) + 1,
                rdp_icon.description,
                Qt.ToolTipRole,
            )
        self.cbb_icon.textActivated.connect(self.cbb_icon_selected)

        # connect help button
        self.btn_box.helpRequested.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl("https://static.geotribu.fr/contribuer/rdp/add_news/"),
            )
        )

    def cbb_icon_selected(self) -> None:
        """Download selected icon locally if it doesn't exist already."""

        icon_remote_url = self.cbb_icon.currentData()
        icon_remote_url_parsed = urlparse(icon_remote_url)
        icon_local_path = Path(self.LOCAL_CDN_PATH / icon_remote_url_parsed.path[1:])
        if not icon_local_path.is_file():
            self.log(message=f"icon not exists: {icon_local_path}", log_level=4)
            icon_local_path.parent.mkdir(parents=True, exist_ok=True)
            self.qntwk.download_file(
                remote_url=icon_remote_url,
                local_path=str(icon_local_path.resolve()),
            )
