#! python3  # noqa: E265

# PyQGIS
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.PyQt.QtWidgets import QAction, QVBoxLayout, QWidget

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT, __title__
from qtribu.logic import RssMiniReader
from qtribu.toolbelt import NetworkAccessManager, PluginLogHandler, RequestsException


class GeotribuPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.log = PluginLogHandler().log
        self.rss_rdr = RssMiniReader()

    def initGui(self):
        self.action = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_geotribu.png")),
            "Dernier article Geotribu",
            self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        nam = NetworkAccessManager(None)
        try:
            (response, content) = nam.request(
                "https://static.geotribu.fr/feed_rss_created.xml"
            )

            self.log(message="Request succeeded!", log_level=3)
            self.rss_rdr.read_feed(content)

            if not self.rss_rdr.latest_item:
                raise Exception("No item found")

            # display web page
            self.wdg_web = QWidget()
            vlayout = QVBoxLayout()
            web = QWebView()
            last_page = QUrl(self.rss_rdr.latest_item.url)
            web.load(last_page)
            vlayout.addWidget(web)
            self.wdg_web.setLayout(vlayout)
            self.wdg_web.setWindowTitle(__title__)
            self.wdg_web.setWindowModality(Qt.WindowModal)
            self.wdg_web.show()
            self.wdg_web.resize(800, 600)

            self.log(
                message="Dernier article de Geotribu affiché depuis le flux RSS téléchargé",
                log_level=3,
                push=True,
            )
        except RequestsException as err:
            self.log(
                message="Something went wrong: {}".format(err), log_level=2, push=True
            )
            # Handle exception
            pass
