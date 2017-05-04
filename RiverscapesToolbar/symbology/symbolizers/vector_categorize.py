from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2

class VectorSymbolizer():

    symbology = "DEMO_categorize"

    def symbolize(self):

        # define a lookup: value -> (color, label)
        animals = {
            'cat': ('#f00', 'Small cat'),
            'dog': ('#0f0', 'Big dog'),
            'sheep': ('#fff', 'Fluffy sheep'),
            '': ('#000', 'Unknown'),
        }

        # create a category for each item in animals
        categories = []
        for animal_name, (color, label) in animals.items():
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            category = QgsRendererCategoryV2(animal_name, symbol, label)
            categories.append(category)

        # create the renderer and assign it to a layer
        expression = 'animal'  # field name
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        self.layer.setRendererV2(renderer)