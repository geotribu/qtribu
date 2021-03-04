#! python3  # noqa: E265

# PyQGIS
from qgis.gui import QgisInterface
from qgis.PyQt.Qt import QUrl
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWebKitWidgets import QWebView
from qgis.PyQt.QtWidgets import QAction, QVBoxLayout, QWidget
from qgis.utils import showPluginHelp

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT, __title__
from qtribu.logic import RssMiniReader
from qtribu.toolbelt import (
    NetworkRequestsManager,
    PlgLogger,
    PlgOptionsFactory,
    PlgTranslator,
)


class GeotribuPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
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
        """Set up plugin UI elements."""

        # -- Actions
        self.action_run = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_geotribu.png")),
            self.tr("Newest article"),
            self.iface.mainWindow(),
        )
        self.action_run.setToolTip(
            self.tr(text="Newest article", context="GeotribuPlugin")
        )
        self.action_run.triggered.connect(self.run)

        self.action_help = QAction(
            QIcon(":/images/themes/default/mActionHelpContents.svg"),
            self.tr("Help", context="GeotribuPlugin"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            lambda: showPluginHelp(filename="resources/help/index")
        )

        # -- Menu
        self.iface.addPluginToWebMenu(__title__, self.action_run)
        self.iface.addPluginToWebMenu(__title__, self.action_help)

        # -- Toolbar
        self.iface.addToolBarIcon(self.action_run)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginWebMenu(__title__, self.action_help)
        self.iface.removePluginWebMenu(__title__, self.action_run)

        # -- Clean up toolbar
        self.iface.removeToolBarIcon(self.action_run)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.action_run
        del self.action_help

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
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
