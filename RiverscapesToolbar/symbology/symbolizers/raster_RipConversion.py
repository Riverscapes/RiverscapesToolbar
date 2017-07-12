from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "RiparianConversion"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.DISCRETE

        self.opacity = 0.4

        self.colLst = [
            [0, QColor('#4CE600'), 'No Change'],
            [50, QColor('#00C5FF'), 'Conversion to Grass/Shrubland'],
            [60, QColor('#A87000'), 'Devegetation'],
            [80, QColor('#FF00C5'), 'Conifer Encroachment'],
            [97, QColor('#A900E6'), 'Conversion to Invasive'],
            [98, QColor('#FF0000'), 'Development'],
            [99, QColor('#E6E600'), 'Conversion to Agriculture'],
            ]