from dataclasses import dataclass
from typing import Optional


@dataclass(init=True, frozen=True)
class QChatMessage:
    type: str


@dataclass(init=True, frozen=True)
class QChatUncompliantMessage(QChatMessage):
    reason: str


@dataclass(init=True, frozen=True)
class QChatTextMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    text: str


@dataclass(init=True, frozen=True)
class QChatImageMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    image_data: str


@dataclass(init=True, frozen=True)
class QChatNbUsersMessage(QChatMessage):
    nb_users: int


@dataclass(init=True, frozen=True)
class QChatNewcomerMessage(QChatMessage):
    newcomer: str


@dataclass(init=True, frozen=True)
class QChatExiterMessage(QChatMessage):
    exiter: str


@dataclass(init=True, frozen=True)
class QChatLikeMessage(QChatMessage):
    liker_author: str
    liked_author: str
    message: str


@dataclass(init=True, frozen=True)
class QChatGeojsonMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    layer_name: str
    crs_wkt: str
    crs_authid: str
    geojson: dict
    style: Optional[str]


@dataclass(init=True, frozen=True)
class QChatCrsMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    crs_wkt: str
    crs_authid: str


@dataclass(init=True, frozen=True)
class QChatBboxMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    crs_wkt: str
    crs_authid: str
    xmin: float
    xmax: float
    ymin: float
    ymax: float
