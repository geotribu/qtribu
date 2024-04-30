#! python3  # noqa: E265


"""
    Minimalist RSS reader.
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
from typing import Optional

# PyQGIS
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtGui import QDesktopServices

try:
    from qgis.PyQt.QtWebKitWidgets import QWebView
except:
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    from PyQt.QtWebEngineWidgets import QWebEngineView as QWebView

from qgis.PyQt.QtWidgets import QVBoxLayout, QWidget

# project
from qtribu.toolbelt import NetworkRequestsManager, PlgLogger, PlgOptionsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class WebViewer:
    """Minimalist web viewer to display webpages into QGIS."""

    def __init__(self):
        """Class initialization."""
        self.log = PlgLogger().log
        self.wdg_web: Optional[QWidget] = None

    def display_web_page(self, url: str):
        """Parse the feed XML as string and store items into an ordered tuple of tuples.

        :param in_xml: XML as string. Must be RSS compliant.
        :type in_xml: str

        :return: RSS items loaded as namedtuples
        :rtype: Tuple[RssItem]
        """
        try:
            qntwk = NetworkRequestsManager()
            if PlgOptionsManager().get_plg_settings().browser == 1:
                # display web page
                self.wdg_web = QWidget()
                vlayout = QVBoxLayout()
                web = QWebView()
                req = qntwk.build_url(url)
                web.load(req)
                vlayout.addWidget(web)
                self.wdg_web.setLayout(vlayout)
                self.wdg_web.setWindowTitle(self.tr("Last article from Geotribu"))
                self.wdg_web.setWindowModality(Qt.WindowModal)
                self.wdg_web.show()
                self.wdg_web.resize(1000, 600)

            else:
                QDesktopServices.openUrl(qntwk.build_url(url))

            self.log(
                message=self.tr("Last article from Geotribu loaded and displayed."),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr(message=f"Michel, we've got a problem: {err}"),
                log_level=2,
                push=True,
            )

    def set_window_title(self, title: str) -> None:
        self.wdg_web.setWindowTitle(title)

    def tr(self, message: str) -> str:
        """Translation method.

        :param message: text to be translated
        :type message: str

        :return: translated text
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)
