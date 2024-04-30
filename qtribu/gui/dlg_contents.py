from pathlib import Path
from typing import Callable, Dict, List

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
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)
        self.setWindowIcon(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_green_no_text.svg"))
        )

        # buttons actions
        self.form_article = None
        self.form_rdp_news = None
        self.submit_article_button.clicked.connect(self.submit_article)
        self.submit_article_button.setIcon(
            QgsApplication.getThemeIcon("mActionEditTable.svg")
        )
        self.submit_news_button.clicked.connect(self.submit_news)
        self.submit_news_button.setIcon(
            QgsApplication.getThemeIcon("mActionAllEdits.svg")
        )
        self.donate_button.clicked.connect(self.donate)
        self.donate_button.setIcon(
            QgsApplication.getThemeIcon("mIconCertificateTrusted.svg")
        )

        # search actions
        self.search_line_edit.textChanged.connect(self.on_search_text_changed)

        # authors combobox
        self.authors_combobox.addItem(MARKER_VALUE)
        for author in self.json_feed_client.authors():
            self.authors_combobox.addItem(author)
        self.authors_combobox.currentTextChanged.connect(self.on_author_changed)

        # categories combobox
        self.categories_combobox.addItem(MARKER_VALUE)
        for cat in self.json_feed_client.categories():
            self.categories_combobox.addItem(cat)
        self.categories_combobox.currentTextChanged.connect(self.on_category_changed)

        # tree widget initialization
        self.contents_tree_widget.setHeaderLabels(
            [
                self.tr("Date"),
                self.tr("Title"),
                self.tr("Author(s)"),
                self.tr("Categories"),
            ]
        )
        self.contents_tree_widget.itemClicked.connect(self.on_tree_view_item_click)

        self.refresh_list(lambda: self.search_line_edit.text())
        self.contents_tree_widget.expandAll()

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
        self.contents_tree_widget.clear()

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
        self.contents_tree_widget.insertTopLevelItems(0, items)
        self.contents_tree_widget.expandAll()

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
        current = self.search_line_edit.text()
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
        self.search_line_edit.setText("")
        if value == MARKER_VALUE:
            self.refresh_list(lambda: self.search_line_edit.text())
            return
        self.refresh_list(lambda: value)

    def on_category_changed(self, value: str) -> None:
        """
        Function triggered when category/tag combobox is changed

        :param value: text value of the selected category
        :type value: str
        """
        self.search_line_edit.setText("")
        if value == MARKER_VALUE:
            self.refresh_list(lambda: self.search_line_edit.text())
            return
        self.refresh_list(lambda: value)

    @staticmethod
    def _build_tree_widget_item_from_content(content: RssItem) -> QTreeWidgetItem:
        """
        Builds a QTreeWidgetItem from a RSS content item

        :param content: content to generate item for
        :type content: RssItem
        """
        item = QTreeWidgetItem(
            [
                content.date_pub.strftime("%d %B"),
                content.title,
                ",".join(content.author),
                ",".join(content.categories),
                content.url,
            ]
        )
        for i in range(4):
            item.setToolTip(i, content.abstract)
        icon_file = ICON_GEORDP if "Revue de presse" in content.title else ICON_ARTICLE

        item.setIcon(1, icon_file)
        return item
