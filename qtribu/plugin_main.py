#! python3  # noqa: E265

"""
Main plugin module.
"""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import Qgis, QgsApplication, QgsSettings
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QLocale, Qt, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qtribu.__about__ import DIR_PLUGIN_ROOT, __icon_path__, __title__, __uri_homepage__
from qtribu.constants import ICON_ARTICLE, ICON_GEORDP
from qtribu.gui.dlg_contents import GeotribuContentsDialog
from qtribu.gui.dlg_settings import PlgOptionsFactory
from qtribu.gui.form_article import ArticleForm
from qtribu.gui.form_rdp_news import RdpNewsForm
from qtribu.logic.news_feed.rss_reader import RssMiniReader
from qtribu.logic.splash_changer import SplashChanger
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser, open_url_in_webviewer

# conditional imports
try:
    from qtribu.gui.dck_qchat import QChatWidget

    EXTERNAL_DEPENDENCIES_AVAILABLE: bool = True
except ImportError:
    EXTERNAL_DEPENDENCIES_AVAILABLE: bool = False


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

        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[
            0:2
        ]
        locale_path: Path = (
            DIR_PLUGIN_ROOT / f"resources/i18n/{__title__.lower()}_{self.locale}.qm"
        )
        self.log(
            message=f"Translation: {self.locale}, {locale_path} "
            f"(exists={locale_path.exists()})",
            log_level=4,
        )
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)
            self.log(
                message=f"Translation loaded from file: {self.locale}, {locale_path}",
                log_level=Qgis.MessageLevel.NoLevel,
            )
        else:
            self.log(
                message=f"Translation file does not exist: {self.locale}, {locale_path}",
                log_level=Qgis.MessageLevel.Warning,
            )

        # sub-modules
        self.rss_reader = None
        self.splash_chgr = SplashChanger(self)

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # toolbar
        self.toolbar = self.iface.addToolBar(name=self.tr("Geotribu toolbar"))

        # -- Forms
        self.form_article = None
        self.form_contents = None
        self.form_rdp_news = None

        # -- QChat
        self.qchat_widget = None

        # -- Actions
        self.action_show_latest_content = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_green_no_text.svg")),
            self.tr("Newest article"),
            self.iface.mainWindow(),
        )

        self.action_show_latest_content.setToolTip(self.tr("Newest article"))
        self.action_show_latest_content.triggered.connect(self.on_show_latest_content)

        self.action_open_contents = QAction(
            QgsApplication.getThemeIcon("mActionOpenTableVisible.svg"),
            self.tr("Browse latest contents"),
            self.iface.mainWindow(),
        )
        self.action_open_contents.setToolTip(self.tr("Browse latest contents"))
        self.action_open_contents.triggered.connect(self.open_contents)

        self.action_form_rdp_news = QAction(
            ICON_GEORDP,
            self.tr("Propose a news to the next GeoRDP"),
            self.iface.mainWindow(),
        )
        self.action_form_rdp_news.setToolTip(
            self.tr("Propose a news to the next GeoRDP")
        )
        self.action_form_rdp_news.triggered.connect(self.open_form_rdp_news)

        self.action_form_article = QAction(
            ICON_ARTICLE,
            self.tr("Submit an article"),
            self.iface.mainWindow(),
        )
        self.action_form_article.setToolTip(self.tr("Submit an article"))
        self.action_form_article.triggered.connect(self.open_form_article)

        self.action_open_chat = QAction(
            QgsApplication.getThemeIcon("mMessageLog.svg"),
            self.tr("QChat"),
            self.iface.mainWindow(),
        )
        self.action_open_chat.setToolTip(self.tr("QChat"))
        self.action_open_chat.triggered.connect(self.open_chat)

        self.action_open_qfield_qchat = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/qfield.svg")),
            self.tr("QChat in QField"),
            self.iface.mainWindow(),
        )
        self.action_open_qfield_qchat.setToolTip(self.tr("QChat in QField"))
        self.action_open_qfield_qchat.triggered.connect(
            partial(
                open_url_in_browser,
                "https://github.com/geotribu/qchat-qfield-plugin",
            )
        )

        self.action_help = QAction(
            QIcon(QgsApplication.iconPath("mActionHelpContents.svg")),
            self.tr("Help"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            partial(open_url_in_browser, __uri_homepage__)
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(currentPage=f"mOptionsPage{__title__}")
        )

        self.action_splash = self.splash_chgr.menu_action
        self.action_splash.triggered.connect(self.splash_chgr.switch)

        # -- Menu
        self.iface.addPluginToWebMenu(__title__, self.action_open_chat)
        self.iface.addPluginToWebMenu(__title__, self.action_open_qfield_qchat)
        self.iface.addPluginToWebMenu(__title__, self.action_show_latest_content)
        self.iface.addPluginToWebMenu(__title__, self.action_form_rdp_news)
        self.iface.addPluginToWebMenu(__title__, self.action_form_article)
        self.iface.addPluginToWebMenu(__title__, self.action_splash)
        self.iface.addPluginToWebMenu(__title__, self.action_settings)
        self.iface.addPluginToWebMenu(__title__, self.action_help)

        # -- Help menu
        self.iface.helpMenu().addSeparator()
        self.action_geotribu = QAction(
            QIcon(str(__icon_path__)),
            self.tr("Geotribu website"),
        )
        self.action_geotribu.triggered.connect(
            partial(
                open_url_in_browser,
                "https://geotribu.fr",
            )
        )

        self.action_georezo = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/georezo.png")),
            self.tr("QGIS forum on GeoRezo"),
        )
        self.action_georezo.triggered.connect(
            partial(
                open_url_in_browser,
                "https://georezo.net/forum/viewforum.php?id=55",
            )
        )
        self.action_osgeofr = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/osgeo.svg")),
            self.tr("OSGeo France"),
        )
        self.action_osgeofr.triggered.connect(
            partial(
                open_url_in_browser,
                "https://www.osgeo.fr/",
            )
        )
        self.iface.helpMenu().addAction(self.action_georezo)
        self.iface.helpMenu().addAction(self.action_geotribu)
        self.iface.helpMenu().addAction(self.action_osgeofr)

        # -- Toolbar
        self.toolbar.addAction(self.action_show_latest_content)
        self.toolbar.addAction(self.action_open_chat)
        self.toolbar.addAction(self.action_form_rdp_news)
        self.toolbar.addAction(self.action_form_article)

        # -- Post UI initialization
        self.rss_reader = RssMiniReader(
            action_read=self.action_show_latest_content,
            on_read_button=self.on_show_latest_content,
        )
        self.iface.initializationCompleted.connect(self.post_ui_init)

        if not self.check_dependencies():
            return

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginWebMenu(__title__, self.action_help)
        self.iface.removePluginWebMenu(__title__, self.action_form_article)
        self.iface.removePluginWebMenu(__title__, self.action_form_rdp_news)
        self.iface.removePluginWebMenu(__title__, self.action_show_latest_content)
        self.iface.removePluginWebMenu(__title__, self.action_open_chat)
        self.iface.removePluginWebMenu(__title__, self.action_open_qfield_qchat)
        self.iface.removePluginWebMenu(__title__, self.action_settings)
        self.iface.removePluginWebMenu(__title__, self.action_splash)

        self.iface.helpMenu().removeAction(self.action_georezo)
        self.iface.helpMenu().removeAction(self.action_geotribu)
        self.iface.pluginHelpMenu().removeAction(self.action_osgeofr)

        # -- Clean up toolbar
        del self.toolbar
        del self.qchat_widget

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.action_help
        del self.action_georezo
        del self.action_open_chat

    def post_ui_init(self):
        """Run after plugin's UI has been initialized.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.rss_reader.process()
        except Exception as err:
            self.log(
                message=self.tr(f"Reading the RSS feed failed. Trace: {err}"),
                log_level=Qgis.MessageLevel.Critical,
                push=True,
            )
            return

        # insert latest item within news feed
        try:
            self.rss_reader.add_latest_item_to_news_feed()
        except Exception as err:
            self.log(
                message=self.tr(
                    f"Unable to insert latest item within QGIS news feed. Trace: {err}"
                ),
                log_level=Qgis.MessageLevel.Critical,
                push=True,
            )
            return

        # auto reconnect to room if needed
        settings = PlgOptionsManager().get_plg_settings()
        if settings.qchat_auto_reconnect and settings.qchat_auto_reconnect_room:
            if not self.qchat_widget:
                self.qchat_widget = QChatWidget(
                    iface=self.iface,
                    parent=self.iface.mainWindow(),
                    auto_reconnect_room=settings.qchat_auto_reconnect_room,
                )
                self.iface.addDockWidget(
                    Qt.DockWidgetArea.RightDockWidgetArea, self.qchat_widget
                )
            self.qchat_widget.show()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def on_show_latest_content(self):
        """Main action on plugin icon pressed event."""
        try:
            if not self.rss_reader.latest_item:
                self.post_ui_init()

            # save latest RSS item displayed
            open_url_in_webviewer(
                self.rss_reader.latest_item.url, self.rss_reader.latest_item.title
            )
            self.action_show_latest_content.setIcon(
                QIcon(str(DIR_PLUGIN_ROOT / "resources/images/logo_green_no_text.svg"))
            )
            self.action_show_latest_content.setToolTip(self.tr("Newest article"))
            # save latest RSS item displayed
            PlgOptionsManager().set_value_from_key(
                key="latest_content_guid", value=self.rss_reader.latest_item.guid
            )
        except Exception as err:
            self.log(
                message=self.tr(f"Michel, we've got a problem: {err}"),
                log_level=Qgis.MessageLevel.Critical,
                push=True,
            )
            raise err

    def check_dependencies(self) -> bool:
        """Check if all dependencies are satisfied. If not, warn the user and disable plugin.

        :return: dependencies status
        :rtype: bool
        """
        # if import failed
        if not EXTERNAL_DEPENDENCIES_AVAILABLE:
            self.log(
                message=self.tr(
                    "Error importing some of dependencies. "
                    "Related functions have been disabled."
                ),
                log_level=Qgis.MessageLevel.Critical,
                push=True,
                duration=0,
                button=True,
                button_connect=partial(
                    QDesktopServices.openUrl,
                    QUrl(f"{__uri_homepage__}installation.html"),
                ),
            )
            # disable plugin widgets
            self.action_open_chat.setEnabled(False)

            # add tooltip over menu
            msg_disable = self.tr(
                "Plugin disabled. Please install all dependencies and then restart QGIS."
                " Refer to the documentation for more information."
            )
            self.action_open_chat.setToolTip(msg_disable)
            return False
        else:
            self.log(message=self.tr("Dependencies satisfied"), log_level=3)
            return True

    def open_contents(self) -> None:
        """Action to open contents dialog"""
        if not self.form_contents:
            self.form_contents = GeotribuContentsDialog()
        self.form_contents.show()

    def open_form_article(self) -> None:
        """Open the form to create a GeoRDP news."""
        if not self.form_article:
            self.form_article = ArticleForm()
            self.form_article.setModal(True)
            self.form_article.finished.connect(self._post_form_article)
        self.form_article.show()

    def _post_form_article(self, dialog_result: int) -> None:
        """Perform actions after the GeoRDP news form has been closed.

        :param dialog_result: dialog's result code. Accepted (1) or Rejected (0)
        :type dialog_result: int
        """
        if self.form_article:
            # if accept button, save user inputs
            if dialog_result == 1:
                self.form_article.wdg_author.save_settings()
            # clean up
            self.form_article.deleteLater()
            self.form_article = None

    def open_form_rdp_news(self) -> None:
        """Open the form to create a GeoRDP news."""
        if not self.form_rdp_news:
            self.form_rdp_news = RdpNewsForm()
            self.form_rdp_news.setModal(True)
            self.form_rdp_news.finished.connect(self._post_form_rdp_news)
        self.form_rdp_news.show()

    def _post_form_rdp_news(self, dialog_result: int) -> None:
        """Perform actions after the GeoRDP news form has been closed.

        :param dialog_result: dialog's result code. Accepted (1) or Rejected (0)
        :type dialog_result: int
        """
        if self.form_rdp_news:
            # if accept button, save user inputs
            if dialog_result == 1:
                self.form_rdp_news.wdg_author.save_settings()
            # clean up
            self.form_rdp_news.deleteLater()
            self.form_rdp_news = None

    def open_chat(self) -> None:
        if not self.qchat_widget:
            self.qchat_widget = QChatWidget(
                iface=self.iface, parent=self.iface.mainWindow()
            )
            self.iface.addDockWidget(
                Qt.DockWidgetArea.RightDockWidgetArea, self.qchat_widget
            )
        self.qchat_widget.show()
