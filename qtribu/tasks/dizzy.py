import random
from datetime import datetime, timedelta
from time import sleep

from qgis.core import QgsTask
from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QTransform


class DizzyTask(QgsTask):
    def __init__(
        self,
        description: str,
        iface: QgisInterface,
        duration: float = 3,
        refresh: float = 0.15,
        max_offset: int = 12,
        max_angle: int = 6,
    ):
        super().__init__(description, QgsTask.CanCancel)
        self.iface = iface
        self.duration = duration
        self.refresh = refresh
        self.max_offset = max_offset
        self.max_angle = max_angle

    def run(self) -> bool:
        stop_time = datetime.now() + timedelta(seconds=self.duration)
        d = self.max_offset
        r = self.max_angle
        canvas = self.iface.mapCanvas()
        while datetime.now() < stop_time:
            if self.isCancelled():
                break
            rect = canvas.sceneRect()
            if rect.x() < -d or rect.x() > d or rect.y() < -d or rect.y() > d:
                # do not affect panning
                pass
            else:
                rect.moveTo(random.randint(-d, d), random.randint(-d, d))
                canvas.setSceneRect(rect)
                matrix = QTransform()
                matrix.rotate(random.randint(-r, r))
                canvas.setTransform(matrix)
                sleep(self.refresh)
        return True

    def finished(self, result: bool) -> None:
        canvas = self.iface.mapCanvas()
        canvas.setSceneRect(canvas.sceneRect())
        canvas.setTransform(QTransform())
