from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "Conductivity"

    def symbolize(self):
        # define ranges: label, lower value, upper value, color name
        cond_cat = (
            ('0-50', 0.0, 50.0, '#D2A8E1'),
            ('50-100', 50.0, 100.0, '#C293D2'),
            ('100-150', 100.0, 150.0, '#B27EC3'),
            ('150-200', 150.0, 200.0, '#A269B5'),
            ('200-250', 200.0, 250.0, '#9254A6'),
            ('250-300', 250.0, 300.0, '#823F97'),
            ('>300', 300.0, 10000, '#722A89')
        )

        # create a category for each item in animals
        ranges = []
        for label, lower, upper, color in cond_cat:
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            symbol.setWidth(0.5)
            rng = QgsRendererRangeV2(lower, upper, symbol, label)
            ranges.append(rng)

        # create the renderer and assign it to a layer
        expression = 'prdCond'  # field name
        self.renderer = QgsGraduatedSymbolRendererV2(expression, ranges)