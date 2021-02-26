#! python3  # noqa: E265

# Standard library
from collections import namedtuple

# Data structures
RssItem = namedtuple(
    typename="RssItem",
    field_names=[
        "abstract",
        "author",
        "date_pub",
        "guid",
        "image_length",
        "image_type",
        "image_url",
        "title",
        "url",
    ],
    defaults=(None, None, None, None, None, None, None, None, None),
)
