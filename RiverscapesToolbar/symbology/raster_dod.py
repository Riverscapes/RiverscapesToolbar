from RiverscapesToolbar.symbology import RasterSymbolizerPlugin
from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class Plugin(RasterSymbolizerPlugin):

    NAME="DoD"

    def SetSymbology(self):
        self.colorramptype = QgsColorRampShader.DISCRETE

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