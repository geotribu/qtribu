#! python3  # noqa: E265

from qgis.core import QgsNewsFeedParser, QgsSettings
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import Qt

FEED_URL = "http://localhost:8000"
# FEED_URL = "https://raw.githubusercontent.com/elpaso/qgis-feed/master/qgisfeedproject/qgisfeed/fixtures/qgisfeed.json"

fifeed = QgsNewsFeedParser(QUrl(FEED_URL))

fifeed.fetch()
print(len(fifeed.entries()))
print(fifeed.keyForFeed(FEED_URL))

settings = QgsSettings()
settings.beginGroup(f"core/{fifeed.keyForFeed(FEED_URL)}")

print(settings.childKeys())

settings.setValue("disabled", False)

settings.endGroup()
