from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleMarkerSymbolLayerV2

class VectorPlugin():

    def __init__(self, layer):
        self.renderer = None
        self.layer = layer
        self.provider = layer.dataProvider()
        extent = layer.extent()

    def apply(self):
        """
        This applies the ramps and shaders you've already defined.
        :return: 
        """
        self.symbolize()

        # assign the renderer to the layer
        self.layer.setRendererV2(self.renderer)

        # Finally trigger the repaint with the new style
        self.layer.triggerRepaint()

    def symbolize(self):
        """ YOU NEED TO IMPLEMENT THIS AS A SENSIBLE DEFAULT"""

        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        renderer = QgsSingleSymbolRendererV2(symbol)

        # create a new simple marker symbol layer, a green circle with a black border
        properties = {'color': 'green', 'color_border': 'black'}
        symbol_layer = QgsSimpleMarkerSymbolLayerV2.create(properties)

        # assign the symbol layer to the symbol
        renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
