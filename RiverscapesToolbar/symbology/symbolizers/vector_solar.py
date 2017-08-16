from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "Solar_Vector"

    def symbolize(self):
        # define ranges: label, lower value, upper value, color name
        cond_cat = (
            ('0-100,000', 0.0, 100000.0, '#3869FF'),
            ('100,000-150,000', 100000.0, 150000.0, '#2FE8FF'),
            ('150,000-200,000', 150000.0, 200000.0, '#27FF8C'),
            ('200,000-250,000', 200000.0, 250000.0, '#44FF1E'),
            ('250,000-300,000', 250000.0, 300000.0, '#D2FF16'),
            ('300,000-350,000', 300000.0, 350000.0, '#FF920D'),
            ('>350,000', 350000.0, 1000000.0, '#FF051A')
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
        expression = 'area_solar'  # field name
        self.renderer = QgsGraduatedSymbolRendererV2(expression, ranges)