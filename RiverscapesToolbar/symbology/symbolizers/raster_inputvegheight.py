from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "input_vegheight"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.INTERPOLATED
        # Now you have a self.layer object and self.stats you can work with
        self.opacity = 0.8

        colDic = {
            'Low':'#FFED96',
            'High':'#2B9600'
        }

        min = self.stats.minimumValue
        max = self.stats.maximumValue

        self.colLst = [
            [min, QColor(colDic['Low']), str(min)],
            [max, QColor(colDic['High']), str(max)]
        ]