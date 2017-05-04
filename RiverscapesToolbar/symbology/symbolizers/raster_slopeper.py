from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class RasterSymbolizer():

    symbology = "SlopePer"

    def setramp(self):
        self.colorramptype = QgsColorRampShader.DISCRETE
        # Now you have a self.layer object you can work with
        # self.opacity = 1.0

        self.colLst = [
            [0.0,QColor(255,235,176), "0 to 3.5%"],
            [3.5, QColor(255,219,135), "3.5% to 8.75%"],
            [8.75, QColor(255,202,97), "8.75% to 15%"],
            [15.0, QColor(255,186,59), "15% to 25%"],
            [25.0, QColor(255,170,0), "25% to 45%"],
            [45.0, QColor(255,128,0), "45% to 70%"],
            [70.0, QColor(255,85,0), "70% to 100%"],
            [100.0, QColor(255,42,0), "100% to 175%"],
            [175.0, QColor(161,120,120), "175% to 565%"],
            [565.0, QColor(130,10,130), "> 565%"],
        ]
