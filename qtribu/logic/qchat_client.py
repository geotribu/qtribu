import json
from typing import Any

# 3rd party
from qgis.PyQt.QtCore import QByteArray

# plugin
from qtribu.__about__ import __title__, __version__
from qtribu.toolbelt import NetworkRequestsManager

# -- GLOBALS --
HEADERS: dict = {
    b"Accept": b"application/json",
    b"User-Agent": bytes(f"{__title__}/{__version__}", "utf8"),
}

NB_MESSAGES_TO_FETCH = 6


class QChatApiClient:
    """
    QChat API client
    """

    def __init__(
        self, instance_uri: str, nb_messages_to_fetch: int = NB_MESSAGES_TO_FETCH
    ):
        self.instance_uri = instance_uri
        self.nb_messages_to_fetch = nb_messages_to_fetch
        self.qntwk = NetworkRequestsManager()

    def get_rooms(self) -> list[str]:
        """
        Get available rooms with an API HTTP call
        """
        url = f"{self.instance_uri}/rooms"
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=url,
            response_expected_content_type="application/json",
        )
        data = json.loads(str(response, "UTF8"))
        return data

    def get_last_messages(self, room: str) -> list[dict[str, Any]]:
        """
        Get last chat messages for a room with an API HTTP call
        """
        url = f"{self.instance_uri}/room/{room}/messages/{self.nb_messages_to_fetch}"
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=url,
            response_expected_content_type="application/json",
        )
        data = json.loads(str(response, "UTF8"))
        return data
