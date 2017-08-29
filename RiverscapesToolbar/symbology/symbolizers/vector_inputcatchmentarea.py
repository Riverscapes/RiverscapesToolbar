from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleFillSymbolLayerV2

class VectorSymbolizer():

    symbology = "input_catchmentarea"

    def symbolize(self):
        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        self.renderer = QgsSingleSymbolRendererV2(symbol)

        # create a new simple marker symbol layer, a green circle with a black border
        properties = {'color':'0,0,0,0','outline_color':'#72A6F9', 'outline_width':'0.36', 'joinstyle':'round'}
        symbol_layer = QgsSimpleFillSymbolLayerV2.create(properties)

        # assign the symbol layer to the symbol
        self.renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)