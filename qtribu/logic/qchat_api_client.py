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

CONTENT_TYPE_JSON = "application/json"

INSTANCES_JSON_URL = "https://github.com/geotribu/gischat/raw/main/instances.json"


class QChatApiClient:
    """
    QChat API client
    """

    def __init__(
        self,
        instance_uri: str,
    ):
        self.instance_uri = instance_uri
        self.qntwk = NetworkRequestsManager()

    def get_registered_instances(self) -> dict[str, list[str]]:
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=INSTANCES_JSON_URL,
            response_expected_content_type="text/plain; charset=utf-8",
            use_cache=False,
        )
        data = json.loads(str(response, "UTF8"))
        return data

    def get_status(self) -> dict[str, Any]:
        """
        Get instance status with an API call
        """
        url = f"{self.instance_uri}/status"
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=url,
            response_expected_content_type=CONTENT_TYPE_JSON,
            use_cache=False,
        )
        data = json.loads(str(response, "UTF8"))
        return data

    def get_rules(self) -> dict[str, str]:
        """
        Get instance rules with an API call
        """
        url = f"{self.instance_uri}/rules"
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=url,
            response_expected_content_type=CONTENT_TYPE_JSON,
            use_cache=True,
        )
        data = json.loads(str(response, "UTF8"))
        return data

    def get_rooms(self) -> list[str]:
        """
        Get available rooms with an API HTTP call
        """
        url = f"{self.instance_uri}/rooms"
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=url,
            response_expected_content_type=CONTENT_TYPE_JSON,
            use_cache=True,
        )
        data = json.loads(str(response, "UTF8"))
        return data

    def get_registered_users(self, room: str) -> list[str]:
        """
        Get registered users in a room with an API HTTP CALL
        """
        url = f"{self.instance_uri}/room/{room}/users"
        response: QByteArray = self.qntwk.get_from_source(
            headers=HEADERS,
            url=url,
            response_expected_content_type=CONTENT_TYPE_JSON,
            use_cache=False,
        )
        data = json.loads(str(response, "UTF8"))
        return data
