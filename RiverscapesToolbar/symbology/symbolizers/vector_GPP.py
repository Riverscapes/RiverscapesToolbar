from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "GPP_Prediction"

    def symbolize(self):
        # define ranges: label, lower value, upper value, color name, width
        GPP = (
            ('0-0.5', 0.0, 0.5, '#fee5d9','1' ),
            ('0.5-1.0', 0.5001, 1.0, '#fcbba1', '1.5'),
            ('1.0-1.5', 1.001, 1.5, '#fc9272', '2'),
            ( '1.5-2.0',1.5, 2.0, '#fb6a4a', '2.5'),
            ('2.0-2.5',2.001, 2.5,'#de2d26', '3'),
            ('>2.5',2.5,10000.0,'#a50f15', '3.5')
        )

        # create a category for each item in GPP
        ranges = []
        for label, lower, upper, color, width in GPP:
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            symbol.setWidth(width)

            rng = QgsRendererRangeV2(lower, upper, symbol, label,)
            ranges.append(rng)

        # create the renderer and assign it to a layer
        expression = 'GPP_1'  # field name (this needs to be the same name in the attribute table of the GPP prediction)
        self.renderer = QgsGraduatedSymbolRendererV2(expression, ranges)