import pprint
from functools import partial

from qgis.core import QgsApplication, QgsDataSourceUri, QgsProviderRegistry
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QComboBox, QDialog

# variables

# point de vigilance, les noms du type de base de données ne sont pas exactement les mêmes...
db_types = ("ogr", "postgres", "spatialite")
dico_connections_for_combobox = {}

# un peu d'info
print(
    "Liste des formats disponibles : ",
    sorted(QgsProviderRegistry.instance().providerList()),
)
print(
    "Liste des drivers de base de données disponibles : ",
    QgsProviderRegistry.instance().databaseDrivers(),
)

for db_type in db_types:
    print("listing des connexions de type : ", db_type)
    # retrouver les connections du type de base de données
    connections = QgsProviderRegistry.instance().providerMetadata(db_type).connections()

    for connection_name in connections:
        dico_connections_for_combobox[connection_name] = db_type, connections.get(
            connection_name
        )


def popo():
    print("hey")
    print(cbb_db_connections.currentText())
    conn = dico_connections_for_combobox[cbb_db_connections.currentText()][1]
    print(conn.providerKey(), conn.icon())

    selected = cbb_db_connections.itemData(cbb_db_connections.currentIndex())
    print(selected)
    print(selected.uri())
    print(isinstance(selected.uri(), str))
#    print(QgsDataSourceUri(selected.uri()).database())
#    print(QgsDataSourceUri(selected.uri()).host())
#    print(selected.configuration())
    
    # print(conn.uri.connectionInfo(True))

    # lister les schémas
#    if conn.providerKey().startswith("postgr"):
#        print("Schémas : ", conn.schemas())

    # lister les tables
    # print("Tables : ", [(t.defaultName(), str(t.flags())) for t in conn.tables()[:10]])


# la fenêtre de dialogue pour accueillir notre liste déroulante
dd = QDialog(iface.mainWindow())
dd.setWindowTitle("Connexions {}".format(" / ".join(db_types)))

# on remplit la liste déroulante
cbb_db_connections = QComboBox(dd)
for k, v in dico_connections_for_combobox.items():
    cbb_db_connections.addItem(v[1].icon(), k, v[1])

cbb_db_connections.activated.connect(partial(popo))

# un peu de tunning des dimensions
dd.resize(300, 30)
cbb_db_connections.resize(300, 30)


# on affiche
dd.show()
