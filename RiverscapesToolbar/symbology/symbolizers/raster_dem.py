from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "DEM"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.INTERPOLATED
        # Now you have a self.layer object and self.stats you can work with
        self.opacity = 0.6

        colDic = {
            'tan': '#ffebb0',
            'green': '#267300',
            'brown': '#734d00',
            'white': '#ffffff'
        }

        lo = self.stats.minimumValue
        hi = self.stats.maximumValue

        interval = (hi - lo) /3.0

        midlo = lo + interval
        midhi = hi - interval

        self.colLst = [
            [lo,    QColor(colDic['tan']),   str(lo)],
            [midlo, QColor(colDic['green']), str(midlo)],
            [midhi, QColor(colDic['brown']), str(midhi)],
            [hi,    QColor(colDic['white']), str(hi)]
        ]

