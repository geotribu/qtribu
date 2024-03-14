from datetime import datetime
from typing import List, Any, Dict, Optional

from qtribu.__about__ import __title__, __version__
from qtribu.logic import RssItem
from qtribu.toolbelt import PlgOptionsManager, PlgLogger

import requests
from requests import Response

HEADERS: dict = {
    b"Accept": b"application/json",
    b"User-Agent": bytes(f"{__title__}/{__version__}", "utf8"),
}

FETCH_UPDATE_INTERVAL_SECONDS = 7200


class JsonFeedClient:
    items: Optional[List[RssItem]] = None
    last_fetch_date: Optional[datetime] = None

    def __init__(
        self, url: str = PlgOptionsManager.get_plg_settings().json_feed_source
    ):
        """Class initialization."""
        self.log = PlgLogger().log
        self.url = url

    def fetch(self, query: str = "") -> List[RssItem]:
        if not self.items or (
            self.last_fetch_date
            and (datetime.now() - self.last_fetch_date).total_seconds()
            > FETCH_UPDATE_INTERVAL_SECONDS
        ):
            r: Response = requests.get(self.url, headers=HEADERS)
            r.raise_for_status()
            self.items = [self._map_item(i) for i in r.json()["items"]]
            self.last_fetch_date = datetime.now()
        return [i for i in self.items if self._matches(query, i)]

    @staticmethod
    def _map_item(item: Dict[str, Any]) -> RssItem:
        return RssItem(
            abstract=item.get("content_html"),
            author=[i["name"] for i in item.get("authors")],
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
        """Moteur de recherche du turfu"""
        return (
            query.upper() in item.abstract.upper()
            or query.upper() in ",".join(item.author).upper()
            or query.upper() in ",".join(item.categories).upper()
            or query.upper() in item.date_pub.isoformat().upper()
            or query.upper() in item.image_url.upper()
            or query.upper() in item.title.upper()
            or query.upper() in item.url.upper()
        )
