from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleMarkerSymbolLayerV2

class VectorSymbolizer():

    symbology = "VBET"

    def symbolize(self):
        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        renderer = QgsSingleSymbolRendererV2(symbol)

        # create a new simple marker symbol layer, a green circle with a black border
        properties = {'color': 'transparent', 'color_border': '#E64C00', 'width_border': '0.5'}
        symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)

        # assign the symbol layer to the symbol
        renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)