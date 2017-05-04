from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer

class VectorPlugin():

    def __init__(self, layer):
        self.shader = QgsRasterShader()
        self.ramp = QgsColorRampShader()

        self.colLst = []
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

        # Map each [val, QColor, label] into a color shader
        colRampMap = list(map(lambda x: QgsColorRampShader.ColorRampItem(*x), self.colLst))

        self.ramp.setColorRampItemList(colRampMap)
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
        self.opacity = 1.0
        lo = self.stats.minimumValue
        hi = self.stats.maximumValue

        self.colLst = [
            [lo, QColor('black'), str(lo)],
            [hi, QColor('white'), str(hi)]
        ]

