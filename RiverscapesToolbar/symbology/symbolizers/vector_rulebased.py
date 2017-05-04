from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsRuleBasedRendererV2, QgsSimpleMarkerSymbolLayerV2

class VectorSymbolizer():

    symbology = "DEMO_rulebased"

    def set(self):

        # define some rules: label, expression, color name, (min scale, max scale)
        road_rules = (
            ('Major road', '"type" LIKE \'major\'', 'orange', None),
            ('Minor road', '"type" LIKE \'minor\'', 'black', (0.0, 2500.0,)),
            ('Residential road', '"type" LIKE \'residential\'', 'grey', (100.0, 1000.0,)),
        )

        # create a new rule-based renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        self.renderer = QgsRuleBasedRendererV2(symbol)

        # get the "root" rule
        root_rule = self.renderer.rootRule()

        for label, expression, color_name, scale in road_rules:
            # create a clone (i.e. a copy) of the default rule
            rule = root_rule.children()[0].clone()
            # set the label, expression and color
            rule.setLabel(label)
            rule.setFilterExpression(expression)
            rule.symbol().setColor(QColor(color_name))
            # set the scale limits if they have been specified
            if scale is not None:
                rule.setScaleMinDenom(scale[0])
                rule.setScaleMaxDenom(scale[1])
            # append the rule to the list of rules
            root_rule.appendChild(rule)

        # delete the default rule
        root_rule.removeChildAt(0)