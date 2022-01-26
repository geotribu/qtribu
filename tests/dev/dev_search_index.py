#! python3  # noqa: E265

# -- IMPORTS ---------------------------------------------------------------------
# standard
import json
import logging
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
    QHBoxLayout,
    QLCDNumber,
    QWidget,
)


# -- CLASSES ---------------------------------------------------------------------
class SearchWidget(QWidget):

    INDEX_REMOTE_URL: str = "https://static.geotribu.fr/search/search_index.json"
    INDEX_LOCAL_PATH: Path = Path().home() / ".geotribu/geotribu_search_index.json"

    def __init__(self, parent=None):
        super(SearchWidget, self).__init__(parent)

        layout = QHBoxLayout()
        self.cbb_tags = QComboBox()
        self.cbb_years = QComboBox()
        self.results_count = QLCDNumber()

        self.cbb_tags.activated.connect(self.selectionchange)
        self.cbb_years.activated.connect(self.selectionchange)

        layout.addWidget(self.cbb_tags)
        layout.addWidget(self.cbb_years)
        layout.addWidget(self.results_count)
        self.setLayout(layout)
        self.setWindowTitle("Geotribu search widget")

        # download and load search index
        self.download_search_index()
        self.search_index: dict = self.load_search_index()

        # update search form
        self.update_search_form()

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

    def selectionchange(self):
        logging.debug(f"Selected tag: {self.cbb_tags.currentText()}")
        logging.debug(f"Selected year: {self.cbb_years.currentText()}")

    def update_search_form(self):
        # Save search form
        search_terms: dict = {
            "tags": self.cbb_tags.currentText(),
            "years": self.cbb_years.currentText(),
        }

        # clear filters list
        self.cbb_tags.clear()
        self.cbb_years.clear()

        self.dico_contents_by_year: defaultdict = defaultdict(list)
        self.dico_contents_by_tag: defaultdict = defaultdict(list)

        for d in self.search_index.get("docs"):
            doc_location: str = d.get("location")
            d_type = self.extract_type(item_location=doc_location)
            d_year = self.extract_year(item_location=doc_location, min_year=2020)
            d_full_url = self.is_full_url(item_location=doc_location)
            if not all([d_type, d_year, d_full_url]):
                continue
            self.dico_contents_by_year[str(d_year)].append(d.get("title"))
            for t in d.get("tags"):
                self.dico_contents_by_tag[t].append(d.get("title"))

        self.cbb_tags.addItems(sorted(list(self.dico_contents_by_tag.keys())))
        self.cbb_years.addItems(sorted(list(self.dico_contents_by_year.keys())))
        self.results_count.display(len(self.search_index.get("docs")))

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
