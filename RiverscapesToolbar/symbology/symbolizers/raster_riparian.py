from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "Riparian"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.DISCRETE

        self.opacity = 0.4

        self.colLst = [
            [0, QColor('transparent'), 'Non-Riparian'],
            [1, QColor('#029507'), 'Riparian']
        ]