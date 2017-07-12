from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "CoverType"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.DISCRETE

        self.opacity = 0.4

        self.colLst = [
            [500, QColor('#0000FF'), 'Open Water'],
            [1, QColor('#FFFF00'), 'Agricultural'],
            [2, QColor('#FF0000'), 'Developed'],
            [3, QColor('#8A2BE2'), 'Invasive'],
            [20, QColor('#FF1493'), 'Conifer'],
            [40, QColor('#8B4513'), 'Sparsely Vegetated'],
            [50, QColor('#00BFFF'), 'Grass and Shrubland'],
            [100, QColor('#32CD32'), 'Riparian-Hardwood']
        ]