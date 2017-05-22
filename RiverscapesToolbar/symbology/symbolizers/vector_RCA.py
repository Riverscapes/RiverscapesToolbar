from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2

class VectorSymbolizer():

    symbology = "RCA"

    def symbolize(self):

        # define a lookup: value -> (color, label)
        conditions = {
            'Confined - Unimpacted': ('#004DA8', 0.25, 'Confined - Unimpacted'),
            'Confined - Impacted': ('#A80000', 0.25, 'Confined - Impacted'),
            'Intact': ('#00E6A9', 0.5, 'Intact'),
            'Good': ('#AAFF00', 0.5, 'Good'),
            'Moderate': ('#FFFF73', 0.5, 'Moderate'),
            'Poor': ('#FFAA00', 0.5, 'Poor'),
            'Very Poor': ('#FF0000', 0.5, 'Very Poor')
        }

        # create a category for each item in animals
        categories = []
        for condition, (color, size, label) in conditions.items():
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            symbol.setWidth(size)
            category = QgsRendererCategoryV2(condition, symbol, label)
            categories.append(category)

        # create the renderer and assign it to a layer
        expression = 'CONDITION'  # field name
        self.renderer = QgsCategorizedSymbolRendererV2(expression, categories)