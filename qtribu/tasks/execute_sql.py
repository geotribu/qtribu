import os

import processing
from qgis.core import QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal


class SqlTask(QgsTask):
    """SQL execution as QgsTask subclass"""

    terminated = pyqtSignal(str)

    def __init__(self, description, iface, layer, nb_label, model_path, extent=None):
        super().__init__(description, QgsTask.CanCancel)
        tmp_name = processing.getTempFilename() + ".tif"
        self.param = {
            "INPUT": layer.id(),
            "OUTPUT": os.path.join(tmp_name),
            "LABELS": nb_label,
            "MODEL": model_path,
        }
        if extent:
            self.param["EXTENT"] = extent

    def run(self):
        out = processing.run(
            "QDeepLandia:InferenceQDeepLandia", self.param, feedback=self.feedback
        )
        if os.path.exists(out["OUTPUT"]):
            self.terminated.emit(out["OUTPUT"])
        return True

    def cancel(self):
        QgsMessageLog.logMessage(
            'Task "{name}" was canceled'.format(name=self.description()), "QDeeplandia"
        )
        self.terminated.emit(None)
        super().cancel()
