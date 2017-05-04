from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class RasterSymbolizer():

    symbology = "SlopeDeg"

    def setramp(self):
        self.colorramptype = QgsColorRampShader.DISCRETE
        # Now you have a self.layer object you can work with
        # self.opacity = 1.0

        min = self.stats.minimumValue

        self.colLst = [
            # [VALUE, COLOR, LABEL]
            [ min, QColor(255,235,176), "{0} to 2".format(min)],
            [ 2.0, QColor(255,219,135), "2 to 5" ],
            [ 5.0, QColor(255,202,97), "5 to 10" ],
            [ 10.0, QColor(255,186,59), "10 to 15" ],
            [ 15.0, QColor(255,170,0), "15 to 25" ],
            [ 25.0, QColor(255,128,0), "25 to 35" ],
            [ 35.0, QColor(255,85,0), "45 to 45" ],
            [ 45.0, QColor(255,42,0), "45 to 60" ],
            [ 60.0, QColor(161,120,120), "60 to 80" ],
            [ 80.0, QColor(130,10,130), "80 to 90" ]
        ]