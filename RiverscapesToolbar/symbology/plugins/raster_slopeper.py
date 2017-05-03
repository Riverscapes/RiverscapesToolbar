from RiverscapesToolbar.symbology.raster import RasterSymbolizerPlugin
from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class Plugin(RasterSymbolizerPlugin):

    NAME="SlopePer"

    def SetSymbology(self):
        self.colorramptype = QgsColorRampShader.DISCRETE
        # Now you have a self.layer object you can work with
        # self.opacity = 1.0

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