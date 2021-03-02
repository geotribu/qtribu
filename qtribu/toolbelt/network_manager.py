#! python3  # noqa: E265

"""
    Perform network request.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
from builtins import str

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.Qt import QByteArray, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# project
from qtribu.toolbelt import PlgLogger
from qtribu.toolbelt.preferences import PLG_PREFERENCES

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

    def get_from_source(
        self, source_ref: str = "geotribu-rss-feed-created"
    ) -> QByteArray:
        """Method to retrieve a RSS feed from a referenced source in preferences. \
        Use cache.

        :param source_ref: source reference name, defaults to "geotribu-rss-feed-created"
        :type source_ref: str, optional

        :raises ConnectionError: if any problem occurs during feed fetching.
        :raises TypeError: if response mime-type is not valid

        :return: feed response in bytes
        :rtype: QByteArray
        """
        if source_ref not in PLG_PREFERENCES:
            source_ref = "geotribu-rss-feed-created"

        url = PLG_PREFERENCES.get("sources").get(source_ref)

        try:
            req_status = self.ntwk_requester.get(
                request=QNetworkRequest(QUrl(url)),
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
