from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "Solar_Raster"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.INTERPOLATED
        # Now you have a self.layer object and self.stats you can work with
        self.opacity = 0.6

        colDic = {
            'Low':'#0000FF',
            'Medium':'#FFFF00',
            'High':'#FF0000'
        }

        min = self.stats.minimumValue
        max = self.stats.maximumValue

        # calculate median
        range = max - min
        med = range//2

        self.colLst = [
            [min, QColor(colDic['Low']), str(min)],
            [med, QColor(colDic['Medium']), str(med)],
            [max, QColor(colDic['High']), str(max)]
        ]