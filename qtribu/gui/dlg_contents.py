#! python3  # noqa: E265

"""
QDialog to browse Geotribu contents.
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional

from qgis.core import QgsApplication
from qgis.PyQt import QtCore, QtWidgets, uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QTreeWidgetItem, QWidget

from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.gui.form_article import ArticleForm
from qtribu.gui.form_rdp_news import RdpNewsForm
from qtribu.logic import RssItem
from qtribu.logic.json_feed import JsonFeedClient
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser, open_url_in_webviewer

# -- GLOBALS --

ICON_ARTICLE = QIcon(str(DIR_PLUGIN_ROOT.joinpath("resources/images/article.svg")))
ICON_GEORDP = QIcon(str(DIR_PLUGIN_ROOT.joinpath("resources/images/geordp.svg")))
MARKER_VALUE = "---"

# -- CLASSES --


class GeotribuContentsDialog(QDialog):
    contents: Dict[int, List[RssItem]] = {}

    def __init__(self, parent: Optional[QWidget] = None):
        """
        QDialog for geotribu contents

        :param parent: parent widget or application
        :type parent: QgsDockWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        self.json_feed_client = JsonFeedClient()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)
        self.setWindowIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_green_no_text.svg"))
        )

        # buttons actions
        self.form_article = None
        self.form_rdp_news = None
        self.btn_submit_article.clicked.connect(self.submit_article)
        self.btn_submit_article.setIcon(
            QgsApplication.getThemeIcon("mActionEditTable.svg")
        )
        self.btn_submit_news.clicked.connect(self.submit_news)
        self.btn_submit_news.setIcon(QgsApplication.getThemeIcon("mActionAllEdits.svg"))
        self.btn_donate.clicked.connect(self.donate)
        self.btn_donate.setIcon(
            QgsApplication.getThemeIcon("mIconCertificateTrusted.svg")
        )

        # search actions
        self.lne_search.textChanged.connect(self.on_search_text_changed)

        # authors combobox
        self.cbb_authors.addItem(MARKER_VALUE)
        for author in self.json_feed_client.authors():
            self.cbb_authors.addItem(author)
        self.cbb_authors.currentTextChanged.connect(self.on_author_changed)

        # categories combobox
        self.cbb_tags.addItem(MARKER_VALUE)
        for cat in self.json_feed_client.categories():
            if cat not in ("article", "revue de presse"):
                self.cbb_tags.addItem(cat)
        self.cbb_tags.currentTextChanged.connect(self.on_category_changed)

        # tree widget initialization
        self.tree_contents.setHeaderLabels(
            [
                self.tr("Date"),
                self.tr("Title"),
                self.tr("Author(s)"),
                self.tr("Categories"),
            ]
        )
        self.tree_contents.itemClicked.connect(self.on_tree_view_item_click)

        self.refresh_list(lambda: self.lne_search.text())
        self.tree_contents.expandAll()

    def submit_article(self) -> None:
        """
        Submit article action
        Usually launched when clicking on button
        """
        self.log("Opening form to submit an article")
        if not self.form_article:
            self.form_article = ArticleForm()
            self.form_article.setModal(True)
            self.form_article.finished.connect(self._post_form_article)
        self.form_article.show()

    def _post_form_article(self, dialog_result: int) -> None:
        """Perform actions after the article form has been closed.

        :param dialog_result: dialog's result code. Accepted (1) or Rejected (0)
        :type dialog_result: int
        """
        if self.form_article:
            # if accept button, save user inputs
            if dialog_result == 1:
                self.form_article.wdg_author.save_settings()
            # clean up
            self.form_article.deleteLater()
            self.form_article = None

    def submit_news(self) -> None:
        """
        Submit RDP news action
        Usually launched when clicking on button
        """
        self.log("Opening form to submit a news")
        if not self.form_rdp_news:
            self.form_rdp_news = RdpNewsForm()
            self.form_rdp_news.setModal(True)
            self.form_rdp_news.finished.connect(self._post_form_rdp_news)
        self.form_rdp_news.show()

    def _post_form_rdp_news(self, dialog_result: int) -> None:
        """Perform actions after the GeoRDP news form has been closed.

        :param dialog_result: dialog's result code. Accepted (1) or Rejected (0)
        :type dialog_result: int
        """
        if self.form_rdp_news:
            # if accept button, save user inputs
            if dialog_result == 1:
                self.form_rdp_news.wdg_author.save_settings()
            # clean up
            self.form_rdp_news.deleteLater()
            self.form_rdp_news = None

    def donate(self) -> None:
        """
        Donate action
        Usually launched when clicking on button
        """
        open_url_in_browser("https://geotribu.fr/team/sponsoring/")

    def refresh_list(self, query_action: Callable[[], str]) -> None:
        """
        Refresh content list as well as treewidget that list all contents

        :param query_action: action to call for potentially filtering contents
        :type query_action: Callable[[], str]
        """
        # fetch last RSS items using JSONFeed
        rss_contents = self.json_feed_client.fetch(query=query_action())
        years = sorted(set([c.date_pub.year for c in rss_contents]), reverse=True)
        self.contents = {
            y: [c for c in rss_contents if c.date_pub.year == y] for y in years
        }

        # clean treeview items
        self.tree_contents.clear()

        # populate treewidget
        items = []
        for i, year in enumerate(years):
            # create root item for year
            item = QTreeWidgetItem([str(year)])
            # create contents items
            for content in self.contents[year]:
                child = self._build_tree_widget_item_from_content(content)
                item.addChild(child)
            items.append(item)
        self.tree_contents.insertTopLevelItems(0, items)
        self.tree_contents.expandAll()
        self.tableTunning()

    def tableTunning(self):
        """Prettify table aspect"""
        # fit to content
        self.tree_contents.resizeColumnToContents(0)
        self.tree_contents.resizeColumnToContents(1)
        self.tree_contents.resizeColumnToContents(2)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def on_tree_view_item_click(self, item: QTreeWidgetItem, column: int):
        """
        Method called when a content item is clicked

        :param item: item that is clicked by user
        :type item: QTreeWidgetItem
        :param column: column that is clicked by user
        :type column: int
        """
        # open URL of content (in column at index 4 which is not displayed)
        url, title = item.text(4), item.text(1)
        open_url_in_webviewer(url, title)

    def on_search_text_changed(self) -> None:
        """
        Method called when search box is changed
        Should get search
        """
        # do nothing if text is too small
        current = self.lne_search.text()
        if current == "":
            self.refresh_list(lambda: current)
            return
        if len(current) < 3:
            return
        self.refresh_list(lambda: current)

    def on_author_changed(self, value: str) -> None:
        """
        Function triggered when author combobox is changed

        :param value: text value of the selected author
        :type value: str
        """
        self.lne_search.setText("")
        if value == MARKER_VALUE:
            self.refresh_list(lambda: self.lne_search.text())
            return
        self.refresh_list(lambda: value)

    def on_category_changed(self, value: str) -> None:
        """
        Function triggered when category/tag combobox is changed

        :param value: text value of the selected category
        :type value: str
        """
        self.lne_search.setText("")
        if value == MARKER_VALUE:
            self.refresh_list(lambda: self.lne_search.text())
            return
        self.refresh_list(lambda: value)

    @staticmethod
    def _build_tree_widget_item_from_content(content: RssItem) -> QTreeWidgetItem:
        """
        Builds a QTreeWidgetItem from a RSS content item

        :param content: content to generate item for
        :type content: RssItem
        """
        tags = ", ".join(
            [t for t in content.categories if t not in ("article", "revue de presse")]
        )

        item = QTreeWidgetItem(
            [
                content.date_pub.strftime("%d %B"),
                content.title,
                ", ".join(content.author),
                tags,
                content.url,
            ]
        )
        for i in range(4):
            item.setToolTip(i, content.abstract)
        icon_file = ICON_GEORDP if "Revue de presse" in content.title else ICON_ARTICLE

        item.setIcon(1, icon_file)
        return item
