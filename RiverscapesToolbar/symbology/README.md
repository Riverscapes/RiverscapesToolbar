# Writing new symbolization plugins

``` python
from RiverscapesToolbar.symbology import RasterSymbolizerPlugin
from PyQt4.QtGui import QColor
from qgis.core import QgsRasterBandStats, QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer, QgsRasterLayer

class Plugin(RasterSymbolizerPlugin):

    NAME="SlopeDeg"

    def SetSymbology(self):
        # Now you have a self.layer object you can work with
        # self.opacity = 1.0
        # HERE'S WHERE YOU START SETTING THINGS
        self.opacity: 0-1 opacity of this layer
        self.valLst = []
        self.labLst = []
        self.colLst = []
        self.colorramptype = QgsColorRampShader.DISCRETE # , EXACT, INTERPOLATED

```

### What can I change inside SetSymbology()?

* self.opacity: 0-1 opacity of this layer
* self.valLst: a list with values
* self.labLst: a list with labels corresponding to vallst
* self.colLst: a list of colors
* self.colorramptype:  QgsColorRampShader.DISCRETE, EXACT, INTERPOLATED

If this isn't enough we can add functionality to `RasterSymbolizerPlugin` easily enough.

### What should I not do inside SetSymbology?

* Don't actually DO anything to the `layer` object if you can help it.
* Do NOT trigger a layer repaint. That's the responsibility of the `apply()` method