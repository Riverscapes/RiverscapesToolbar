from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleLineSymbolLayerV2

class VectorSymbolizer():

    symbology = "input_streamnetwork"

    def symbolize(self):

        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        symbol.setWidth(0.30)
        symbol.setColor(QColor('#0044FF'))
        self.renderer = QgsSingleSymbolRendererV2(symbol)
