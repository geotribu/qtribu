#! python3  # noqa: E265


"""
    Search within Geotribu contents.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import json
from pathlib import Path

# project
from qtribu.toolbelt import PlgLogger
from qtribu.toolbelt.file_downloader import get_from_http

# ############################################################################
# ########## Classes ###############
# ##################################


class SearchWidget:
    """Search widget within Geotribu contents."""

    INDEX_PATH: Path = Path().home() / ".geotribu/geotribu_search_index.json"

    def __init__(self):
        """Class initialization."""
        self.log = PlgLogger().log
        self.INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    def download_search_index(self):
        """Download search index from Geotribu."""
        get_from_http(
            uri="https://static.geotribu.fr/search/search_index.json",
            output_path=str(self.INDEX_PATH.resolve()),
        )

    def load_search_index(self):
        """Load search index from local file."""
        if not self.INDEX_PATH.exists():
            self.download_search_index()

        with self.INDEX_PATH.open(mode="r", encoding="UTF8") as in_json:
            search_index = json.load(in_json)

        self.log(search_index.keys())
        self.log(len(search_index.get("docs")))
