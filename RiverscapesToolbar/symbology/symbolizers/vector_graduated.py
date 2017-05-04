from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "DEMO_graduated"

    def set(self):
        # define ranges: label, lower value, upper value, color name
        coffee_prices = (
            ('Free', 0.0, 0.0, 'green'),
            ('Cheap', 0.0, 1.5, 'yellow'),
            ('Average', 1.5, 2.5, 'orange'),
            ('Expensive', 2.5, 999.0, 'red'),
        )

        # create a category for each item in animals
        ranges = []
        for label, lower, upper, color in coffee_prices:
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            rng = QgsRendererRangeV2(lower, upper, symbol, label)
            ranges.append(rng)

        # create the renderer and assign it to a layer
        expression = 'cost'  # field name
        renderer = QgsGraduatedSymbolRendererV2(expression, ranges)
        self.layer.setRendererV2(renderer)
