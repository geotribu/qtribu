import pprint

from qgis.core import QgsDataSourceUri
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QComboBox

# variables
db_types = {
    "GeoPackage": QIcon(":/images/themes/default/mGeoPackage.svg"),
    "PostgreSQL": QIcon(":/images/themes/default/mIconPostgis.svg"),
    "SpatiaLite": QIcon(":/images/themes/default/mIconSpatialite.svg"),
}
dico_connections_for_combobox = {}
settings = QSettings()

for db_type in db_types:
    print(db_type)
    # retrouver les connections du type de base de données
    settings.beginGroup(f"/{db_type}/connections/")
    connections = settings.childGroups()
    settings.endGroup()
    
    selected_conn = settings.value(f"/{db_type}/connections/selected", "", type=str)
    if selected_conn not in connections:
        connections.append(selected_conn)

    for connection_name in connections:
        print(connection_name)
        uri = QgsDataSourceUri()
        uri.setConnection(
            aHost=settings.value(f"{db_type}/connections/{connection_name}/host"),
            aPort=settings.value(f"{db_type}/connections/{connection_name}/port"),
            aDatabase=settings.value(
                f"{db_type}/connections/{connection_name}/database"
            ),
            aUsername="",
            aPassword="",
        )
        # selon le type d'authentification configuré, on s'adapte
        if (
            settings.value(f"{db_type}/connections/{connection_name}/saveUsername")
            == "true"
        ):
            uri.setUsername(
                settings.value(f"{db_type}/connections/{connection_name}/username"),
            )
        if (
            settings.value(f"{db_type}/connections/{connection_name}/savePassword")
            == "true"
        ):
            uri.setPassword(
                settings.value(f"{db_type}/connections/{connection_name}/password"),
            )
        dico_connections_for_combobox[connection_name] = db_type, uri


# la fenêtre de dialogue pour accueillir notre liste déroulante
dd = QDialog(iface.mainWindow())
dd.setWindowTitle("Connexions {}".format(" / ".join(db_types)))

# on remplit la liste déroulante
cbb_db_connections = QComboBox(dd)
for k, v in dico_connections_for_combobox.items():
    cbb_db_connections.addItem(db_types.get(v[0]), k, v[1])

# un peu de tunning des dimensions
dd.resize(300, 30)
cbb_db_connections.resize(300, 30)

# on affiche
dd.show()
