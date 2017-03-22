from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer
import math

class RasterSymbolizer(QgsRasterLayer):

    def __init__(self, layer):
        self.colDic = {'tan':'#ffebb0', 'green':'#267300', 'brown':'#734d00', 'white':'#ffffff',
                                'red':'#e60000', 'light gray':'#f0f0f0', 'blue':'#004cab'}
        self.shader = QgsRasterShader()
        self.ramp = QgsColorRampShader()
        self.colLst = []
        self.valLst = []
        self.labLst = []
        self.opacity = 1.0

        self.layer = layer
        self.provider = layer.dataProvider()
        extent = layer.extent()
        self.ver = self.provider.hasStatistics(1, QgsRasterBandStats.All)
        self.stats = self.provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)

    def render_GCD(self, type):

        self.setRendererOptions(type)

        self.shader.setRasterShaderFunction(self.ramp)
        renderer = QgsSingleBandPseudoColorRenderer(self.layer.dataProvider(), 1, self.shader)

        self.layer.setRenderer(renderer)
        self.layer.renderer().setOpacity(self.opacity)
        self.layer.triggerRepaint()

    def setRendererOptions(self, type):

        if type == "DEM":
            self.setValueBreaks_DEM()
            self.setColorRamp_DEM()

        elif type == "DoD":
            self.setValueBreaks_DoD()
            self.setColorRamp_DoD()

        elif type == "Slope_deg":
            self.setValueBreaks_SlopeDeg()
            self.setColorRamp_Slope()

        elif type == "Slope_per":
            self.setValueBreaks_SlopePer()
            self.setColorRamp_Slope()

        elif type == "Roughness":
            self.setValueBreaks_Roughness()
            self.setColorRamp_Roughness()

    def setValueBreaks_DEM(self):
        lo = self.stats.minimumValue
        hi = self.stats.maximumValue
        rng = hi - lo
        interval = rng/3.0
        self.valLst = [lo, lo+interval, hi-interval, hi]

    def setValueBreaks_DoD(self):
        nClasses = 20
        lo = self.stats.minimumValue
        hi = self.stats.maximumValue
        mid = 0.0

        if abs(lo) > abs(hi):
            hi = abs(lo)

        else:
            lo = hi*-1.0

        rng = hi*2.0
        interval = rng/(nClasses*1.0)

        nRound = self.magnitude(rng)

        if nRound < 0:
            nRound = abs(nRound) + 2

        else:
            nRound = 2

        self.valLst.append(lo)

        for i in range(1,nClasses+1,1):
            self.valLst.append(lo + i*interval)
            self.labLst.append(str(round(self.valLst[i-1], nRound))+" to "+str(round(self.valLst[i], nRound)))

    def setValueBreaks_SlopeDeg(self):

        self.valLst.append(self.stats.minimumValue)
        self.valLst.append(2.0)
        self.valLst.append(5.0)
        self.valLst.append(10.0)
        self.valLst.append(15.0)
        self.valLst.append(25.0)
        self.valLst.append(35.0)
        self.valLst.append(45.0)
        self.valLst.append(60.0)
        self.valLst.append(80.0)

        self.labLst.append("0 to 2")
        self.labLst.append("2 to 5")
        self.labLst.append("5 to 10")
        self.labLst.append("10 to 15")
        self.labLst.append("15 to 25")
        self.labLst.append("25 to 35")
        self.labLst.append("35 to 45")
        self.labLst.append("45 to 60")
        self.labLst.append("60 to 80")
        self.labLst.append("80 to 90")

    def setValueBreaks_SlopePer(self):
        self.valLst.append(0.0)
        self.valLst.append(3.5)
        self.valLst.append(8.75)
        self.valLst.append(15.0)
        self.valLst.append(25.0)
        self.valLst.append(45.0)
        self.valLst.append(70.0)
        self.valLst.append(100.0)
        self.valLst.append(175.0)
        self.valLst.append(565.0)

        self.labLst.append("0 to 3.5%")
        self.labLst.append("3.5% to 8.75%")
        self.labLst.append("8.75% to 15%")
        self.labLst.append("15% to 25%")
        self.labLst.append("25% to 45%")
        self.labLst.append("45% to 70%")
        self.labLst.append("70% to 100%")
        self.labLst.append("100% to 175%")
        self.labLst.append("175% to 565%")
        self.labLst.append("> 565%")

    def setValueBreaks_Roughness(self):
        self.valLst.append(0)
        self.valLst.append(2)
        self.valLst.append(16)
        self.valLst.append(64)
        self.valLst.append(256)

        self.labLst.append("Fines, Sand (0 to 2 mm)")
        self.labLst.append("Fine Gravel (2 mm to 16 mm)")
        self.labLst.append("Coarse Gravel (16 mm to 64 mm)")
        self.labLst.append("Cobbles (64 mm to 256 mm)")
        self.labLst.append("Boulders (> 256 mm)")

    def setColorRamp_DEM(self):

        self.colLst = [QgsColorRampShader.ColorRampItem(self.valLst[0], QColor(self.colDic['tan']), str(self.valLst[0])),
                           QgsColorRampShader.ColorRampItem(self.valLst[1], QColor(self.colDic['green']), str(self.valLst[1])),
                           QgsColorRampShader.ColorRampItem(self.valLst[2], QColor(self.colDic['brown']), str(self.valLst[2])),
                           QgsColorRampShader.ColorRampItem(self.valLst[3], QColor(self.colDic['white']), str(self.valLst[3]))]

        self.ramp.setColorRampItemList(self.colLst)
        self.ramp.setColorRampType(QgsColorRampShader.INTERPOLATED)
        self.opacity = 0.6

    def setColorRamp_DoD(self):

        self.colLst = [QgsColorRampShader.ColorRampItem(self.valLst[0], QColor(230,0,0), self.labLst[0]),
                       QgsColorRampShader.ColorRampItem(self.valLst[1], QColor(235,45,23), self.labLst[1]),
                       QgsColorRampShader.ColorRampItem(self.valLst[2], QColor(240,67,41), self.labLst[2]),
                       QgsColorRampShader.ColorRampItem(self.valLst[3], QColor(242,88,61), self.labLst[3]),
                       QgsColorRampShader.ColorRampItem(self.valLst[4], QColor(245,108,81), self.labLst[4]),
                       QgsColorRampShader.ColorRampItem(self.valLst[5], QColor(245,131,105), self.labLst[5]),
                       QgsColorRampShader.ColorRampItem(self.valLst[6], QColor(245,151,130), self.labLst[6]),
                       QgsColorRampShader.ColorRampItem(self.valLst[7], QColor(242,171,155), self.labLst[7]),
                       QgsColorRampShader.ColorRampItem(self.valLst[8], QColor(237,190,180), self.labLst[8]),
                       QgsColorRampShader.ColorRampItem(self.valLst[9], QColor(230,208,207), self.labLst[9]),
                       QgsColorRampShader.ColorRampItem(self.valLst[10], QColor(218,218,224), self.labLst[10]),
                       QgsColorRampShader.ColorRampItem(self.valLst[11], QColor(197,201,219), self.labLst[11]),
                       QgsColorRampShader.ColorRampItem(self.valLst[12], QColor(176,183,214), self.labLst[12]),
                       QgsColorRampShader.ColorRampItem(self.valLst[13], QColor(155,166,207), self.labLst[13]),
                       QgsColorRampShader.ColorRampItem(self.valLst[14], QColor(135,150,201), self.labLst[14]),
                       QgsColorRampShader.ColorRampItem(self.valLst[15], QColor(110,131,194), self.labLst[15]),
                       QgsColorRampShader.ColorRampItem(self.valLst[16], QColor(92,118,189), self.labLst[16]),
                       QgsColorRampShader.ColorRampItem(self.valLst[17], QColor(72,105,184), self.labLst[17]),
                       QgsColorRampShader.ColorRampItem(self.valLst[18], QColor(49,91,176), self.labLst[18]),
                       QgsColorRampShader.ColorRampItem(self.valLst[19], QColor(2,7,168), self.labLst[19])]

        self.ramp.setColorRampItemList(self.colLst)
        self.ramp.setColorRampType(QgsColorRampShader.DISCRETE)

    def setColorRamp_Slope(self):
        self.colLst = [QgsColorRampShader.ColorRampItem(self.valLst[0], QColor(255,235,176), self.labLst[0]),
                       QgsColorRampShader.ColorRampItem(self.valLst[1], QColor(255,219,135), self.labLst[1]),
                       QgsColorRampShader.ColorRampItem(self.valLst[2], QColor(255,202,97), self.labLst[2]),
                       QgsColorRampShader.ColorRampItem(self.valLst[3], QColor(255,186,59), self.labLst[3]),
                       QgsColorRampShader.ColorRampItem(self.valLst[4], QColor(255,170,0), self.labLst[4]),
                       QgsColorRampShader.ColorRampItem(self.valLst[5], QColor(255,128,0), self.labLst[5]),
                       QgsColorRampShader.ColorRampItem(self.valLst[6], QColor(255,85,0), self.labLst[6]),
                       QgsColorRampShader.ColorRampItem(self.valLst[7], QColor(255,42,0), self.labLst[7]),
                       QgsColorRampShader.ColorRampItem(self.valLst[8], QColor(161,120,120), self.labLst[8]),
                       QgsColorRampShader.ColorRampItem(self.valLst[9], QColor(130,10,130), self.labLst[9])]

        self.ramp.setColorRampItemList(self.colLst)
        self.ramp.setColorRampType(QgsColorRampShader.DISCRETE)

    def setColorRamp_Roughness(self):
        self.colLst = [QgsColorRampShader.ColorRampItem(self.valLst[0], QColor(194,82,60), self.labLst[0]),
                       QgsColorRampShader.ColorRampItem(self.valLst[1], QColor(240,180,17), self.labLst[1]),
                       QgsColorRampShader.ColorRampItem(self.valLst[2], QColor(123,237,0), self.labLst[2]),
                       QgsColorRampShader.ColorRampItem(self.valLst[3], QColor(27,168,124), self.labLst[3]),
                       QgsColorRampShader.ColorRampItem(self.valLst[4], QColor(11,44,122), self.labLst[4])]

    def magnitude(self, x):
        return int(math.floor(math.log10(x)))
