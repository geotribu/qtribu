#! python3  # noqa: E265

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.Qt import QByteArray, QUrl
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtNetwork import QNetworkRequest

from qtribu.logic import RssMiniReader

rss_rdr = RssMiniReader()

qntwk_req = QgsBlockingNetworkRequest()
req_status = qntwk_req.get(
    request=QNetworkRequest(QUrl("https://geotribu.fr/feed_rss_created.xml")),
    forceRefresh=False,
)

print(isinstance(req_status, QgsBlockingNetworkRequest.ErrorCode))
print(req_status == QgsBlockingNetworkRequest.ErrorCode.NoError)
print(req_status == 0)
print(qntwk_req.errorMessage() == "")


if req_status != QgsBlockingNetworkRequest.ErrorCode.NoError:
    print("Et meeeeeeeerde")
    print(qntwk_req.errorMessage())

req_reply = qntwk_req.reply()
print(type(req_reply.content()))
print(req_reply.rawHeaderList())
print(req_reply.rawHeader(b"Content-Type"))
print(req_reply.rawHeader(b"last-modified"))
print(req_reply.rawHeader(b"Content-type") == "application/xml")
print(isinstance(req_reply.content(), QByteArray))
# print(req_reply.content())

rss = rss_rdr.read_feed(req_reply.content())
print(rss_rdr.latest_item.url)
