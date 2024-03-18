from pathlib import Path
from typing import Dict, List

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QModelIndex, Qt, QUrl
from qgis.PyQt.QtGui import (
    QCursor,
    QDesktopServices,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from qgis.PyQt.QtWidgets import QAction, QDialog, QListView, QMenu, QWidget

from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.gui.form_rdp_news import RdpNewsForm
from qtribu.logic import RssItem, WebViewer
from qtribu.logic.json_feed import JsonFeedClient
from qtribu.toolbelt import PlgLogger, PlgOptionsManager


class GeotribuContentsDialog(QDialog):
    contents: Dict[int, List[RssItem]] = {}

    def __init__(self, parent: QWidget = None):
        """
        QDialog for geotribu contents

        :param parent: parent widget or application
        :type parent: QgsDockWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        self.json_feed_client = JsonFeedClient()
        self.web_viewer = WebViewer()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # buttons actions
        self.form_rdp_news = None
        self.submit_article_button.clicked.connect(self.submit_article)
        self.submit_news_button.clicked.connect(self.submit_news)
        self.donate_button.clicked.connect(self.donate)
        self.refresh_list_button.clicked.connect(self.refresh_list)

        # search actions
        self.search_line_edit.textChanged.connect(self.on_search_text_changed)

        # articles lists and treeviews
        self.contents_list_view = QListView()
        self.contents_model = QStandardItemModel(self.contents_list_view)
        self.contents_tree_view.setModel(self.contents_model)
        self.contents_tree_view.doubleClicked.connect(self.on_content_double_clicked)
        self.contents_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contents_tree_view.customContextMenuRequested.connect(
            self.on_open_content_context_menu
        )

        self.refresh_list(expand_all=True)

    @staticmethod
    def _open_url_in_browser(url: str) -> None:
        QDesktopServices.openUrl(QUrl(url))

    def _open_url_in_webviewer(self, url: str, window_title: str) -> None:
        self.web_viewer.display_web_page(url)
        self.web_viewer.set_window_title(window_title)

    def submit_article(self) -> None:
        self._open_url_in_browser(
            "https://github.com/geotribu/website/issues/new?labels=contribution+externe%2Carticle%2Ctriage&projects=&template=ARTICLE.yml"
        )

    def submit_news(self) -> None:
        self.log("Opening form to submit a news")
        if not self.form_rdp_news:
            self.form_rdp_news = RdpNewsForm()
            self.form_rdp_news.setModal(True)
            self.form_rdp_news.finished.connect(self._post_form_rdp_news)
        self.form_rdp_news.show()

    def donate(self) -> None:
        self._open_url_in_browser("https://fr.tipeee.com/geotribu")

    def refresh_list(self, expand_all: bool = False) -> None:
        # fetch last RSS items using JSONFeed
        rss_contents = self.json_feed_client.fetch(query=self.search_line_edit.text())
        years = sorted(set([c.date_pub.year for c in rss_contents]), reverse=True)
        self.contents = {
            y: [c for c in rss_contents if c.date_pub.year == y] for y in years
        }
        # save expanded item states
        expanded = [
            expand_all
            or self.contents_tree_view.isExpanded(self.contents_model.index(i, 0))
            for i in range(len(years))
        ]

        # clean treeview items
        self.contents_model.clear()

        # populate treeview
        for i, year in enumerate(years):
            # create root item for year
            year_item = self._build_root_item(year)
            self.contents_model.invisibleRootItem().appendRow(year_item)
            # create contents items
            for content in self.contents[year]:
                content_item = self._build_item_from_content(content)
                year_item.setChild(year_item.rowCount(), 0, content_item)
            self.contents_tree_view.setExpanded(
                self.contents_model.index(i, 0), expanded[i]
            )

    def on_search_text_changed(self) -> None:
        # do nothing if text is too small
        current = self.search_line_edit.text()
        if current == "":
            self.refresh_list(expand_all=True)
            return
        if len(current) < 3:
            return
        self.refresh_list()

    @staticmethod
    def _build_root_item(year: int) -> QStandardItem:
        item = QStandardItem(str(year))
        item.setEditable(False)
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        return item

    @staticmethod
    def _build_item_from_content(content: RssItem) -> QStandardItem:
        icon_file = (
            "logo_orange_no_text"
            if "Revue de presse" in content.title
            else "logo_green_no_text"
        )
        icon = QIcon(str(DIR_PLUGIN_ROOT / f"resources/images/{icon_file}.svg"))
        text = "{date_pub} - {title} ({authors}) - {tags}".format(
            date_pub=content.date_pub.strftime("%d.%m"),
            title=content.title,
            authors=",".join(content.author),
            tags=",".join(content.categories),
        )
        item = QStandardItem(icon, text)
        item.setEditable(False)
        return item

    def on_content_double_clicked(self, index: QModelIndex) -> None:
        # if parent year item has been double clicked
        if index.parent().row() < 0:
            return
        year = list(self.contents)[index.parent().row()]
        content = self.contents[year][index.row()]
        self._open_url_in_webviewer(content.url, content.title)

    def on_open_content_context_menu(self) -> None:
        selected_index = next(i for i in self.contents_tree_view.selectedIndexes())
        # if parent year item has been selected
        if selected_index.parent().row() < 0:
            return
        year = list(self.contents)[selected_index.parent().row()]
        content = self.contents[year][selected_index.row()]

        content_menu = QMenu("Content menu", self)

        # open in browser action
        open_browser_action = QAction(self.tr("Open in browser"), self)
        open_browser_action.triggered.connect(
            lambda checked: self._open_url_in_browser(content.url)
        )
        content_menu.addAction(open_browser_action)

        # open in webviewer action
        open_webviewer_action = QAction(self.tr("Open in webviewer"), self)
        open_webviewer_action.triggered.connect(
            lambda checked: self._open_url_in_webviewer(content.url, content.title)
        )
        content_menu.addAction(open_webviewer_action)

        content_menu.exec(QCursor.pos())
