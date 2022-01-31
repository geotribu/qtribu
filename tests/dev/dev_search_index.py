#! python3  # noqa: E265

# -- IMPORTS ---------------------------------------------------------------------
# standard
import json
import logging
import webbrowser
from collections import defaultdict
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Union

# 3rd party
import requests

# PyQGIS
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# -- CLASSES ---------------------------------------------------------------------


class SearchWidget(QWidget):

    URL_REMOTE: str = "https://static.geotribu.fr/"
    INDEX_LOCAL_PATH: Path = Path().home() / ".geotribu/geotribu_search_index.json"

    def __init__(
        self, parent=None, search_index_path: str = "search/search_index.json"
    ):
        """Instantiate the search widget.

        :param parent: parent window, defaults to None
        :type parent: Qt Window, optional
        :param search_index_path: relative to the URL_REMOTE, defaults to "search/search_index.json"
        :type search_index_path: str, optional
        """
        super(SearchWidget, self).__init__(parent)

        # attributes
        self.INDEX_REMOTE_URL: str = f"{self.URL_REMOTE}{search_index_path}"

        self.setWindowTitle("Geotribu search widget")

        # drop-down list for tags
        self.cbb_tags = QComboBox()
        self.cbb_tags.activated.connect(self.update_search_form)
        self.cbb_tags.setEditable(True)
        self.cbb_tags.completer().setCompletionMode(QCompleter.PopupCompletion)
        # self.cbb_tags.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.cbb_tags.setInsertPolicy(QComboBox.NoInsert)

        # results
        self.results_count = QLCDNumber()
        self.tab_results = QTableWidget()
        self.tab_results.setColumnCount(3)
        self.tab_results.setHorizontalHeaderLabels(["Title", "Type", "Open"])
        self.tab_results.horizontalHeader().setStretchLastSection(True)
        self.tab_results.resizeColumnsToContents()
        self.tab_results.resizeRowsToContents()
        self.tab_results.setSortingEnabled(True)

        # layouts
        lyt_global = QGridLayout()
        lyt_filters = QHBoxLayout()
        lyt_results = QVBoxLayout()
        lyt_filters.addWidget(self.cbb_tags)
        lyt_filters.addWidget(self.results_count)
        lyt_global.addLayout(lyt_filters, 0, 0)
        lyt_results.addWidget(QLabel("Search results:"))
        lyt_results.addWidget(self.tab_results)
        lyt_global.addLayout(lyt_results, 1, 0)
        self.setLayout(lyt_global)

        # download and load search index
        self.download_search_index()
        self.search_index: dict = self.load_search_index()

        # update search form
        self.reset_search_form()

    def download_search_index(self, expiration_hours: int = 168) -> None:
        """Download search index from remote URL only if the local file is older than
        the expiration delta.

        :param expiration_hours: expiration delta in hours, defaults to 168 (= 1 week)
        :type expiration_hours: int, optional
        """
        if self.INDEX_LOCAL_PATH.exists():
            f_creation = datetime.fromtimestamp(self.INDEX_LOCAL_PATH.stat().st_ctime)
            if (datetime.now() - f_creation) < timedelta(hours=expiration_hours):
                logging.debug("Search index is up to date. Using existing local file.")
                return
            else:
                self.INDEX_LOCAL_PATH.unlink()

        self.INDEX_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url=self.INDEX_REMOTE_URL, stream=True) as req:
            with self.INDEX_LOCAL_PATH.open(mode="wb") as f:
                for chunk in req.iter_content(chunk_size=16 * 1024):
                    if chunk:
                        f.write(chunk)
        logging.debug(f"Downloaded search index to {self.INDEX_LOCAL_PATH}")
        return

    def load_search_index(self) -> dict:
        """Load search index from local file.

        :return: search index
        :rtype: dict
        """
        with self.INDEX_LOCAL_PATH.open(mode="r", encoding="UTF8") as in_json:
            search_index = json.load(in_json)
        logging.debug(f"Loaded search index from {self.INDEX_LOCAL_PATH}")
        return search_index

    def reset_search_form(self) -> None:
        """Reset search form."""
        # clear filters list
        self.cbb_tags.clear()
        self.dico_contents_by_tag: defaultdict = defaultdict(list)

        for d in self.search_index.get("docs"):
            doc_location: str = d.get("location")
            d_type = self.extract_type(item_location=doc_location)
            d_year = self.extract_year(item_location=doc_location, min_year=2020)
            d_full_url = self.is_full_url(item_location=doc_location)
            if not all([d_type, d_year, d_full_url]):
                continue
            for t in d.get("tags"):
                self.dico_contents_by_tag[t].append(
                    self.search_index.get("docs").index(d)
                )
        self.cbb_tags.addItems(sorted(list(self.dico_contents_by_tag.keys())))

    def update_search_form(self) -> None:
        """Update search form."""
        # Save search form
        search_terms: dict = {
            "tag": self.cbb_tags.currentText(),
        }

        logging.debug(f"Search terms: {search_terms}")

        results = self.dico_contents_by_tag.get(search_terms.get("tag"))
        self.results_count.display(len(results))

        self.tab_results.setRowCount(len(results))
        for i, r in enumerate(results):
            d = self.search_index.get("docs")[r]

            # first column: title
            item_title = QTableWidgetItem(d.get("title"))
            item_title.setToolTip(d.get("text"))
            self.tab_results.setItem(i, 0, item_title)

            # second column: type
            self.tab_results.setItem(
                i,
                1,
                QTableWidgetItem(self.extract_type(item_location=d.get("location"))),
            )

            # third column: button
            item_open = QPushButton("Open")
            item_open.clicked.connect(
                lambda: self.open_item_url(url_part=d.get("location"))
            )
            self.tab_results.setCellWidget(i, 2, item_open)

        self.tab_results.horizontalHeader().setStretchLastSection(True)

    def open_item_url(self, url_part: str):
        """Open URL using the default web browser.

        :param url_part: part of URL to the item
        :type url_part: str
        """
        webbrowser.open_new_tab(url=f"{self.URL_REMOTE}{url_part}")

    # -- Index manipulations -----------------------------------------------------------
    @lru_cache(maxsize=254)
    def is_full_url(self, item_location: str) -> bool:
        """Return True is it's a full URL or False if it's an anchor.

        :param item_location: content path
        :type item_location: str

        :return: [description]
        :rtype: bool
        """
        return "#" not in item_location

    @lru_cache(maxsize=254)
    def extract_type(self, item_location: str) -> Union[str, None]:
        """Extract the type of the item.

        :param item_location: content path
        :type item_location: str

        :return: content type ('article' or 'rdp')
        :rtype: Union[int, None]
        """
        if item_location.startswith("articles"):
            return "article"
        elif item_location.startswith("rdp"):
            return "rdp"
        else:
            return None

    @lru_cache(maxsize=254)
    def extract_year(
        self, item_location: str, min_year: int = 2020
    ) -> Union[int, None]:
        """Extract the year of the item.

        :param item_location: content path
        :type item_location: str
        :param min_year: minimum year to filter on, defaults to 2020
        :type min_year: int, optional

        :return: content publication year
        :rtype: Union[int, None]

        """
        loc_split = item_location.split("/")
        if len(loc_split) > 2:
            if loc_split[1].isdigit():
                year = int(loc_split[1])
                if year >= min_year:
                    return year
        else:
            return None


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        format="%(asctime)s: %(levelname)s: %(message)s", level=logging.DEBUG
    )

    # create the application and the main window
    try:
        app = QApplication(sys.argv)
        combodemo = SearchWidget()
        combodemo.show()

    except Exception as exp:
        logging.error(exp)
    sys.exit(app.exec_())


# #############################################################################
# ##### QGIS Console ###############
# ##################################
if __name__ == "__console__":
    combodemo = SearchWidget()
    combodemo.show()
