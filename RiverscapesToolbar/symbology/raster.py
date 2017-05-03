from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer
import math

class RasterPlugin():

    def __init__(self, layer):
        self.colDic = {'tan': '#ffebb0', 'green': '#267300', 'brown': '#734d00', 'white': '#ffffff',
                       'red': '#e60000', 'light gray': '#f0f0f0', 'blue': '#004cab'}
        self.shader = QgsRasterShader()
        self.ramp = QgsColorRampShader()

        self.colLst = []
        self.valLst = []
        self.labLst = []
        self.opacity = 1.0
        self.colorramptype = QgsColorRampShader.INTERPOLATED

        self.layer = layer
        self.provider = layer.dataProvider()
        extent = layer.extent()
        self.ver = self.provider.hasStatistics(1, QgsRasterBandStats.All)
        self.stats = self.provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)

    def apply(self):
        """
        This applies the ramps and shaders you've already defined.
        :return: 
        """
        self.SetSymbology()

        self.ramp.setColorRampItemList(self.colLst)
        self.ramp.setColorRampType(self.colorramptype)

        self.shader.setRasterShaderFunction(self.ramp)
        renderer = QgsSingleBandPseudoColorRenderer(self.layer.dataProvider(), 1, self.shader)

        self.layer.setRenderer(renderer)
        self.layer.renderer().setOpacity(self.opacity)

        # Finally trigger the repaint with the new style
        self.layer.triggerRepaint()

    def SetSymbology(self):
        """ YOU NEED TO IMPLEMENT THIS AS A SENSIBLE DEFAULT"""
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

    @staticmethod
    def magnitude(x):
        return int(math.floor(math.log10(x)))
