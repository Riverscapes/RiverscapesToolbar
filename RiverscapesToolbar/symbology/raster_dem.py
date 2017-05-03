from RiverscapesToolbar.symbology import RasterSymbolizerPlugin
from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class Plugin(RasterSymbolizerPlugin):

    NAME="DEM"

    def SetSymbology(self):
        self.colorramptype = QgsColorRampShader.INTERPOLATED
        # Now you have a self.layer object and self.stats you can work with
        self.opacity = 0.6

        lo = self.stats.minimumValue
        hi = self.stats.maximumValue
        rng = hi - lo
        interval = rng/3.0

        self.valLst = [lo, lo+interval, hi-interval, hi]
        self.colLst = [QgsColorRampShader.ColorRampItem(self.valLst[0], QColor(self.colDic['tan']), str(self.valLst[0])),
                           QgsColorRampShader.ColorRampItem(self.valLst[1], QColor(self.colDic['green']), str(self.valLst[1])),
                           QgsColorRampShader.ColorRampItem(self.valLst[2], QColor(self.colDic['brown']), str(self.valLst[2])),
                           QgsColorRampShader.ColorRampItem(self.valLst[3], QColor(self.colDic['white']), str(self.valLst[3]))]

