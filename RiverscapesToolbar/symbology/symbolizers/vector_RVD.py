from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "RVD_Departure"

    def symbolize(self):
        # define ranges: label, lower value, upper value, color name
        rvd_cat = (
            ('Large: > 66%', 0.0, 0.33, '#F50000'),
            ('Significant: 33% to 66%', 0.33, 0.66, '#FFFF00'),
            ('Minor: 10% to 33%', 0.6, 0.9, '#98E600'),
            ('Negligible: < 10%', 0.9, 100000, '#38A800'),
        )

        # create a category for each item in animals
        ranges = []
        for label, lower, upper, color in rvd_cat:
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            symbol.setWidth(0.5)
            rng = QgsRendererRangeV2(lower, upper, symbol, label)
            ranges.append(rng)

        # create the renderer and assign it to a layer
        expression = 'DEP_RATIO'  # field name
        self.renderer = QgsGraduatedSymbolRendererV2(expression, ranges)