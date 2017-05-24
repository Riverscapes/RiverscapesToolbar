from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "Solar_Raster"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.INTERPOLATED
        # Now you have a self.layer object and self.stats you can work with
        self.opacity = 0.4

        colDic = {
            'blue': '#1977EF',
            'red': '#EA4A39'
        }

        lo = self.stats.minimumValue
        hi = self.stats.maximumValue

        self.colLst = [
            [lo, QColor(colDic['blue']), str(lo)],
            [hi, QColor(colDic['red']), str(hi)]
        ]