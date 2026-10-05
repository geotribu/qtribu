#! python3

# Standard library
from dataclasses import dataclass


@dataclass
class RssItem:
    """Dataclass describing a RSS channel item."""

    abstract: str | None = None
    authors: list[str | None] | None = None
    categories: list[str | None] | None = None
    date_pub: tuple[int, ...] | None = None
    guid: str | None = None
    image_length: str | None = None
    image_type: str | None = None
    image_url: str | None = None
    title: str | None = None
    url: str | None = None
