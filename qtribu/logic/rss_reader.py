#! python3  # noqa: E265


"""
    Minimalist RSS reader.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
import xml.etree.ElementTree as ET
from email.utils import parsedate
from typing import Optional, List

# QGIS
from qgis.core import Qgis, QgsSettings
from qgis.PyQt.QtCore import QCoreApplication

# project
from qtribu.__about__ import __title__, __version__
from qtribu.logic.custom_datatypes import RssItem
from qtribu.toolbelt import PlgLogger, PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class RssMiniReader:
    """Minimalist RSS feed parser."""

    FEED_ITEMS: Optional[tuple] = None
    HEADERS: dict = {
        b"Accept": b"application/xml",
        b"User-Agent": bytes(f"{__title__}/{__version__}", "utf8"),
    }
    PATTERN_INCLUDE: list = ["articles/", "rdp/"]

    def __init__(self):
        """Class initialization."""
        self.log = PlgLogger().log

    def read_feed(self, in_xml: str) -> tuple[RssItem]:
        """Parse the feed XML as string and store items into an ordered tuple of tuples.

        :param in_xml: XML as string. Must be RSS compliant.
        :type in_xml: str

        :return: RSS items loaded as namedtuples
        :rtype: Tuple[RssItem]
        """
        feed_items = []
        tree = ET.ElementTree(ET.fromstring(in_xml))
        root = tree.getroot()
        items = root.findall("channel/item")
        for item in items:
            try:
                # filter on included pattern
                if not any([i in item.find("link").text for i in self.PATTERN_INCLUDE]):
                    logging.debug(
                        "Item ignored because unmatches the include pattern: {}".format(
                            item.find("title")
                        )
                    )
                    continue

                # add items to the feed
                feed_items.append(
                    RssItem(
                        abstract=item.find("description").text,
                        author=[author.text for author in item.findall("author")]
                        or None,
                        categories=[
                            category.text for category in item.findall("category")
                        ]
                        or None,
                        date_pub=parsedate(item.find("pubDate").text),
                        guid=item.find("guid").text,
                        image_length=item.find("enclosure").attrib.get("length"),
                        image_type=item.find("enclosure").attrib.get("type"),
                        image_url=item.find("enclosure").attrib.get("url"),
                        title=item.find("title").text,
                        url=item.find("link").text,
                    )
                )
            except Exception as err:
                err_msg = f"Feed item triggers an error. Trace: {err}"
                logger.error(err_msg)
                self.log(message=err_msg, log_level=2)

        # store feed items as attribute and return it
        self.FEED_ITEMS = feed_items
        return feed_items

    @property
    def latest_item(self) -> RssItem:
        """Returns the latest feed item, based on index 0.

        :return: latest feed item.
        :rtype: RssItem
        """
        if not self.FEED_ITEMS:
            logger.warning(
                "Feed has not been loaded, so it's impossible to "
                "return the latest item."
            )
            return None

        return self.FEED_ITEMS[0]

    def latest_items(self, count: int = 36) -> List[RssItem]:
        """Returns the latest feed items.
        :param count: number of items to fetch
        :type count: int
        :return: latest feed items
        :rtype: List[RssItem]
        """
        if count <= 0:
            raise ValueError("Number of RSS items to get must be > 0")
        if not self.FEED_ITEMS:
            logger.warning(
                "Feed has not been loaded, so it's impossible to "
                "return the latest item."
            )
            return []
        return self.FEED_ITEMS[:count]

    @property
    def has_new_content(self) -> bool:
        """Compare the saved item guid (in plugin settings) with feed latest item to \
        determine if a newer item has been published.

        :return: True is a newer item has been published.
        :rtype: bool
        """
        settings = PlgOptionsManager.get_plg_settings()
        if self.latest_item.guid != settings.latest_content_guid:
            return True
        else:
            return False

    def add_latest_item_to_news_feed(self) -> bool:
        """Check if the news feed integration is enabled. If so, insert the latest RSS
        item at the top of the news feed.

        :return: True if it worked. False if disabled or something wen wrong.
        :rtype: bool
        """

        # sample stucture:
        # news-feed\items\httpsfeedqgisorg\entries\items\64\title=It\x2019s OSM\x2019s...
        # news-feed\items\httpsfeedqgisorg\entries\items\65\content="<p>The Cyber/..</strong></p>"
        # news-feed\items\httpsfeedqgisorg\entries\items\65\expiry=@DateTime(\0\0\0\x10\0\0\0\0\0\0%\x8b\xd1\x3\xba\xe1\x38\0)
        # news-feed\items\httpsfeedqgisorg\entries\items\65\image-url=https://feed.qgis.org/media/feedimages/2023/11/09/europe.jpg
        # news-feed\items\httpsfeedqgisorg\entries\items\65\link=https://www.osgeo.org/foundation-news/eu-cyber-resilience-act/
        # news-feed\items\httpsfeedqgisorg\entries\items\65\sticky=false

        plg_settings = PlgOptionsManager.get_plg_settings()
        if not plg_settings.integration_qgis_news_feed:
            self.log(
                message="The QGIS news feed integration is disabled. Abort!",
                log_level=4,
            )
            return False

        qsettings = QgsSettings()

        # get latest QGIS item id
        latest_geotribu_article = self.latest_item
        item_id = 99

        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/title",
            value=f"[Geotribu] {latest_geotribu_article.title}",
            section=QgsSettings.App,
        )
        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/content",
            value=f"<p>{latest_geotribu_article.abstract}</p><p>"
            + self.tr("Author(s): ")
            + f"{', '.join(latest_geotribu_article.author)}</p><p><small>"
            + self.tr("Keywords: ")
            + f"{', '.join(latest_geotribu_article.categories)}</small></p>",
            section=QgsSettings.App,
        )
        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/image-url",
            value=latest_geotribu_article.image_url,
            section=QgsSettings.App,
        )
        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/link",
            value=latest_geotribu_article.url,
            section=QgsSettings.App,
        )

        qsettings.sync()

        self.log(
            message=f"Latest Geotribu content inserted in QGIS news feed: "
            f"{latest_geotribu_article.title}",
            log_level=Qgis.Info,
        )

        return True

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)


class RssArticlesMiniReader(RssMiniReader):
    PATTERN_INCLUDE: list = ["articles/"]

    def __init__(self):
        super().__init__()


class RssRdpMiniReader(RssMiniReader):
    PATTERN_INCLUDE: list = ["rdp/"]

    def __init__(self):
        super().__init__()
