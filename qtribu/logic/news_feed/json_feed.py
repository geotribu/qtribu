#! python3  # noqa: E265

"""
    JSON Feed wrapper.
"""

# ############################################################################
# ########## Imports ###############
# ##################################


import json
from datetime import datetime
from typing import Any, List, Optional

# 3rd party
from qgis.PyQt.QtCore import QByteArray

# plugin
from qtribu.__about__ import __title__, __version__
from qtribu.logic.news_feed.mdl_rss_item import RssItem
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager

# -- GLOBALS --
HEADERS: dict = {
    b"Accept": b"application/json",
    b"User-Agent": bytes(f"{__title__}/{__version__}", "utf8"),
}

FETCH_UPDATE_INTERVAL_SECONDS = 7200


# -- CLASSES --


class JsonFeedClient:
    """
    Class representing a client for JSON feed built with Mkdocs website with RSS plugin.
    """

    items: Optional[List[RssItem]] = None
    last_fetch_date: Optional[datetime] = None

    def __init__(
        self, url: str = PlgOptionsManager.get_plg_settings().json_feed_source
    ):
        """Class initialization.

        :param url: JSON Feed URL, defaults to PlgOptionsManager.get_plg_settings().json_feed_source
        :type url: str, optional
        """
        self.log = PlgLogger().log
        self.url = url
        self.qntwk = NetworkRequestsManager()

    def fetch(self, query: str = "") -> list[RssItem]:
        """Fetch RSS feed items using JSON Feed

        :param query: filter to look for items matching this query, defaults to ""
        :type query: str, optional

        :return: list of RssItem objects matching the query filter
        :rtype: list[RssItem]
        """
        if not self.items or (
            self.last_fetch_date
            and (datetime.now() - self.last_fetch_date).total_seconds()
            > FETCH_UPDATE_INTERVAL_SECONDS
        ):

            response: QByteArray = self.qntwk.get_from_source(
                headers=HEADERS,
                url=self.url,
                response_expected_content_type="application/json; charset=utf-8",
            )

            self.items = [
                self._map_item(i) for i in json.loads(str(response, "UTF8"))["items"]
            ]
            self.last_fetch_date = datetime.now()

        return [i for i in self.items if self._matches(query, i)]

    def authors(self) -> list[str]:
        """Get a list of authors available in the RSS feed

        :return: list of authors
        :rtype: list[str]
        """
        authors = []
        for content in self.fetch():
            for ca in content.authors:
                authors.append(" ".join([a.title() for a in ca.split(" ")]))
        return sorted(set(authors))

    def categories(self) -> list[str]:
        """Get a list of all categories available in the RSS feed.

        :return: list of categories available in the RSS feed
        :rtype: list[str]
        """
        tags = []
        for content in self.fetch():
            tags.extend([c.lower() for c in content.categories])
        return sorted(set(tags))

    @staticmethod
    def _map_item(item: dict[str, Any]) -> RssItem:
        """Map raw JSON object coming from JSON feed to an RssItem object.

        :param item: raw JSON object
        :type item: dict[str, Any]

        :return: RssItem
        """
        return RssItem(
            abstract=item.get("content_html"),
            authors=[i["name"] for i in item.get("authors")],
            categories=item.get("tags", []),
            date_pub=datetime.fromisoformat(item.get("date_published")),
            guid=item.get("id"),
            image_length=666,
            image_type=item.get("image"),
            image_url=item.get("image"),
            title=item.get("title"),
            url=item.get("url"),
        )

    @staticmethod
    def _matches(query: str, item: RssItem) -> bool:
        """Check if item matches given query.

        :param query: filter to look for items matching this query
        :type query: str
        :param item: RssItem to check
        :type item: RssItem

        :return: True if item matches given query, False if not
        """
        words = query.split(" ")
        if len(words) > 1:
            return all([JsonFeedClient._matches(w, item) for w in words])
        return (
            query.upper() in item.abstract.upper()
            or query.upper() in ",".join(item.authors).upper()
            or query.upper() in ",".join(item.categories).upper()
            or query.upper() in item.date_pub.isoformat().upper()
            or query.upper() in item.image_url.upper()
            or query.upper() in item.title.upper()
            or query.upper() in item.url.upper()
        )
