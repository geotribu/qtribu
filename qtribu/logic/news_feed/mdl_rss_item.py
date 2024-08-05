#! python3  # noqa: E265

# Standard library
from dataclasses import dataclass
from typing import Optional


@dataclass
class RssItem:
    """Dataclass describing a RSS channel item."""

    abstract: Optional[str] = None
    authors: Optional[list[Optional[str]]] = None
    categories: Optional[list[Optional[str]]] = None
    date_pub: Optional[tuple[int, ...]] = None
    guid: Optional[str] = None
    image_length: Optional[str] = None
    image_type: Optional[str] = None
    image_url: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
