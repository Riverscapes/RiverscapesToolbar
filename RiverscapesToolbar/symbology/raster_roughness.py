from RiverscapesToolbar.symbology import RasterSymbolizerPlugin
from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class Plugin(RasterSymbolizerPlugin):

    NAME="Roughness"

    def SetSymbology(self):
        self.colorramptype = QgsColorRampShader.DISCRETE
        # Now you have a self.layer object you can work with
        # self.opacity = 1.0

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

        self.colLst = [QgsColorRampShader.ColorRampItem(self.valLst[0], QColor(194,82,60), self.labLst[0]),
                       QgsColorRampShader.ColorRampItem(self.valLst[1], QColor(240,180,17), self.labLst[1]),
                       QgsColorRampShader.ColorRampItem(self.valLst[2], QColor(123,237,0), self.labLst[2]),
                       QgsColorRampShader.ColorRampItem(self.valLst[3], QColor(27,168,124), self.labLst[3]),
                       QgsColorRampShader.ColorRampItem(self.valLst[4], QColor(11,44,122), self.labLst[4])]

