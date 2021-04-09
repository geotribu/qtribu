#! python3  # noqa: E265

"""
    Perform network request.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.Qt import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from qtribu.__about__ import __title__, __version__
from qtribu.toolbelt.log_handler import PlgLogger
from qtribu.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class NetworkRequestsManager:
    """Helper on network operations.

    :param tr: method to translate
    :type tr: func
    """

    def __init__(self, tr):
        """Initialization."""
        self.log = PlgLogger().log
        self.ntwk_requester = QgsBlockingNetworkRequest()
        self.tr = tr

    def build_url(self, url: str) -> QUrl:

        url += PlgOptionsManager.get_plg_settings().request_path
        return QUrl(url)

    def get_from_source(self, headers: dict = None) -> QByteArray:
        """Method to retrieve a RSS feed from a referenced source in preferences. \
        Use cache.

        :raises ConnectionError: if any problem occurs during feed fetching.
        :raises TypeError: if response mime-type is not valid

        :return: feed response in bytes
        :rtype: QByteArray
        """
        url = self.build_url(PlgOptionsManager.get_plg_settings().rss_source)

        try:
            # prepare request
            req = QNetworkRequest(QUrl(url))
            if headers:
                for k, v in headers.items():
                    req.setRawHeader(k, v)
            else:
                req.setHeader(
                    QNetworkRequest.UserAgentHeader,
                    bytes(f"{__title__}/{__version__}", "utf8"),
                )

            req_status = self.ntwk_requester.get(
                request=req,
                forceRefresh=False,
            )

            # check if request is fine
            if req_status != QgsBlockingNetworkRequest.NoError:
                self.log(
                    message=self.ntwk_requester.errorMessage(), log_level=2, push=1
                )
                raise ConnectionError(self.ntwk_requester.errorMessage())

            self.log(
                message=self.tr("Request to {} succeeded.".format(url)),
                log_level=3,
                push=0,
            )

            req_reply = self.ntwk_requester.reply()
            if not req_reply.rawHeader(b"Content-Type") == "application/xml":
                raise TypeError(
                    "Response mime-type is '{}' not 'application/xml' as required.".format(
                        req_reply.rawHeader(b"Content-type")
                    )
                )

            return req_reply.content()

        except Exception as err:
            err_msg = self.tr(
                text="Houston, we've got a problem: {}".format(err),
                context="NetworkRequestsManager",
            )
            logger.error(err_msg)
            self.log(message=err_msg, log_level=2, push=1)
