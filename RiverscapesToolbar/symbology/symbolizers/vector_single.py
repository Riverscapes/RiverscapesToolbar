from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleMarkerSymbolLayerV2

class VectorSymbolizer():

    symbology = "DEMO_single"

    def symbolize(self):
        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        renderer = QgsSingleSymbolRendererV2(symbol)

        # create a new simple marker symbol layer, a green circle with a black border
        properties = {'color': 'green', 'color_border': 'black'}
        symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)

        # assign the symbol layer to the symbol
        renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)

