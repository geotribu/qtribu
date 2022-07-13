#! python3  # noqa: E265

"""
    Main plugin module.
"""

# standard
from functools import partial

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT, __icon_path__, __title__, __uri_homepage__
from qtribu.gui.dlg_settings import PlgOptionsFactory
from qtribu.logic import RssMiniReader, SplashChanger, WebViewer
from qtribu.toolbelt import (
    NetworkRequestsManager,
    PlgLogger,
    PlgOptionsManager,
    PlgTranslator,
)

# ############################################################################
# ########## Classes ###############
# ##################################


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
        self.splash_chgr = SplashChanger(self)
        self.web_viewer = WebViewer()

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        self.action_run = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_green_no_text.svg")),
            self.tr("Newest article"),
            self.iface.mainWindow(),
        )
        self.action_run.setToolTip(
            self.tr(text="Newest article", context="GeotribuPlugin")
        )
        self.action_run.triggered.connect(self.run)

        self.action_help = QAction(
            QIcon(QgsApplication.iconPath("mActionHelpContents.svg")),
            self.tr("Help", context="GeotribuPlugin"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )

        self.action_splash = self.splash_chgr.menu_action
        self.action_splash.triggered.connect(self.splash_chgr.switch)

        # -- Menu
        self.iface.addPluginToWebMenu(__title__, self.action_run)
        self.iface.addPluginToWebMenu(__title__, self.action_splash)
        self.iface.addPluginToWebMenu(__title__, self.action_settings)
        self.iface.addPluginToWebMenu(__title__, self.action_help)

        # -- Help menu
        self.iface.helpMenu().addSeparator()
        self.action_georezo = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/georezo.png")),
            self.tr("QGIS forum on GeoRezo"),
        )
        self.action_georezo.triggered.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl("https://georezo.net/forum/viewforum.php?id=55"),
            )
        )
        self.iface.helpMenu().addAction(self.action_georezo)

        self.action_geotribu = QAction(
            QIcon(str(__icon_path__)),
            self.tr("Geotribu website"),
        )
        self.action_geotribu.triggered.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl("http://geotribu.fr"),
            )
        )
        self.iface.helpMenu().addAction(self.action_geotribu)

        self.action_osgeofr = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/osgeo.svg")),
            self.tr("OSGeo France"),
        )
        self.action_osgeofr.triggered.connect(
            partial(
                QDesktopServices.openUrl,
                QUrl("https://www.osgeo.asso.fr/"),
            )
        )

        self.iface.pluginHelpMenu().addAction(self.action_osgeofr)

        # -- Toolbar
        self.iface.addToolBarIcon(self.action_run)

        # -- Post UI initialization
        self.iface.initializationCompleted.connect(self.post_ui_init)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginWebMenu(__title__, self.action_help)
        self.iface.removePluginWebMenu(__title__, self.action_run)
        self.iface.removePluginWebMenu(__title__, self.action_settings)
        self.iface.removePluginWebMenu(__title__, self.action_splash)

        self.iface.helpMenu().removeAction(self.action_georezo)
        self.iface.helpMenu().removeAction(self.action_geotribu)
        self.iface.pluginHelpMenu().removeAction(self.action_osgeofr)

        # -- Clean up toolbar
        self.iface.removeToolBarIcon(self.action_run)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.action_run
        del self.action_help
        del self.action_georezo

    def post_ui_init(self):
        """Run after plugin's UI has been initialized.

        :raises Exception: if there is no item in the feed
        """
        try:
            qntwk = NetworkRequestsManager(tr=self.tr)
            self.rss_rdr.read_feed(qntwk.get_from_source(headers=self.rss_rdr.HEADERS))
            if not self.rss_rdr.latest_item:
                raise Exception("No item found")

            # change tooltip
            self.action_run.setToolTip(
                "{} - {}".format(
                    self.tr("Newest article"), self.rss_rdr.latest_item.title
                )
            )

            # check if a new content has been published
            if self.rss_rdr.has_new_content:
                # change action icon
                self.action_run.setIcon(
                    QIcon(
                        str(
                            DIR_PLUGIN_ROOT / "resources/images/logo_orange_no_text.svg"
                        )
                    ),
                )
                # notify
                self.log(
                    message="{} {}".format(
                        self.tr("New content published:"),
                        self.rss_rdr.latest_item.title,
                    ),
                    log_level=3,
                    push=PlgOptionsManager().get_plg_settings().notify_push_info,
                    duration=PlgOptionsManager()
                    .get_plg_settings()
                    .notify_push_duration,
                    button=True,
                    button_text=self.tr("Newest article"),
                    button_connect=self.run,
                )

        except Exception as err:
            self.log(
                message=self.tr(
                    text=f"Michel, we've got a problem: {err}",
                    context="GeotribuPlugin",
                ),
                log_level=2,
                push=True,
            )

    def run(self):
        """Main action on plugin icon pressed event."""
        try:
            if not self.rss_rdr.latest_item:
                self.post_ui_init()

            self.web_viewer.display_web_page(url=self.rss_rdr.latest_item.url)
            self.action_run.setIcon(
                QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_green_no_text.svg"))
            )
            self.action_run.setToolTip(
                self.tr(text="Newest article", context="GeotribuPlugin")
            )
            # save latest RSS item displayed
            PlgOptionsManager().set_value_from_key(
                key="latest_content_guid", value=self.rss_rdr.latest_item.guid
            )
        except Exception as err:
            raise err
