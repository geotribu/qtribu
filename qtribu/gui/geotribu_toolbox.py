from pathlib import Path

from PyQt5.QtCore import QModelIndex, Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView
from qgis.gui import QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

from qtribu.gui.form_rdp_news import RdpNewsForm
from qtribu.logic.rss_reader import RssArticlesMiniReader, RssRdpMiniReader
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager


class GeotribuToolbox(QgsDockWidget):
    def __init__(self, parent: QWidget = None):
        """
        QgsDockWidget for geotribu toolbox

        :param parent: parent widget or application
        :type parent: QgsDockWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # articles lists and treeviews
        self.articles_list_view = QListView()
        self.articles_model = QStandardItemModel(self.articles_list_view)
        self.articles_tree_view.setModel(self.articles_model)
        self.articles_tree_view.doubleClicked.connect(self.on_article_double_clicked)
        self.articles_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.articles_tree_view.customContextMenuRequested.connect(
            self.on_open_article_context_menu
        )

        # RDP lists and treeviews
        self.rdp_list_view = QListView()
        self.rdp_model = QStandardItemModel(self.rdp_list_view)
        self.rdp_tree_view.setModel(self.rdp_model)
        self.rdp_tree_view.doubleClicked.connect(self.on_article_double_clicked)
        self.rdp_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rdp_tree_view.customContextMenuRequested.connect(
            self.on_open_article_context_menu
        )

        # buttons actions
        self.form_rdp_news = None
        self.submit_article_button.clicked.connect(self.submit_new_article)
        self.refresh_articles_list_button.clicked.clicked(self.refresh_articles_list)
        self.submit_news_button.clicked.connect(self.submit_news)
        self.refresh_articles_list_button.clicked.clicked(self.refresh_rdp_list)

        self.refresh_articles_list()
        self.refresh_rdp_list()

    # region articles

    def submit_new_article(self) -> None:
        self.log("Opening form to submit a new article")
        github_url = "https://github.com/geotribu/website/issues/new?assignees=aurelienchaumet%2Cguts%2Cigeofr&labels=contribution+externe%2Crdp%2Ctriage&projects=&template=RDP_NEWS.yml"
        QDesktopServices.openUrl(QUrl(github_url))

    def refresh_articles_list(self) -> None:
        self.log("Refreshing articles list")
        # clean article items
        self.articles_model.clear()
        # fetch last RSS items
        qntwk = NetworkRequestsManager()
        rss_reader = RssArticlesMiniReader()
        rss_reader.read_feed(qntwk.get_from_source(headers=rss_reader.HEADERS))
        # create QStandardItems with RSS items and add them to treeview's model
        articles = rss_reader.latest_items()
        for article in articles:
            article_item = QStandardItem(article.title)
            article_item.setEditable(False)
            self.articles_model.invisibleRootItem().appendRow(article_item)

    def on_article_double_clicked(self, index: QModelIndex) -> None:
        self.log(f"Opening article at index {index}")
        # TODO: open article in QWeb window

    def on_open_article_context_menu(self) -> None:
        selected_index = next(i for i in self.articles_tree_view.selectedIndexes())
        self.log(f"Opening article at index {selected_index}")
        # TODO: add actions when right-clic on an article item: open in browser, open in QWeb, open GitHub PR, contact author...

    # endregion

    # region GeoRDP

    def submit_news(self) -> None:
        self.log("Opening form to submit a news")
        if not self.form_rdp_news:
            self.form_rdp_news = RdpNewsForm()
            self.form_rdp_news.setModal(True)
            self.form_rdp_news.finished.connect(self._post_form_rdp_news)
        self.form_rdp_news.show()

    def on_form_rdp_news_finished(self, dialog_result: int) -> None:
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

    def refresh_rdp_list(self) -> None:
        self.log("Refreshing RDP list")
        # clean articles_tree_view QTreeView items
        self.rdp_model.clear()
        # fetch last RSS items
        qntwk = NetworkRequestsManager()
        rss_reader = RssRdpMiniReader()
        rss_reader.read_feed(qntwk.get_from_source(headers=rss_reader.HEADERS))
        # create QStandardItems with RSS items
        rdps = rss_reader.latest_items()
        for rdp in rdps:
            rdp_item = QStandardItem(rdp.title)
            rdp_item.setEditable(False)
            self.rdp_model.invisibleRootItem().appendRow(rdp_item)

    def on_rdp_double_clicked(self, index: QModelIndex) -> None:
        self.log(f"Opening RDP at index {index}")
        # TODO: open RDP in QWeb window

    def on_open_rdp_context_menu(self) -> None:
        selected_index = next(i for i in self.rdp_tree_view.selectedIndexes())
        self.log(f"Opening RDP at index {selected_index}")
        # TODO: add actions when right-clic on a RDP item: open in browser, open in QWeb, open GitHub PR, contact authors...

    # endregion
