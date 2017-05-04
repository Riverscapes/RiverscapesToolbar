from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class Plugin():

    NAME="DEM"

    def SetSymbology(self):
        self.colorramptype = QgsColorRampShader.INTERPOLATED
        # Now you have a self.layer object and self.stats you can work with
        self.opacity = 0.6

        lo = self.stats.minimumValue
        hi = self.stats.maximumValue

        interval = (hi - lo) /3.0

        midlo = lo + interval
        midhi = hi - interval

        self.colLst = [
            [lo,    QColor(self.colDic['tan']),   str(lo)],
            [midlo, QColor(self.colDic['green']), str(midlo)],
            [midhi, QColor(self.colDic['brown']), str(midhi)],
            [hi,    QColor(self.colDic['white']), str(hi)]
        ]

