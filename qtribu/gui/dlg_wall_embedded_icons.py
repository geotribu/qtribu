# standard
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgsCollapsibleGroupBox, QgsPixmapLabel
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QPushButton,
    QStyle,
    QWidget,
)

# plugin
from qtribu.toolbelt import PlgLogger


class IconsWall(QDialog):
    ICONS_SAMPLE_FALLBACK = (
        "mAlgorithmExtractLayerExtent.svg",
        "mAlgorithmIntersect.svg",
        "mAlgorithmConcaveHull.svg",
        "mAlgorithmLineDensity.svg",
        "mAlgorithmLineIntersections.svg",
        "mAlgorithmLineToPolygon.svg",
        "mAlgorithmMeanCoordinates.svg",
        "mAlgorithmMergeLayers.svg",
        "mAlgorithmMultiToSingle.svg",
        "mAlgorithmNearestNeighbour.svg",
        "mAlgorithmNormalRaster.svg",
        "mAlgorithmNetworkAnalysis.svg",
    )

    def __init__(self, parent: QWidget = None):
        """QWidget to set user informations.

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log

        self.log(QgsApplication.defaultThemePath())

        self.grid_layout = QGridLayout(self)

        self.show_qt_standard_icons()

        # icons = sorted([attr for attr in dir(QStyle) if attr.startswith("SP_")])

        # for n, name in enumerate(icons):
        #     btn = QPushButton(name)

        #     pixmapi = getattr(QStyle, name)
        #     icon = self.style().standardIcon(pixmapi)
        #     btn.setIcon(icon)
        #     self.grid_layout.addWidget(btn, n // 4, n % 4)

    def show_qt_standard_icons(self):
        self.grp_standard_icons = QgsCollapsibleGroupBox(self)

        icons = sorted([attr for attr in dir(QStyle) if attr.startswith("SP_")])

        # for attr in dir(QStyle):
        #     if not attr.startswith("SP"):
        #         continue

        #     le = QLineEdit(attr, self)
        #     le.setReadOnly(True)
        #     icon = self.style().standardIcon(getattr(QStyle, attr))
        #     self._layout.addRow(le, self.getLabelWithIcon(icon))

        # for n, name in enumerate(icons):
        #     pixmapi = getattr(QStyle, name)
        #     icon = self.style().standardIcon(pixmapi)
        #     lbl = QLabel(name)
        #     lbl.setPixmap(QgsPixmapLabel(pixmapi))
        #     self.grid_layout.addWidget(lbl, n // 4, n % 4)
