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

    FEED_ITEMS: tuple = None
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
