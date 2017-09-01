from PyQt4.QtCore import *
from PyQt4.QtGui import QColor
from qgis.core import QgsField, QgsSymbolV2, QgsRendererRangeV2, QgsGraduatedSymbolRendererV2

class VectorSymbolizer():

    symbology = "StreamTemp"

    def symbolize(self):
        # define ranges: label, lower value, upper value, color name
        temp_cat = (
            ('0-10', 0.0, 10.0, '#0024E3'),
            ('10-12', 10.0, 12.0, '#0087CD'),
            ('12-14', 12.0, 14.0, '#16F45A'),
            ('14-16', 14.0, 16.0, '#73FF1A'),
            ('16-18', 16.0, 18.0, '#BDFF0C'),
            ('18-20', 18.0, 20.0, '#FFDD00'),
            ('20-22', 20.0, 22.0, '#FF9000'),
            ('22-24', 22.0, 24.0, '#FF4400'),
            ('24-26', 24.0, 26.0, '#FF1D00'),
            ('26-28', 26.0, 28.0, '#F70000'),
            ('>28', 28.0, 40.0, '#AA0000')
        )

        # create categories
        ranges = []
        for label, lower, upper, color in temp_cat:
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            symbol.setWidth(0.3)
            rng = QgsRendererRangeV2(lower, upper, symbol, label)
            ranges.append(rng)

        # get list of existing fields in stream temperature shapefile
        field_names = [field.name() for field in self.layer.pendingFields()]

        # add temporary virtual field to store mean temperature values
        mn_field = QgsField('mean_temp', QVariant.Double)
        exp = "({0}+{1}+{2}+{3}+{4})/6".format(field_names[29],
                                               field_names[30],
                                               field_names[31],
                                               field_names[32],
                                               field_names[33])
        self.layer.addExpressionField(exp, mn_field)
        self.layer.updateFields()

        # create the renderer and assign it to a layer
        expression = 'mean_temp'
        self.renderer = QgsGraduatedSymbolRendererV2(expression, ranges)