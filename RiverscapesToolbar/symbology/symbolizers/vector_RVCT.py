from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRendererCategoryV2, QgsCategorizedSymbolRendererV2

class VectorSymbolizer():

    symbology = "RVCT"

    def symbolize(self):

        # define a lookup: value -> (color, label)
        conditions = {
            'Minor Conifer Encroachment': ('#FFBEE8', 'Minor Conifer Encroachment'),
            'Moderate Conifer Encroachment': ('#FF00C5', 'Moderate Conifer Encroachment'),
            'Significant Conifer Encroachment': ('#A80084', 'Significant Conifer Encroachment'),
            'Minor Conversion to Agriculture': ('#FFFFBE', 'Minor Conversion to Agriculture'),
            'Moderate Conversion to Agriculture': ('#E6E600', 'Moderate Conversion to Agriculture'),
            'Significant Conversion to Agriculture': ('#A8A800', 'Significant Conversion to Agriculture'),
            'Minor Conversion to Grass/Shrubland': ('#BEE8FF', 'Minor Conversion to Grass/Shrubland'),
            'Moderate Conversion to Grass/Shrubland': ('#00C5FF', 'Moderate Conversion to Grass/Shrubland'),
            'Significant Conversion to Grass/Shrubland': ('#0084A8', 'Significant Conversion to Grass/Shrubland'),
            'Minor Conversion to Invasive': ('#DF73FF', 'Minor Conversion to Invasive'),
            'Moderate Conversion to Invasive': ('#A900E6', 'Moderate Conversion to Invasive'),
            'Significant Conversion to Invasive': ('#8400A8', 'Significant Conversion to Invasive'),
            'Minor Devegetation': ('#CDAA66', 'Minor Devegetation'),
            'Moderate Devegetation': ('#A87000', 'Moderate Devegetation'),
            'Significant Devegetation': ('#734C00', 'Significant Devegetation'),
            'Minor Development': ('#FF7F7F', 'Minor Development'),
            'Moderate Development': ('#FF0000', 'Moderate Development'),
            'Significant Development': ('#A80000', 'Significant Development'),
            'Multiple Dominant Conversion Types': ('#4E4E4E', 'Multiple Dominant Conversion Types'),
            'No Change': ('#4CE600', 'No Change')
        }

        # create a category for each item in animals
        categories = []
        for condition, (color, label) in conditions.items():
            symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
            symbol.setColor(QColor(color))
            symbol.setWidth(0.5)
            category = QgsRendererCategoryV2(condition, symbol, label)
            categories.append(category)

        # create the renderer and assign it to a layer
        expression = 'conv_type'  # field name
        self.renderer = QgsCategorizedSymbolRendererV2(expression, categories)