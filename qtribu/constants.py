#! python3  # noqa: E265

"""
    Plugin constants.
"""

# standard
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# 3rd party
from qgis.PyQt.QtGui import QIcon

# plugin
from qtribu.__about__ import DIR_PLUGIN_ROOT

ICON_ARTICLE = QIcon(str(DIR_PLUGIN_ROOT.joinpath("resources/images/article.svg")))
ICON_GEORDP = QIcon(str(DIR_PLUGIN_ROOT.joinpath("resources/images/geordp.svg")))
LOCAL_CDN_PATH: Path = Path().home() / ".geotribu/cdn/"


# Classes
@dataclass
class RdpNewsCategory:
    name: str
    description: str
    order: int
    example: Optional[str] = None


@dataclass
class GeotribuImage:
    name: str
    url: str
    kind: str
    description: Optional[str] = None

    def local_path(self, base_path: Path = Path().home() / ".geotribu/cdn/") -> Path:
        """Get expected local path.

        :param base_path: base path to store images, defaults to Path().home()/".geotribu/cdn/"
        :type base_path: Path, optional

        :return: local path to the image
        :rtype: Path
        """
        url_parsed = urlparse(self.url)
        return Path(base_path / url_parsed.path[1:])


# Objects
GEORDP_NEWS_CATEGORIES: tuple = (
    RdpNewsCategory(
        name="Sorties de la semaine",
        description="Pour relayer les nouveautés dans les outils de la "
        "géomatique. Attention, il ne s'agit pas de paraphraser les notes de version "
        "ou les communiqués de presse, mais d'apporter une valeur ajoutée personnelle.",
        order=1,
    ),
    RdpNewsCategory(
        name="Logiciel",
        description="Découverte, cas d'usage d'un logiciel pas forcément nouveau mais "
        "intéressant.",
        order=2,
    ),
    RdpNewsCategory(
        name="Représentation cartographique",
        description="Dataviz, cartographies, art...",
        order=3,
        example="https://geotribu.fr/rdp/2021/rdp_2021-06-18/#francepixel-bati",
    ),
    RdpNewsCategory(
        name="OpenStreetMap",
        description="Toute news liée au plus grand projet de cartographie "
        "collaborative mondiale.",
        order=4,
    ),
    RdpNewsCategory(
        name="Google",
        description="Toute news liée à la plus grande agence de publicité numérique "
        "mondiale.",
        order=5,
    ),
    RdpNewsCategory(
        name="Open Data",
        description="Tout ce qui a trait aux données ouvertes.",
        order=6,
        example="https://geotribu.fr/rdp/2020/rdp_2020-12-11/#open-data",
    ),
    RdpNewsCategory(
        name="Geo-event",
        description="Evénements, salons, conférences...",
        order=7,
        example="SAGEO, GéoDataDays, CartoMob, "
        "https://geotribu.fr/rdp/2020/rdp_2020-12-11/#rencontres-des-utilisateurs-francophones-de-qgis)...",
    ),
    RdpNewsCategory(
        name="Divers",
        description="Tout ce qui ne rentre pas dans les autres sections.",
        order=8,
        example="https://geotribu.fr/rdp/2021/rdp_2021-03-26/#les-villes-ont-elles-un-corps",
    ),
)

GEORDP_NEWS_ICONS: tuple = (
    GeotribuImage(
        name="news",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/news.png",
        kind="icon",
        description="icône news générique",
    ),
    GeotribuImage(
        name="world",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/world.png",
        kind="icon",
        description="icône globe générique",
    ),
    GeotribuImage(
        name="absurde",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/absurde.png",
        kind="icon",
        description="icône globe retourné",
    ),
    GeotribuImage(
        name="ancien",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/ancien.png",
        kind="icon",
        description="icône globe ancien",
    ),
    GeotribuImage(
        name="flux",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/flux.png",
        kind="icon",
        description="icône globe flux",
    ),
    GeotribuImage(
        name="genre",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/genre.png",
        kind="icon",
        description="icône globe genre",
    ),
    GeotribuImage(
        name="heatmap",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/heatmap.png",
        kind="icon",
        description="icône globe heatmap",
    ),
    GeotribuImage(
        name="itinéraire",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/itineraire.png",
        kind="icon",
        description="icône globe itinéraire",
    ),
    GeotribuImage(
        name="mentale",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/mentale.png",
        kind="icon",
        description="icône globe mentale",
    ),
    GeotribuImage(
        name="metro",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/metro.png",
        kind="icon",
        description="icône globe metro",
    ),
    GeotribuImage(
        name="microworld",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/microworld.png",
        kind="icon",
        description="icône globe microworld",
    ),
    GeotribuImage(
        name="night",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/night.png",
        kind="icon",
        description="icône globe night",
    ),
    GeotribuImage(
        name="mystique",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/mystique.png",
        kind="icon",
        description="icône globe mystique",
    ),
    GeotribuImage(
        name="pointillisme",
        url="https://cdn.geotribu.fr/img/internal/icons-rdp-news/pointillisme.png",
        kind="icon",
        description="icône globe pointillisme",
    ),
)
