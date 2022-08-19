#! python3  # noqa: E265

"""
    Plugin constants.
"""

# standard
from dataclasses import dataclass


# Classes
@dataclass
class RdpNewsCategory:
    name: str
    description: str
    order: int
    example: str = None


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
        example="https://static.geotribu.fr/rdp/2021/rdp_2021-06-18/#francepixel-bati",
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
        example="https://static.geotribu.fr/rdp/2020/rdp_2020-12-11/#open-data",
    ),
    RdpNewsCategory(
        name="Geo-event",
        description="Evénements, salons, conférences...",
        order=7,
        example="SAGEO, GéoDataDays, CartoMob, "
        "https://static.geotribu.fr/rdp/2020/rdp_2020-12-11/#rencontres-des-utilisateurs-francophones-de-qgis)...",
    ),
    RdpNewsCategory(
        name="Divers",
        description="Tout ce qui ne rentre pas dans les autres sections.",
        order=8,
        example="https://static.geotribu.fr/rdp/2021/rdp_2021-03-26/#les-villes-ont-elles-un-corps",
    ),
)
