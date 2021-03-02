#! python3  # noqa: E265

# PyQGIS
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.PyQt.QtWidgets import QAction, QVBoxLayout, QWidget

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT
from qtribu.logic import RssMiniReader
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgTranslator


class GeotribuPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.log = PlgLogger().log

        # translation
        plg_translation_mngr = PlgTranslator()
        translator = plg_translation_mngr.get_translator()
        if translator:
            QCoreApplication.installTranslator(translator)
        self.tr = plg_translation_mngr.tr

        # sub-modules
        self.rss_rdr = RssMiniReader()

    def initGui(self):
        self.action = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_geotribu.png")),
            self.tr("Newest article"),
            self.iface.mainWindow(),
        )
        self.action.setToolTip(self.tr(text="Newest article", context="GeotribuPlugin"))
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        try:
            qntwk = NetworkRequestsManager(tr=self.tr)
            self.rss_rdr.read_feed(qntwk.get_from_source())

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
            self.wdg_web.setWindowTitle(self.tr("Last article from Geotribu"))
            self.wdg_web.setWindowModality(Qt.WindowModal)
            self.wdg_web.show()
            self.wdg_web.resize(800, 600)

            self.log(
                message=self.tr(
                    text="Last article from Geotribu loaded and displayed.",
                    context="GeotribuPlugin",
                ),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr(
                    text="Houston, we've got a problem: {}".format(err),
                    context="GeotribuPlugin",
                ),
                log_level=2,
                push=True,
            )
