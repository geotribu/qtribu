from functools import partial
from pathlib import Path
from typing import Callable, Dict, List

from qgis.PyQt import QtCore, QtWidgets, uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QTreeWidgetItem, QWidget

from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.gui.form_rdp_news import RdpNewsForm
from qtribu.logic import RssItem, WebViewer
from qtribu.logic.json_feed import JsonFeedClient
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser


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
        self.refresh_list_button.clicked.connect(
            partial(self.refresh_list, lambda: self.search_line_edit.text())
        )

        # search actions
        self.search_line_edit.textChanged.connect(self.on_search_text_changed)

        # categories combobox
        for cat in self.json_feed_client.categories():
            self.categories_combobox.addItem(cat)
        self.categories_combobox.currentTextChanged.connect(self.on_category_changed)

        # treet widget initialization
        self.contents_tree_widget.setHeaderLabels(
            ["Date", "Title", "Author(s)", "Categories"]
        )
        self.contents_tree_widget.itemClicked.connect(self.on_tree_view_item_click)

        self.refresh_list(lambda: self.search_line_edit.text())
        self.contents_tree_widget.expandAll()

    def _open_url_in_webviewer(self, url: str, window_title: str) -> None:
        self.web_viewer.display_web_page(url)
        self.web_viewer.set_window_title(window_title)

    def submit_article(self) -> None:
        """
        Submit article action
        Usually launched when clicking on button
        """
        open_url_in_browser(
            "https://github.com/geotribu/website/issues/new?labels=contribution+externe%2Carticle%2Ctriage&projects=&template=ARTICLE.yml"
        )

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
        print(item, column, item.text(column))

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

    def on_category_changed(self, value: str) -> None:
        self.refresh_list(lambda: value)

    @staticmethod
    def _build_tree_widget_item_from_content(content: RssItem) -> QTreeWidgetItem:
        """
        Builds a QTreeWidgetItem from a RSS content
        """
        item = QTreeWidgetItem(
            [
                content.date_pub.strftime("%d %B"),
                content.title,
                ",".join(content.author),
                ",".join(content.categories),
            ]
        )
        item.setToolTip(1, content.abstract)
        icon_file = (
            "logo_orange_no_text"
            if "Revue de presse" in content.title
            else "logo_green_no_text"
        )
        icon = QIcon(str(DIR_PLUGIN_ROOT / f"resources/images/{icon_file}.svg"))
        item.setIcon(1, icon)
        return item
