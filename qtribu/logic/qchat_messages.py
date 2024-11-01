from dataclasses import dataclass
from typing import Optional


@dataclass(init=True, frozen=True)
class QChatMessage:
    type: str


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
