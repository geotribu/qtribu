# standard
from functools import partial
from pathlib import Path
from typing import Optional

# PyQGIS
from qgis.core import QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

# plugin
from qtribu.constants import contribution_guides_base_url
from qtribu.toolbelt import PlgLogger, PlgOptionsManager
from qtribu.toolbelt.commons import open_url_in_browser
from qtribu.toolbelt.preferences import PlgSettingsStructure


class EditingPolicyWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """QWidget to set user informations.

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # initialize GUI
        self.initGui()

    def initGui(self) -> None:
        """Initialize GUI elements."""
        # populate license combo box
        self.cbb_license_article.addItems(
            [
                "Creative Commons International BY-NC-SA 4.0",
                "Creative Commons International BY-SA 4.0",
                "Creative Commons International BY 4.0",
                "Beerware (Révision 42)",
                "autre - merci de préciser dans le champ libre en fin de formulaire",
            ]
        )

        # buttons
        self.btn_license_open.setIcon(
            QgsApplication.getThemeIcon("mActionShowAllLayers.svg")
        )
        self.btn_license_open.pressed.connect(
            partial(
                open_url_in_browser,
                f"{contribution_guides_base_url}guides/licensing/#licence-par-defaut",
            )
        )
        self.btn_open_editing_policy.setIcon(
            QgsApplication.getThemeIcon("mIconCodeEditor.svg")
        )
        self.btn_open_editing_policy.clicked.connect(
            partial(
                open_url_in_browser,
                f"{contribution_guides_base_url}requirements/#charte-editoriale",
            )
        )

        # fill fields from saved settings
        self.load_settings()

    def load_settings(self) -> None:
        """Load options from QgsSettings into UI form."""
        settings: PlgSettingsStructure = self.plg_settings.get_plg_settings()
        self.chb_genai_editing_policy.setChecked(settings.editorial_policy_accept)
        self.chb_license_rdp.setChecked(settings.license_global_accept)

        # set license combo box
        index = self.cbb_license_article.findText(settings.license_article_preferred)
        if index != -1:
            self.cbb_license_article.setCurrentIndex(index)

    def save_settings(self) -> None:
        """Save form text into QgsSettings."""
        # get settings
        settings: PlgSettingsStructure = self.plg_settings.get_plg_settings()

        settings.editorial_policy_accept = self.chb_genai_editing_policy.isChecked()
        settings.license_article_preferred = self.cbb_license_article.currentText()
        settings.license_global_accept = self.chb_license_rdp.isChecked()

        # save it
        self.plg_settings.save_from_object(settings)
