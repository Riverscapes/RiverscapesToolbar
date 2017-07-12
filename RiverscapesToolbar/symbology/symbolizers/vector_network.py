from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleMarkerSymbolLayerV2

class VectorSymbolizer():

    symbology = "Network"

    def symbolize(self):

        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        symbol.setWidth(0.25)
        symbol.setColor(QColor('0044FF'))
        self.renderer = QgsSingleSymbolRendererV2(symbol)
