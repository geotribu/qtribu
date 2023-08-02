#! python3  # noqa: E265


"""
    Search within Geotribu contents.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import json
from datetime import datetime, timedelta
from pathlib import Path

# project
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.file_downloader import get_from_http

# ############################################################################
# ########## Classes ###############
# ##################################


class SearchWidget:
    """Search widget within Geotribu contents and CDN."""

    CDN_IDX_PATH: Path = Path().home() / ".geotribu/search/cdn_search_index.json"
    CDN_IDX_EXPIRE_HOURS: int = 12
    CONTENT_IDX_PATH: Path = Path().home() / ".geotribu/search/site_search_index.json"
    CONTENT_IDX_EXPIRE_HOURS: int = 168

    def __init__(self):
        """Class initialization."""
        self.log = PlgLogger().log
        self.settings = PlgOptionsManager.get_plg_settings()

        # make sure that folders exist
        self.CONTENT_IDX_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.CDN_IDX_PATH.parent.mkdir(parents=True, exist_ok=True)

    def download_search_index(self, index_to_download: str = "content"):
        """Download search index from Geotribu."""
        if index_to_download == "content":
            remote_uri = f"{self.settings.website_url}/search/search_index.json"
            local_filepath = self.CONTENT_IDX_PATH
            expiration_hours = self.CONTENT_IDX_EXPIRE_HOURS
        elif index_to_download == "cdn":
            remote_uri = f"{self.settings.cdn_url}/img/search-index.json"
            local_filepath = self.CDN_IDX_PATH
            expiration_hours = self.CDN_IDX_EXPIRE_HOURS
        else:
            self.log(
                message=f"Unrecognized index type to download: {index_to_download}. "
                "Expected one of: 'content' or 'cdn'.",
                log_level=4,
            )

        # content search index
        if local_filepath.exists():
            f_creation = datetime.fromtimestamp(local_filepath.stat().st_ctime)
            if (datetime.now() - f_creation) < timedelta(hours=expiration_hours):
                self.log(
                    message=f"Local search index ({local_filepath}) is up to date. "
                    "No download needed.",
                    log_level=4,
                )
                return
            else:
                local_filepath.unlink()

        # download the remote file into local
        get_from_http(
            uri=remote_uri,
            output_path=str(local_filepath.resolve()),
        )

    def load_search_index(self):
        """Load search index from local file."""
        if not self.CONTENT_IDX_PATH.exists():
            self.download_search_index(index_to_download="content")
        if not self.CDN_IDX_PATH.exists():
            self.download_search_index(index_to_download="cdn")

        with self.CONTENT_IDX_PATH.open(mode="r", encoding="UTF8") as in_json:
            search_index = json.load(in_json)

        self.log(search_index.keys())
        self.log(len(search_index.get("docs")))
