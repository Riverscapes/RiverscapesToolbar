from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "StreamTemp"

    def symbolize(self):
        # define ranges: label, lower value, upper value, color name
        cond_cat = (
            ('-9999', -9999, -0.01, '#808080'),
            ('0-1', 0.0, 1.0, '#195ABA'),
            ('1-2', 1.0, 2.0, '#3674B6'),
            ('2-3', 2.0, 3.0, '#548EB1'),
            ('3-4', 3.0, 4.0, '#71A9AD'),
            ('4-5', 4.0, 5.0, '#8EC3A9'),
            ('5-6', 5.0, 6.0, '#ABDDA4'),
            ('6-7', 6.0, 7.0, '#B7DF83'),
            ('7-8', 7.0, 8.0, '#C3E162'),
            ('8-9', 8.0, 9.0, '#CFE341'),
            ('9-10', 9.0, 10.0, '#DBE520'),
            ('10-11', 10.0, 11.0, "#E7E700"),
            ('11-12', 11.0, 12.0, "#ECDC13"),
            ('12-13', 12.0, 13.0, "#F0D126"),
            ('13-14', 13.0, 14.0, "#F5C53A"),
            ('14-15', 14.0, 15.0, "#F9BA4D"),
            ('15-16', 15.0, 16.0, "#FDAE61"),
            ('16-17', 16.0, 17.0, "#F69053"),
            ('17-18', 17.0, 18.0, "#EE7245"),
            ('18-19', 18.0, 19.0, "#E75437"),
            ('19-20', 19.0, 20.0, "#DF3729"),
            ('20-100', 20.0, 100.0, "#D7191C")
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
        expression = 'Tmn_14_129'  # field name
        self.renderer = QgsGraduatedSymbolRendererV2(expression, ranges)