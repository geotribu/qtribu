
from email.utils import parsedate, parsedate_tz, parsedate_to_datetime
from urllib.request import urlopen
import xml.etree.ElementTree as ET

PATTERN_INCLUDE = ["articles/", "rdp/"]

tree = ET.parse(urlopen("https://static.geotribu.fr/feed_rss_created.xml"))
root = tree.getroot()

print(root)
articles = root.findall('channel/item')
print(len(articles))

for art in articles:
    if not any([i in art.find("link").text for i in PATTERN_INCLUDE]):
        print(art.find("title").text)
    # print(art.find("title").text)
    date_pub = art.find("pubDate").text


# handle date RFC 2822
# print(date_pub)
# print(parsedate(date_pub))
# print(parsedate_tz(date_pub))
# print(parsedate_to_datetime(date_pub).timestamp())

# # image
# print(art.find("enclosure").attrib.get("url"))
