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
from typing import Tuple

# project
from qtribu.__about__ import __title__, __version__
from qtribu.logic.custom_datatypes import RssItem
from qtribu.toolbelt import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class RssMiniReader:

    FEED_ITEMS: tuple = None
    PATTERN_INCLUDE = ["articles/", "rdp/"]
    HEADERS = {
        b"Accept": b"application/xml",
        b"User-Agent": bytes(f"{__title__}/{__version__}", "utf8"),
    }

    def __init__(self):
        """Minimalist RSS feed parser."""
        self.log = PlgLogger().log

    def read_feed(self, in_xml: str) -> Tuple[RssItem]:
        """Parse eth feed XML as string and store items into an ordered tuple of tuples/

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
                        author=item.find("author").text or None,
                        date_pub=parsedate(item.find("pubDate").text),
                        image_length=item.find("enclosure").attrib.get("length"),
                        image_type=item.find("enclosure").attrib.get("type"),
                        image_url=item.find("enclosure").attrib.get("url"),
                        guid=item.find("guid").text,
                        title=item.find("title").text,
                        url=item.find("link").text,
                    )
                )
            except Exception as err:
                err_msg = "Feed item (index = {}) triggers an error. Trace: {}".format(
                    items.index(item), err
                )
                logger.error(err_msg)
                self.log(message=err_msg, log_level=2)

        # store feed items as attribute and return it
        self.FEED_ITEMS = feed_items
        return feed_items

    @property
    def latest_item(self) -> RssItem:
        if not self.FEED_ITEMS:
            logger.warning(
                "Feed has not been loaded, so it's impossible to "
                "return the latest item."
            )
            return None

        return self.FEED_ITEMS[0]
