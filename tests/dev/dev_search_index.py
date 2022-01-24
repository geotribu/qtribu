#! python3  # noqa: E265
import requests
from typing import Union

# FUNCTIONS


def is_full_url(item: dict) -> bool:
    """Return True is it's a full URL or False if it's an anchor."""
    if "#" in item.get("location"):
        return False
    else:
        return True


def extract_type(item: dict) -> str:
    """Extract the type of the item."""
    if item.get("location").startswith("articles"):
        return "article"
    elif item.get("location").startswith("rdp"):
        return "rdp"
    else:
        return None


def extract_year(item: dict, min_year: int = 2020) -> Union[int, None]:
    """Extract the year of the item."""
    loc_split = item.get("location").split("/")
    if len(loc_split) > 2:
        if loc_split[1].isdigit():
            year = int(loc_split[1])
            print(year, min_year)
            if year >= min_year:
                return year
    else:
        return None


# MAIN
with requests.Session() as s:
    rez = s.request(
        method="get", url="https://static.geotribu.fr/search/search_index.json"
    )

search_index = rez.json()

print(search_index.keys())

for d in search_index.get("docs"):
    d_type = extract_type(d)
    d_year = extract_year(d, 2020)
    d_full_url = is_full_url(d)
    if not all([d_type, d_year, d_full_url]):
        # print("Not a wanted content")
        continue
    print(d.get("title"))
    print(d_type, d_year)
