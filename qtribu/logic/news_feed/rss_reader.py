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
from pathlib import Path
from typing import Callable, Optional

# QGIS
from qgis.core import Qgis, QgsSettings
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT, __title__, __version__
from qtribu.logic.news_feed.mdl_rss_item import RssItem
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.file_stats import is_file_older_than
from qtribu.toolbelt.network_manager import NetworkRequestsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class RssMiniReader:
    """Minimalist RSS feed parser."""

    FEED_ITEMS: Optional[list[RssItem]] = None
    HEADERS: dict = {
        b"Accept": b"application/xml",
        b"User-Agent": bytes(f"{__title__}/{__version__}", "utf8"),
    }
    PATTERN_INCLUDE: list = ["articles/", "rdp/"]

    def __init__(
        self,
        action_read: Optional[QAction] = None,
        on_read_button: Optional[Callable] = None,
    ):
        """Class initialization."""
        self.log = PlgLogger().log
        self.ntwk_manager = NetworkRequestsManager()
        self.plg_settings = PlgOptionsManager.get_plg_settings()
        self.local_feed_filepath: Path = self.plg_settings.local_app_folder.joinpath(
            "rss.xml"
        )
        self.action_read = action_read
        self.on_read_button = on_read_button

    def process(self) -> None:
        """Download, parse and read RSS feed than store items as attribute."""
        # download remote RSS feed to cache folder
        self.download_feed()
        if not self.local_feed_filepath.exists():
            self.log(
                message=self.tr(
                    "The RSS feed is not available locally: {}. "
                    "Features related to the RSS reader are disabled.".format(
                        self.local_feed_filepath
                    )
                ),
                log_level=Qgis.MessageLevel.Critical,
            )
            return

        # parse the local RSS feed
        self.read_feed()

        # check if a new item has been published since last check
        if not self.has_new_content:
            self.log(
                message="No new item found in RSS feed.",
                log_level=Qgis.MessageLevel.NoLevel,
            )
            return
        # notify
        if isinstance(self.latest_item, RssItem):
            latest_item = self.latest_item
            self.log(
                message="{} {}".format(
                    self.tr("New content published:"),
                    latest_item.title,
                ),
                log_level=Qgis.MessageLevel.Success,
                push=PlgOptionsManager().get_plg_settings().notify_push_info,
                duration=PlgOptionsManager().get_plg_settings().notify_push_duration,
                button=True,
                button_label=self.tr("Read it!"),
                button_connect=self.on_read_button,
            )

            # change action icon
            if isinstance(self.action_read, QAction):
                self.action_read.setIcon(
                    QIcon(
                        str(
                            DIR_PLUGIN_ROOT / "resources/images/logo_orange_no_text.svg"
                        )
                    ),
                )

    def download_feed(self) -> bool:
        """Download RSS feed locally if it's older than latest 24 hours.

        :return: True is a new file has been downloaded.
        :rtype: bool
        """
        if is_file_older_than(
            local_file_path=self.local_feed_filepath,
            expiration_rotating_hours=self.plg_settings.rss_poll_frequency_hours,
        ):
            self.ntwk_manager.download_file_to(
                remote_url=self.plg_settings.rss_source,
                local_path=self.local_feed_filepath,
            )
            self.log(
                message=f"The remote RSS feed ({self.plg_settings.rss_source}) has been "
                f"downloaded to {self.local_feed_filepath}",
                log_level=Qgis.MessageLevel.Info,
            )
            return True
        self.log(
            message=f"A fresh local RSS feed already exists: {self.local_feed_filepath}",
            log_level=Qgis.MessageLevel.Info,
        )
        return False

    def read_feed(self) -> list[RssItem]:
        """Parse the feed XML as string and store items into an ordered list of RSS items.

        :return: list of RSS items dataclasses
        :rtype: list[RssItem]
        """
        feed_items: list[RssItem] = []
        tree = ET.parse(self.local_feed_filepath)
        items = tree.findall("channel/item")
        for item in items:
            try:
                # filter on included pattern
                if not any([i in item.find("link").text for i in self.PATTERN_INCLUDE]):
                    self.log(
                        message="Item ignored because unmatches the include pattern: {}".format(
                            item.find("title").text
                        ),
                        log_level=Qgis.MessageLevel.NoLevel,
                    )
                    continue

                # feed item object
                feed_item_obj = RssItem(
                    abstract=item.find("description").text,
                    authors=[author.text for author in item.findall("author")] or None,
                    categories=[category.text for category in item.findall("category")]
                    or None,
                    date_pub=parsedate(item.find("pubDate").text),
                    guid=item.find("guid").text,
                    image_length=item.find("enclosure").attrib.get("length"),
                    image_type=item.find("enclosure").attrib.get("type"),
                    image_url=item.find("enclosure").attrib.get("url"),
                    title=item.find("title").text,
                    url=item.find("link").text,
                )
                if item.find("enclosure") is not None:
                    item_enclosure = item.find("enclosure")
                    feed_item_obj.image_length = item_enclosure.attrib.get("length")
                    feed_item_obj.image_type = item_enclosure.attrib.get("type")
                    feed_item_obj.image_url = item_enclosure.attrib.get("url")

                # add items to the feed
                feed_items.append(feed_item_obj)
            except Exception as err:
                item_idx: Optional[int] = None
                if hasattr(items, "index"):
                    item_idx = items.index(item)

                err_msg = f"Feed item {item_idx} triggers an error. Trace: {err}"
                self.log(message=err_msg, log_level=Qgis.MessageLevel.Critical)

        # store feed items as attribute and return it
        self.FEED_ITEMS = feed_items
        return feed_items

    @property
    def latest_item(self) -> Optional[RssItem]:
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

    def latest_items(self, count: int = 36) -> list[RssItem]:
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
        if (
            isinstance(self.latest_item, RssItem)
            and self.latest_item.guid != settings.latest_content_guid
        ):
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
                log_level=Qgis.MessageLevel.NoLevel,
            )
            return False

        qsettings = QgsSettings()

        # get latest QGIS item id
        latest_geotribu_article = self.latest_item
        item_id = 99

        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/title",
            value=f"[Geotribu] {latest_geotribu_article.title}",
            section=QgsSettings.Section.App,
        )
        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/content",
            value=f"<p>{latest_geotribu_article.abstract}</p><p>"
            + self.tr("Author(s): ")
            + f"{', '.join(latest_geotribu_article.authors)}</p><p><small>"
            + self.tr("Keywords: ")
            + f"{', '.join(latest_geotribu_article.categories)}</small></p>",
            section=QgsSettings.Section.App,
        )
        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/image-url",
            value=latest_geotribu_article.image_url,
            section=QgsSettings.Section.App,
        )
        qsettings.setValue(
            key=f"news-feed/items/httpsfeedqgisorg/entries/items/{item_id}/link",
            value=latest_geotribu_article.url,
            section=QgsSettings.Section.App,
        )

        qsettings.sync()

        self.log(
            message=f"Latest Geotribu content inserted in QGIS news feed: "
            f"{latest_geotribu_article.title}",
            log_level=Qgis.MessageLevel.Info,
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
