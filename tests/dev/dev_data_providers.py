from qgis.core import QgsDataItemProviderRegistry

reg_data_provider = QgsDataItemProviderRegistry()
providers_name = [
    data_provider.name() for data_provider in reg_data_provider.providers()
]
"""
[
    "DB2",
    "WFS",
    "AFS",
    "AMS",
    "GDAL",
    "GeoNode",
    "GRASS",
    "MDAL",
    "MSSQL",
    "OGR",
    "GPKG",
    "OWS",
    "PostGIS",
    "spatialite",
    "Vector Tiles",QgsProviderRegistry
    "WMS",
    "XYZ Tiles",
]
"""

xyz_tiles = reg_data_provider.provider("XYZ Tiles")

new_connection = QgsAbstractProviderConnection("Test")

# https://gist.github.com/ThomasG77/48fc558fb8ee0e188f5b9da7bae6cd85