#! python3  # noqa: E265

"""
    Perform network request.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
from functools import lru_cache
from urllib.parse import urlparse, urlunparse

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest, QgsFileDownloader
from qgis.PyQt.QtCore import QByteArray, QCoreApplication, QEventLoop, QUrl
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

    @lru_cache(maxsize=128)
    def build_url(self, url: str) -> QUrl:
        """Returns the URL using the plugin settings.

        :param url: input URL to complete
        :type url: str

        :return: Qt URL object with full parameters
        :rtype: QUrl
        """
        parsed_url = urlparse(url)
        clean_url = parsed_url._replace(
            query=PlgOptionsManager.get_plg_settings().request_path
        )
        return QUrl(urlunparse(clean_url))

    def build_request(self, url: QUrl = None) -> QNetworkRequest:
        """Build request object using plugin settings.

        :return: network request object.
        :rtype: QNetworkRequest
        """
        # if URL is not specified, let's use the default one
        if not url:
            url = self.build_url()

        # create network object
        qreq = QNetworkRequest(url=url)

        # headers
        headers = {
            b"Accept": bytes(self.plg_settings.http_content_type, "utf8"),
            b"User-Agent": bytes(self.plg_settings.http_user_agent, "utf8"),
        }
        for k, v in headers.items():
            qreq.setRawHeader(k, v)

        return qreq

    def get_from_source(self, headers: dict = None) -> QByteArray:
        """Method to retrieve a RSS feed from a referenced source in preferences. \
        Use cache.

        :raises ConnectionError: if any problem occurs during feed fetching.
        :raises TypeError: if response mime-type is not valid

        :return: feed response in bytes
        :rtype: QByteArray

        :example:

        .. code-block:: python

            import json
            response_as_dict = json.loads(str(response, "UTF8"))
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
                message=f"Request to {url} succeeded.",
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
            err_msg = "Houston, we've got a problem: {}".format(err)
            logger.error(err_msg)
            self.log(message=err_msg, log_level=2, push=1)

    def download_file(self, remote_url: str, local_path: str) -> str:
        """Download a file from a remote web server accessible through HTTP.

        :param remote_url: remote URL
        :type remote_url: str
        :param local_path: path to the local file
        :type local_path: str
        :return: output path
        :rtype: str
        """
        self.log(
            message=f"Downloading file from {remote_url} to {local_path}", log_level=4
        )
        # download it
        loop = QEventLoop()
        file_downloader = QgsFileDownloader(
            url=QUrl(remote_url), outputFileName=local_path, delayStart=True
        )
        file_downloader.downloadExited.connect(loop.quit)
        file_downloader.startDownload()
        loop.exec_()

        self.log(
            message=f"Download of {remote_url} to {local_path} succeedeed", log_level=3
        )
        return local_path
